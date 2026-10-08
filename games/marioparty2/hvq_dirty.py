"""DIRTY ROOM: decode HVQ-MPS pictures by running the game's own decoder under Unicorn.

MP2 library (main segment, ROM 0x93A80..0x978E8): init func_80096C10(alpha), setup func_80096708(header file
"HVQ-MPS 1.1": size, Huffman trees), decode func_80096188(data, out, stride, work 0xC00).  Board tiles are
"HVQS" + data (or u32 3, u32 size, LZ type 3 over raw RGBA5551 when a tile was stored without HVQ).

Only used by extract_spec (to take the coarse colour grid) and by dev contact sheets.
"""
import struct

import numpy as np
from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2, UC_MIPS_REG_A3, UC_MIPS_REG_SP, UC_MIPS_REG_RA

BASE = 0x80000000
INIT, SETUP, DECODE = 0x80096C10, 0x80096708, 0x80096188
CODE, HDR, OUT, WORK, STOP, STACK = 0x80400000, 0x80480000, 0x80500000, 0x80600000, 0x80700000, 0x807F0000


class Decoder:
    def __init__(self, rom):
        self.uc = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_BIG_ENDIAN)
        self.uc.mem_map(0, 0x800000)       # kseg0 0x80000000 = physical 0 under Unicorn
        self.uc.mem_write(0x400, bytes(rom[0x1000:0x1000 + 0x100000]))
        self.uc.mem_write(STOP - BASE, b"\0" * 16)
        # Unicorn 2 on Windows crashes natively on this code unless a global code hook is installed (slow but
        # needed once: the decoded tiles are cached by `cache()`)
        self._hook = lambda *a: None
        self.uc.hook_add(UC_HOOK_CODE, self._hook)
        self._call(INIT, 0xFF)
        self.size = None

    def _call(self, addr, *args):
        for reg, v in zip((UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2, UC_MIPS_REG_A3), args):
            self.uc.reg_write(reg, v)
        self.uc.reg_write(UC_MIPS_REG_SP, STACK)
        self.uc.reg_write(UC_MIPS_REG_RA, STOP)
        self.uc.emu_start(addr, STOP)

    def setup(self, header):
        """The "HVQ-MPS 1.1" header file of the pictures that follow."""
        assert header[:11] == b"HVQ-MPS 1.1"
        self.size = struct.unpack_from(">HH", header, 0x14)
        self.uc.mem_write(HDR - BASE, bytes(header))
        self._call(SETUP, HDR)

    def decode(self, data):
        """Picture data (after setup) -> RGBA uint8 (h, w, 4)."""
        w, h = self.size
        self.uc.mem_write(CODE - BASE, bytes(data) + bytes(64))
        self._call(DECODE, CODE, OUT, w, WORK)
        px = np.frombuffer(bytes(self.uc.mem_read(OUT - BASE, w * h * 2)), ">u2").reshape(h, w)
        return px5551(px)


def px5551(px):
    out = np.empty(px.shape + (4,), np.uint8)
    out[..., 0] = ((px >> 11) & 31) * 255 // 31
    out[..., 1] = ((px >> 6) & 31) * 255 // 31
    out[..., 2] = ((px >> 1) & 31) * 255 // 31
    out[..., 3] = 255
    return out


def tile(dec, t, tw, th):
    if t[:4] == b"HVQS":
        return dec.decode(t[4:])
    from . import mainfs
    assert struct.unpack_from(">I", t, 0)[0] in (2, 3, 4)
    raw, _ = mainfs.decompress(3, t, 8, tw * th * 2)
    return px5551(np.frombuffer(raw, ">u2").reshape(th, tw))


CACHE = "D:/n64work/mp2work/work/hvq"


def cache_build(rom):
    """Decode every HVQ still once into the dirty work dir (resumable): bg<b>.npy (tiles, h, w, 4), fs<d>_<f>.npy."""
    import os
    import time
    from . import hvqfs, mainfs
    os.makedirs(CACHE, exist_ok=True)
    dec, t0 = Decoder(rom), time.time()
    for b, files in enumerate(hvqfs.read(rom)):
        path = f"{CACHE}/bg{b}.npy"
        if not os.path.exists(path):
            tw, th = struct.unpack_from(">II", files[0])
            dec.setup(files[1])
            np.save(path + ".tmp.npy", np.stack([tile(dec, t, tw, th) for t in files[2:]]))
            os.replace(path + ".tmp.npy", path)
            print(f"hvq bg {b} ({len(files) - 2} tiles) {time.time() - t0:.0f}s", flush=True)
    for d, files in enumerate(mainfs.read(rom)):
        for f, e in enumerate(files):
            path = f"{CACHE}/fs{d}_{f}.npy"
            if e["raw"][:11] == b"HVQ-MPS 1.1" and not os.path.exists(path):
                dec.setup(e["raw"])
                np.save(path, dec.decode(files[f - 1]["raw"]))
    print("hvq cache: done", flush=True)


def bg(b):
    return np.load(f"{CACHE}/bg{b}.npy")


def fs(d, f):
    return np.load(f"{CACHE}/fs{d}_{f}.npy")


if __name__ == "__main__":
    import sys
    cache_build(open(sys.argv[1], "rb").read())
