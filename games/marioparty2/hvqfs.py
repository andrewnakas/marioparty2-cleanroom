"""Background container ("HVQ fs", 0x1164160), the animated-tile container and our CRQ picture formats.

Container (big endian): u32 count (dirs + 1), u32 offset[count] (last = end); each dir: u32 count (files + 1),
u32 offset[count] relative to the dir. File 0 of a background is its 60-byte metadata (tile size, tile counts,
camera): layout, kept. File 1 is the "HVQ-MPS 1.1" header (picture size + Huffman trees). The other files are the
tiles, rows bottom to top: "HVQS" + HVQ-MPS data, or u32 3, u32 size, LZ over raw pixels.

The clean ROM stores "HVQS" + CRQ pictures instead and swaps the game's HVQ-MPS decoder for ours
(`native/crq_mips.c`, reached through the same entry point), so no HVQ bitstream is ever produced or kept.
"""
import ctypes
import os
import struct

import numpy as np

ROM_OFFSET = 0x1164160
ROM_END = 0x16EC470           # the animation container follows
DECODE_ROM = 0x96D88          # func_80096188: the game's HVQ-MPS decode entry (code, out, stride, work); we put a jump here
SETUP_ROM = 0x97308           # func_80096708: reads the Huffman trees of an "HVQ-MPS 1.1" header; becomes a plain return
CODE_ROM, CODE_RAM = 0x93A80, 0x80092E80      # start of the HVQ-MPS decoder's code (dead once the entry jumps to ours)
ANIM_OFFSET, ANIM_END = 0x16EC470, 0x1750450  # animated board tiles (raw RGBA5551 tiles, LZ type 3)
MAGIC = b"HVQ-MPS 1.1\0"
CODE_ROOM = DECODE_ROM - CODE_ROM

_here = os.path.dirname(os.path.abspath(__file__))
_dll = ctypes.CDLL(os.path.join(_here, "native", "mplz.dll"))


def read(rom, base=ROM_OFFSET):
    """dirs[b] = [file bytes]."""
    u32 = lambda o: struct.unpack_from(">I", rom, o)[0]
    out = []
    for b in range(u32(base) - 1):
        bo = base + u32(base + 4 + 4 * b)
        n = u32(bo)
        offs = [u32(bo + 4 + 4 * k) for k in range(n)]
        out.append([bytes(rom[bo + offs[k]:bo + offs[k + 1]]) for k in range(n - 1)])
    return out


def pack_dir(files):
    out = bytearray(4 + 4 * (len(files) + 1))
    struct.pack_into(">I", out, 0, len(files) + 1)
    for k, f in enumerate(files):
        struct.pack_into(">I", out, 4 + 4 * k, len(out))
        out += f + bytes(-len(f) % 4)
    struct.pack_into(">I", out, 4 + 4 * len(files), len(out))
    return bytes(out)


def rgba5551(rgba):
    """RGBA uint8 (h, w, 4) -> uint16 (h, w), opaque."""
    c = (rgba[..., :3].astype(np.uint16) * 31 + 127) // 255
    return ((c[..., 0] << 11) | (c[..., 1] << 6) | (c[..., 2] << 1) | 1).astype(np.uint16)


def crq(px):
    """uint16 (h, w) pixels -> CRQ1 file."""
    h, w = px.shape
    px = np.ascontiguousarray(px, np.uint16)
    buf = ctypes.create_string_buffer(w * h * 3 + 16)
    n = _dll.crq_enc(px.ctypes.data_as(ctypes.c_void_p), w, h, buf)
    assert n > 0, "picture too large for CRQ1"
    return b"CRQ1" + bytes(12) + struct.pack(">HH", w, h) + bytes(12) + buf.raw[:n]


def crq_smooth(lattice, w, h, k):
    """RGB uint8 lattice ((h >> k) + 1, (w >> k) + 1, 3) -> CRQ2 file (the decoder interpolates)."""
    assert lattice.shape == ((h >> k) + 1, (w >> k) + 1, 3) and w % (1 << k) == 0 and h % (1 << k) == 0
    return b"CRQ2" + bytes(12) + struct.pack(">HHB", w, h, k) + bytes(11) + lattice.astype(np.uint8).tobytes()


def uncrq(data):
    w, h = struct.unpack_from(">HH", data, 16)
    out = np.zeros((h, w), np.uint16)
    _dll.crq_dec(bytes(data) + bytes(8), out.ctypes.data_as(ctypes.c_void_p), w)
    return out


def decoder_blob():
    """Our decoder's machine code, jumps rebased to its place in RAM."""
    code = bytearray(open(os.path.join(_here, "native", "crq_mips.bin"), "rb").read())
    assert len(code) <= CODE_ROOM
    for line in open(os.path.join(_here, "native", "crq_mips.rel")):
        o = int(line, 16)
        ins = struct.unpack_from(">I", code, o)[0]
        target = ((ins & 0x3FFFFFF) << 2) + CODE_RAM
        struct.pack_into(">I", code, o, (ins & 0xFC000000) | ((target >> 2) & 0x3FFFFFF))
    return bytes(code)


def entry_jump():
    """`j CODE_RAM; nop` for the game's decode entry."""
    return struct.pack(">II", 0x08000000 | ((CODE_RAM >> 2) & 0x3FFFFFF), 0)


def blank_header(header):
    """An "HVQ-MPS 1.1" header file with nothing but the magic and the picture size (the setup call is a no-op)."""
    return MAGIC + bytes(4) + bytes(4) + header[0x14:0x18] + bytes(len(header) - 0x18)


def setup_return():
    return struct.pack(">II", 0x03E00008, 0)          # jr $ra; nop


def anim_read(rom, base=ANIM_OFFSET):
    """sets[s][e] = [(tile index, raw RGBA5551 bytes)]."""
    from . import mainfs
    u32 = lambda o: struct.unpack_from(">I", rom, o)[0]
    sets = []
    for s in range(u32(base) - 1):
        so = base + u32(base + 4 + 4 * s)
        entries = []
        for e in range(u32(so)):
            eo = so + u32(so + 4 + 4 * e)
            tiles = []
            for t in range(u32(eo) - 1):
                to = eo + u32(eo + 4 + 4 * t)
                index, kind, size = struct.unpack_from(">III", rom, to)
                assert kind == 3
                tiles.append((index, mainfs.decompress(3, rom, to + 12, size)[0]))
            entries.append(tiles)
        sets.append(entries)
    return sets


def anim_pack(sets):
    from . import mainfs
    out = bytearray(4 + 4 * (len(sets) + 1))
    struct.pack_into(">I", out, 0, len(sets) + 1)
    for s, entries in enumerate(sets):
        struct.pack_into(">I", out, 4 + 4 * s, len(out))
        sb = bytearray(4 + 4 * len(entries))
        struct.pack_into(">I", sb, 0, len(entries))
        for e, tiles in enumerate(entries):
            struct.pack_into(">I", sb, 4 + 4 * e, len(sb))
            eb = bytearray(4 + 4 * (len(tiles) + 1))
            struct.pack_into(">I", eb, 0, len(tiles) + 1)
            for t, (index, raw) in enumerate(tiles):
                struct.pack_into(">I", eb, 4 + 4 * t, len(eb))
                eb += struct.pack(">III", index, 3, len(raw)) + mainfs.compress(3, raw)
                eb += bytes(-len(eb) % 4)
            struct.pack_into(">I", eb, 4 + 4 * len(tiles), len(eb))
            sb += eb
        out += sb + bytes(-len(sb) % 4)
    struct.pack_into(">I", out, 4 + 4 * len(sets), len(out))
    return bytes(out)
