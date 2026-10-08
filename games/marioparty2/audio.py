"""Audio containers of Mario Party 2 (USA): one MBF0 music bank and two SBF0 sound-effect banks.

MBF0 (PartyPlanner64 docs): 'MBF0', u32 nseq, header to 0x40, 16-byte sequence entries, then {u32 B1 offset,
u32 B1 size, u32 tbl offset, u32 tbl size}; B1 is a libultra ALBankFile.
SBF0: 'SBF0', u32 neffects, ..., u32 sound count at 0x44, tbl offset/size at 0x54/0x58, 16-byte sounds at 0x74
{u32 env, u32 rate, u32 wavetable, pan, volume, flags} with offsets from that table.

`waves(rom)` lists every wavetable once: where its sample bytes, codebook and loop live in the ROM image.
Sequences, envelopes, key maps, loop points and the effect tables are structure (kept); only sample bytes,
codebooks and loop states are regenerated, in place (same byte counts), so nothing moves.
"""
import ctypes
import os
import struct

import numpy as np

from cleanroom.audio import albank, vadpcm

_dll = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "native", "mpvadpcm.dll"))
BOOK = np.asarray(vadpcm.make_book()["book"], np.int16)      # our own 4-predictor codebook (retail size: 4)
SFX_RATE = 22050                                              # T3 sound not named by any effect: analysis rate

MBF0_OFFSETS = (0x1750450,)
SBF0_OFFSETS = (0x190A090, 0x1CBF410)


def _u32(b, o):
    return struct.unpack_from(">I", b, o)[0]


def _wave(rom, ctl, tbl, off, rate, key, name):
    base, ln, typ = struct.unpack_from(">IIB", rom, ctl + off)
    lp, bk = struct.unpack_from(">II", rom, ctl + off + 12)
    w = {"name": name, "pos": tbl + base, "len": ln, "type": typ, "rate": rate, "key": key, "loop": None, "book": None}
    if lp:
        s, e, c = struct.unpack_from(">III", rom, ctl + lp)
        w["loop"] = {"pos": ctl + lp, "start": s, "end": e, "count": c}
    if typ == albank.ADPCM and bk:
        order, npred = struct.unpack_from(">ii", rom, ctl + bk)
        w["book"] = {"pos": ctl + bk, "order": order, "npred": npred}
    return w


def waves(rom):
    out, seen = [], set()
    for si, m in enumerate(MBF0_OFFSETS):
        assert rom[m:m + 4] == b"MBF0"
        ext = m + 0x40 + _u32(rom, m + 4) * 16
        ctl, tbl = m + _u32(rom, ext), m + _u32(rom, ext + 8)
        bf = albank.parse_bankfile(rom[ctl:ctl + _u32(rom, ext + 4)])
        for bi, bank in enumerate(bf["banks"]):
            insts = [(f"i{k}", i) for k, i in enumerate(bank["insts"])] + [("perc", bank["percussion"])]
            for iname, inst in insts:
                for k, snd in enumerate(inst["sounds"] if inst else ()):
                    off = int(snd["wave"]["_id"].split("@")[1], 16)
                    if (ctl, off) not in seen:
                        seen.add((ctl, off))
                        out.append(_wave(rom, ctl, tbl, off, bank["rate"], snd["keymap"]["key_base"],
                                         f"mbf_{si}/b{bi}/{iname}/{k}"))
    for ti, s in enumerate(SBF0_OFFSETS):
        assert rom[s:s + 4] == b"SBF0"
        ctl, tbl = s + 0x74, s + _u32(rom, s + 0x54)
        for k in range(_u32(rom, s + 0x44)):
            rate, off = _u32(rom, ctl + k * 16 + 4), _u32(rom, ctl + k * 16 + 8)
            if (ctl, off) not in seen:
                seen.add((ctl, off))
                out.append(_wave(rom, ctl, tbl, off, rate or SFX_RATE, 60, f"sbf_{ti}/{k}"))
    return out


def _ptr(a):
    return a.ctypes.data_as(ctypes.c_void_p)


def nsamples(w):
    return w["len"] // 9 * 16 if w["type"] == albank.ADPCM else w["len"] // 2


def decode(rom, w):
    """DIRTY: retail samples of one wave (int16)."""
    data = bytes(rom[w["pos"]:w["pos"] + w["len"]])
    if w["type"] != albank.ADPCM:
        return np.frombuffer(data[:len(data) // 2 * 2], ">i2").astype(np.int16)
    b = w["book"]
    assert b["order"] == 2
    book = np.frombuffer(rom[b["pos"] + 8:b["pos"] + 8 + b["npred"] * 32], ">i2").astype(np.int16)
    out = np.zeros(len(data) // 9 * 16, np.int16)
    _dll.vadpcm_dec(data, len(data) // 9, _ptr(book), _ptr(out))
    return out


def put(image, w, pcm):
    """Write our samples over one wave in place: sample bytes, codebook, loop state."""
    pcm = np.ascontiguousarray(pcm, np.int16)
    assert len(pcm) == nsamples(w)
    size = len(image)
    _put(image, w, pcm)
    assert len(image) == size


def _put(image, w, pcm):
    if w["type"] != albank.ADPCM:
        image[w["pos"]:w["pos"] + len(pcm) * 2] = pcm.astype(">i2").tobytes()
        return
    b, n = w["book"], len(pcm) // 16
    assert b["order"] == 2 and b["npred"] == 4
    out, dec = ctypes.create_string_buffer(n * 9), np.zeros(n * 16, np.int16)
    _dll.vadpcm_enc(_ptr(pcm), n, _ptr(BOOK), 4, out, _ptr(dec))
    image[w["pos"]:w["pos"] + n * 9] = out.raw
    image[w["pos"] + n * 9:w["pos"] + w["len"]] = bytes(w["len"] - n * 9)
    image[b["pos"] + 8:b["pos"] + 8 + 128] = BOOK.astype(">i2").tobytes()      # 4 predictors x 2 x 8 s16
    if w["loop"]:
        start = w["loop"]["start"] // 16 * 16
        state = dec[start - 16:start] if start >= 16 else np.zeros(16, np.int16)
        image[w["loop"]["pos"] + 12:w["loop"]["pos"] + 44] = state.astype(">i2").tobytes()


if __name__ == "__main__":
    import collections
    import sys
    rom = open(sys.argv[1], "rb").read()
    ws = waves(rom)
    for grp in ("mbf_0", "sbf_0", "sbf_1"):
        g = [w for w in ws if w["name"].startswith(grp)]
        nbytes = sum(w["len"] for w in g)
        print(f"{grp}: {len(g)} waves, {nbytes >> 10} KB, types {dict(collections.Counter(w['type'] for w in g))}, "
              f"loops {sum(1 for w in g if w['loop'])}, npred {dict(collections.Counter(w['book']['npred'] for w in g if w['book']))}, "
              f"rates {sorted(collections.Counter(w['rate'] for w in g).items())[:6]}, uniq pos {len({w['pos'] for w in g})}")
    spans = sorted((w["pos"], w["pos"] + w["len"]) for w in ws)
    ov = sum(1 for a, b in zip(spans, spans[1:]) if b[0] < a[1] and a != b)
    print("overlapping sample spans:", ov, "range", hex(spans[0][0]), hex(max(e for _, e in spans)))
