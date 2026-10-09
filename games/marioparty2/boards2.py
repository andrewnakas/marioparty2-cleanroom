"""Board spaces and paths, from kept facts: the board definition files (MainFS dir 10) and each background's
camera (file 0 of the background). Projection as documented by PartyPlanner64 (MP2: eye / 1.2, points *
scaleFactor / 1.2, vertical fov, y flipped).

    spaces(raw) -> [(type, x, y, z)], chains -> [[space index]]
    project(meta_bytes, pts, w, h) -> pixel (x, y)
"""
import math
import struct

import numpy as np

# board name -> (board definition file in dir 10, background index)
BOARDS = {"western": (64, 2), "pirate": (65, 10), "horror": (66, 21), "space": (67, 24), "mystery": (68, 16),
          "bowser": (69, 37), "rules": (80, 43)}
# space type ids (PartyPlanner64 MP2 adapter): 1 blue, 2 red, 4 happening, 5 chance, 6 item, 7 bank, 9 battle,
# 12 Bowser, 14 star; 0/3/8/16/17 are invisible markers (start, Toad, Baby Bowser, path points)
VISIBLE = {1, 2, 4, 5, 6, 7, 9, 12, 14, 15}


def parse(raw):
    n, nchain, so, lo = struct.unpack_from(">HHHH", raw, 0)
    spaces = []
    for i in range(n):
        o = so + 16 * i
        t = raw[o + 3]
        x, z, y = struct.unpack_from(">fff", raw, o + 4)
        spaces.append((t, x, y, z))
    chains = []
    for i in range(nchain):
        co = lo + struct.unpack_from(">H", raw, lo + 2 * i)[0]
        cnt = struct.unpack_from(">H", raw, co)[0]
        chains.append(list(struct.unpack_from(f">{cnt}H", raw, co + 2)))
    return spaces, chains


def meta(raw60):
    f = struct.unpack_from(">4I11f", raw60, 0)
    tw, th, nx, ny, fov, scale, ex, ez, ey, lx, lz, ly = f[:12]
    return dict(w=tw * nx, h=th * ny, fov=fov, scale=scale, eye=(ex, ey, ez), look=(lx, ly, lz))


def project(m, pts):
    """pts: [(x, y, z)] board coordinates -> (N, 2) pixels and (N,) depth (camera distance)."""
    eye = np.asarray(m["eye"], np.float64) / 1.2
    look = np.asarray(m["look"], np.float64)
    z = eye - look
    z /= np.linalg.norm(z)
    x = np.cross([0.0, 1.0, 0.0], z)
    if np.linalg.norm(x) < 1e-6:                # looking straight down: three.js nudges the eye
        x = np.cross([0.0, 1.0, 1e-4], z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    p = np.asarray(pts, np.float64) * (m["scale"] / 1.2) - eye
    xc, yc, zc = p @ x, -(p @ y), p @ z           # camera.scale.y = -1
    f = 1 / math.tan(math.radians(m["fov"]) / 2)
    aspect = m["w"] / m["h"]
    nx, ny = f / aspect * xc / -zc, f * yc / -zc
    return np.stack([nx * m["w"] / 2 + m["w"] / 2, -ny * m["h"] / 2 + m["h"] / 2], 1), -zc


# background -> (board, style): "board" = full painted board, "map" = the small route map
BG_BOARD = {2: ("western", "board"), 10: ("pirate", "board"), 21: ("horror", "board"), 24: ("space", "board"),
            16: ("mystery", "board"), 37: ("bowser", "board"),
            8: ("western", "map"), 15: ("pirate", "map"), 22: ("horror", "map"), 23: ("horror", "map"),
            29: ("space", "map"), 35: ("mystery", "map"), 42: ("bowser", "map")}


def segments(spaces, chains, xy):
    """Path segments in pixels: consecutive spaces of every chain, plus each chain end joined to the nearest
    space of another chain when it is about one step away (junctions)."""
    segs = [(xy[a], xy[b]) for c in chains for a, b in zip(c, c[1:])]
    steps = [np.linalg.norm(a - b) for a, b in segs]
    step = float(np.median(steps)) if steps else 0
    owner = {i: k for k, c in enumerate(chains) for i in c}
    for k, c in enumerate(chains):
        for end in (c[0], c[-1]):
            d = np.linalg.norm(xy - xy[end], axis=1)
            d[[i for i in range(len(xy)) if owner.get(i) == k or i not in owner]] = 1e9
            j = int(np.argmin(d))
            if d[j] < 1.8 * step:
                segs.append((xy[end], xy[j]))
    return segs, step


def draw(img, board_raw, meta_raw, style):
    """img: float RGB (h, w, 3), the smooth picture of the kept grid. Draws the board's paths onto it."""
    from PIL import Image, ImageDraw, ImageFilter
    sp, ch = parse(board_raw)
    m = meta(meta_raw)
    xy, _ = project(m, [s[1:] for s in sp])
    segs, step = segments(sp, ch, xy)
    h, w = img.shape[:2]
    ss = 2
    mask = Image.new("L", (w * ss, h * ss), 0)
    dr = ImageDraw.Draw(mask)
    width = max(2.0, step * (0.42 if style == "board" else 0.2)) * ss
    for a, b in segs:
        dr.line([tuple(a * ss), tuple(b * ss)], fill=255, width=int(width))
    for x, y in xy[[i for c in ch for i in c]]:
        r = width / 2
        dr.ellipse([x * ss - r, y * ss - r, x * ss + r, y * ss + r], fill=255)
    core = np.asarray(mask.resize((w, h), Image.LANCZOS), np.float32) / 255
    edge = np.asarray(mask.filter(ImageFilter.MaxFilter(5)).resize((w, h), Image.LANCZOS), np.float32) / 255
    if style == "board":
        pts = np.clip(np.round(xy).astype(int), 0, [w - 1, h - 1])
        col = np.median(img[pts[:, 1], pts[:, 0]], 0)
        col = col * 0.55 + np.array([236, 220, 180]) * 0.45          # a light path, tinted by the ground it lies on
        dark = col * 0.45
    else:
        col, dark = np.array([250.0, 250, 250]), np.array([40.0, 40, 60])
    img = img * (1 - edge[..., None]) + dark * edge[..., None]
    return img * (1 - core[..., None]) + col * core[..., None]
