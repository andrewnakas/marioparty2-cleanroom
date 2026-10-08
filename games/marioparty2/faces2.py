"""Mario Party 2 player faces, painted from descriptions (no retail pixels).

Every player has one face layout (the 64x64 texture of the head model, also used at 32x32) and a set of
expressions. A face is described here in normalised coordinates and drawn with a small supersampled painter;
`face(who, expr)` returns a brief function for briefs.B: f(w, h, spec entry, alpha) -> RGBA.

Expressions: eyes = open | half | closed | sleep | sad | angry | worried | dizzy | cry | x | smug,
mouth = None | small | open | grin.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

SS = 8
K = (14, 10, 12)
W = (252, 252, 252)


class Canvas:
    def __init__(self, w, h, base, box=(0, 0, 1, 1)):
        """base: a colour, or an RGB array (h, w, 3) to paint over. box: the part of the picture the unit
        square of the description maps to."""
        self.w, self.h = w * SS, h * SS
        if isinstance(base, np.ndarray):
            self.im = Image.fromarray(base.astype(np.uint8), "RGB").resize((self.w, self.h), Image.BILINEAR)
        else:
            self.im = Image.new("RGB", (self.w, self.h), tuple(base))
        self.d = ImageDraw.Draw(self.im)
        self.box = box

    def _p(self, x, y):
        x0, y0, x1, y1 = self.box
        return ((x0 + x * (x1 - x0)) * self.w, (y0 + y * (y1 - y0)) * self.h)

    def ell(self, cx, cy, rx, ry, c, rot=0.0):
        if rot and self.box != (0, 0, 1, 1):
            rot = 0.0
        if not rot:
            self.d.ellipse([self._p(cx - rx, cy - ry), self._p(cx + rx, cy + ry)], fill=tuple(c))
            return
        a = math.radians(rot)
        pts = []
        for k in range(48):
            t = 2 * math.pi * k / 48
            x, y = rx * math.cos(t), ry * math.sin(t)
            pts.append(self._p(cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
        self.d.polygon(pts, fill=tuple(c))

    def poly(self, pts, c):
        self.d.polygon([self._p(*p) for p in pts], fill=tuple(c))

    def line(self, pts, wd, c):
        r = wd * self.w * (self.box[2] - self.box[0]) / 2
        q = [self._p(*p) for p in pts]
        self.d.line(q, fill=tuple(c), width=max(1, int(r * 2)), joint="curve")
        for x, y in (q[0], q[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(c))

    def arc(self, cx, cy, rx, ry, a0, a1, wd, c):
        n = 24
        self.line([(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
                    cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)], wd, c)

    def rect(self, x0, y0, x1, y1, c):
        self.d.rectangle([self._p(x0, y0), self._p(x1, y1)], fill=tuple(c))

    def out(self, w, h):
        rgb = np.asarray(self.im.resize((w, h), Image.LANCZOS))
        return np.dstack([rgb, np.full((h, w), 255, np.uint8)])


def eye(cv, cx, cy, rx, ry, side, state, skin, iris=(40, 120, 230), ring=None, lid=None, pupil=K, outline=0.16):
    """One cartoon eye. side: -1 = the eye on the left of the picture, +1 = on the right (irises look inwards)."""
    lid = lid or skin
    if state in ("closed", "sleep", "smugclosed"):
        up = state != "sleep"
        cv.arc(cx, cy + (ry * 0.35 if up else -ry * 0.1), rx * 0.95, ry * 0.6, 200 if up else 20, 340 if up else 160, rx * 0.3, K)
        return
    if state == "x":
        for s in (-1, 1):
            cv.line([(cx - rx * 0.7, cy - s * ry * 0.5), (cx + rx * 0.7, cy + s * ry * 0.5)], rx * 0.28, K)
        return
    cv.ell(cx, cy, rx, ry, K)
    if ring:
        cv.ell(cx, cy, rx * (1 - outline), ry * (1 - outline * 0.7), ring)
        cv.ell(cx, cy, rx * (1 - outline * 2.1), ry * (1 - outline * 1.6), W)
    else:
        cv.ell(cx, cy, rx * (1 - outline), ry * (1 - outline * 0.7), W)
    if state == "dizzy":
        for k, r in enumerate((0.62, 0.3)):
            cv.arc(cx, cy, rx * r, ry * r, 0, 300 + 60 * k, rx * 0.14, K)
        return
    small = 0.7 if state == "worried" else 1.0
    ix, iy = cx - side * rx * 0.22, cy + ry * 0.12
    cv.ell(ix, iy, rx * 0.56 * small, ry * 0.6 * small, iris)
    cv.ell(ix, iy + ry * 0.04, rx * 0.34 * small, ry * 0.4 * small, pupil)
    cv.ell(ix - rx * 0.12, iy - ry * 0.24 * small, rx * 0.14, ry * 0.13, W)
    if state in ("half", "smug"):
        cv.rect(cx - rx * 1.1, cy - ry * 1.1, cx + rx * 1.1, cy - ry * 0.05, lid)
        cv.line([(cx - rx, cy - ry * 0.02), (cx + rx, cy - ry * 0.02)], rx * 0.26, K)
    elif state == "sad":
        cv.poly([(cx + side * rx * 1.3, cy - ry * 1.2), (cx - side * rx * 1.3, cy - ry * 1.2), (cx - side * rx * 1.3, cy - ry * 0.55),
                 (cx + side * rx * 1.3, cy + ry * 0.25)], lid)
        cv.line([(cx - side * rx * 1.0, cy - ry * 0.55), (cx + side * rx * 1.0, cy + ry * 0.2)], rx * 0.24, K)
    elif state == "angry":
        cv.poly([(cx - side * rx * 1.3, cy - ry * 1.2), (cx + side * rx * 1.3, cy - ry * 1.2), (cx + side * rx * 1.3, cy - ry * 0.6),
                 (cx - side * rx * 1.3, cy + ry * 0.05)], lid)
        cv.line([(cx + side * rx * 1.0, cy - ry * 0.6), (cx - side * rx * 1.0, cy + ry * 0.02)], rx * 0.26, K)
    elif state == "cry":
        cv.ell(cx + side * rx * 0.5, cy + ry * 1.05, rx * 0.3, ry * 0.3, (120, 200, 255))


def brow(cv, cx, cy, rx, side, state, wd, c=K):
    """Eyebrow over the eye at (cx, cy): a short arc, tilted by the expression."""
    tilt = {"angry": 0.55, "sad": -0.45, "worried": -0.55, "cry": -0.45, "smug": 0.2}.get(state, 0.0)
    inner, outer = (cx - side * rx * 0.9, cy + tilt * rx * 0.9), (cx + side * rx * 1.0, cy - tilt * rx * 0.5)
    mid = ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - rx * (0.35 if not tilt else 0.1))
    cv.line([inner, mid, outer], wd, c)


def _mouth(cv, cx, cy, s, kind, dark=(120, 20, 30), tongue=(250, 120, 150)):
    if kind == "small":
        cv.ell(cx, cy, s * 0.5, s * 0.3, dark)
        cv.ell(cx, cy + s * 0.1, s * 0.34, s * 0.16, tongue)
    elif kind in ("open", "grin"):
        cv.ell(cx, cy, s, s * 0.55, dark)
        cv.ell(cx, cy + s * 0.25, s * 0.66, s * 0.28, tongue)
        if kind == "grin":
            cv.rect(cx - s * 0.7, cy - s * 0.5, cx + s * 0.7, cy - s * 0.25, W)


# ---------------------------------------------------------------- the six players

SKIN = (250, 186, 138)


def mario(cv, eyes, mouth):
    for s in (-1, 1):
        cx = 0.5 + s * 0.15
        brow(cv, cx, 0.17, 0.12, s, eyes, 0.07)
        eye(cv, cx, 0.42, 0.115, 0.175, s, eyes, SKIN)
    # moustache: a band with a dip under the nose and three scallops per side
    for s in (-1, 1):
        cv.ell(0.5 + s * 0.2, 0.7, 0.26, 0.1, K, rot=s * -12)
        for k, (x, r) in enumerate(((0.1, 0.085), (0.24, 0.09), (0.37, 0.075))):
            cv.ell(0.5 + s * x, 0.775 - k * 0.012, r, r * 0.95, K)
    cv.ell(0.5, 0.615, 0.1, 0.045, SKIN)
    _mouth(cv, 0.5, 0.92, 0.1, mouth)


def luigi(cv, eyes, mouth):
    for s in (-1, 1):
        cx = 0.5 + s * 0.13
        brow(cv, cx, 0.13, 0.13, s, eyes, 0.075)
        eye(cv, cx, 0.44, 0.105, 0.2, s, eyes, SKIN, iris=(60, 150, 235), ring=(120, 230, 240))
    # smooth moustache, hanging lower at its ends
    for s in (-1, 1):
        cv.ell(0.5 + s * 0.22, 0.79, 0.27, 0.085, K, rot=s * 14)
    cv.ell(0.5, 0.71, 0.09, 0.04, SKIN)
    _mouth(cv, 0.5, 0.94, 0.09, mouth)


def peach(cv, eyes, mouth):
    skin = (252, 204, 186)
    for s in (-1, 1):
        cx = 0.5 + s * 0.225
        cv.arc(cx, 0.25, 0.14, 0.08, 200 if s < 0 else 250, 290 if s < 0 else 340, 0.018, (160, 110, 60))
        if eyes in ("closed", "sleep", "x", "dizzy"):
            eye(cv, cx, 0.38, 0.11, 0.12, s, eyes, skin)
            continue
        cv.ell(cx, 0.375, 0.125, 0.125, K)                       # lash line
        cv.ell(cx, 0.395, 0.115, 0.115, W)
        cv.ell(cx - s * 0.015, 0.39, 0.085, 0.1, (30, 70, 190))
        cv.ell(cx - s * 0.015, 0.395, 0.05, 0.062, (10, 20, 70))
        cv.ell(cx - s * 0.04, 0.35, 0.025, 0.028, W)
        for k in range(3):                                         # lashes at the outer corner
            cv.line([(cx + s * 0.1, 0.33 + k * 0.035), (cx + s * (0.17 - k * 0.01), 0.29 + k * 0.045)], 0.014, K)
        if eyes in ("half", "smug"):
            cv.rect(cx - 0.14, 0.24, cx + 0.14, 0.375, skin)
            cv.line([(cx - 0.12, 0.375), (cx + 0.12, 0.375)], 0.03, K)
        elif eyes in ("sad", "cry", "worried"):
            cv.poly([(cx - 0.15, 0.22), (cx + 0.15, 0.22), (cx + s * 0.15, 0.4), (cx - s * 0.15, 0.3)], skin)
            cv.line([(cx - s * 0.12, 0.3), (cx + s * 0.12, 0.4)], 0.028, K)
            if eyes == "cry":
                cv.ell(cx + s * 0.05, 0.56, 0.03, 0.045, (120, 200, 255))
        elif eyes == "angry":
            cv.poly([(cx - 0.15, 0.22), (cx + 0.15, 0.22), (cx + s * 0.15, 0.3), (cx - s * 0.15, 0.4)], skin)
            cv.line([(cx + s * 0.12, 0.3), (cx - s * 0.12, 0.39)], 0.03, K)
    if mouth:
        _mouth(cv, 0.5, 0.9, 0.09, mouth, dark=(170, 30, 70))
    else:
        cv.ell(0.5, 0.895, 0.06, 0.022, (240, 100, 150))
        cv.ell(0.5, 0.915, 0.045, 0.018, (250, 140, 180))


def yoshi(cv, eyes, mouth):
    green, dgreen = (0, 168, 0), (0, 110, 0)
    for s in (-1, 1):                                              # the two eye mounds
        cv.ell(0.5 + s * 0.17, 0.72, 0.31, 0.52, dgreen)
    for s in (-1, 1):
        cv.ell(0.5 + s * 0.17, 0.74, 0.27, 0.48, W)
    cv.rect(0.3, 0.6, 0.7, 1.0, W)
    for s in (-1, 1):
        cx = 0.5 + s * 0.09
        if eyes in ("closed", "sleep", "x", "dizzy"):
            eye(cv, cx, 0.62, 0.07, 0.13, s, eyes, W)
            continue
        cv.ell(cx, 0.62, 0.055, 0.15, K)
        cv.ell(cx, 0.66, 0.03, 0.07, (40, 80, 230))
        cv.ell(cx - 0.01, 0.53, 0.02, 0.035, W)
        if eyes in ("half", "smug"):
            cv.rect(cx - 0.08, 0.44, cx + 0.08, 0.6, W)
            cv.line([(cx - 0.06, 0.6), (cx + 0.06, 0.6)], 0.022, K)
        elif eyes in ("sad", "cry", "worried"):
            cv.line([(cx - s * 0.07, 0.4), (cx + s * 0.07, 0.46)], 0.025, K)
        elif eyes == "angry":
            cv.poly([(cx - 0.09, 0.42), (cx + 0.09, 0.42), (cx + s * 0.09, 0.5), (cx - s * 0.09, 0.6)], W)
            cv.line([(cx + s * 0.07, 0.48), (cx - s * 0.07, 0.58)], 0.03, K)
    del green


def wario(cv, eyes, mouth):
    """Upright description; the texture stores the face turned a quarter (see face())."""
    skin = (250, 190, 150)
    for s in (-1, 1):
        cx = 0.5 + s * 0.26
        # heavy brow wedge and a lilac eyelid
        cv.poly([(cx - s * 0.24, 0.12), (cx + s * 0.22, 0.02), (cx + s * 0.26, 0.2), (cx - s * 0.2, 0.34)], K)
        if eyes in ("closed", "sleep", "x", "dizzy"):
            eye(cv, cx, 0.4, 0.15, 0.13, s, eyes, skin)
            continue
        cv.ell(cx, 0.4, 0.2, 0.17, K)
        cv.ell(cx, 0.42, 0.165, 0.13, (130, 170, 230))
        cv.ell(cx, 0.38, 0.15, 0.1, W)
        cv.ell(cx - s * 0.05, 0.38, 0.05, 0.055, K)
        cv.ell(cx - s * 0.06, 0.365, 0.016, 0.018, W)
        if eyes in ("half", "smug"):
            cv.rect(cx - 0.2, 0.2, cx + 0.2, 0.36, (130, 170, 230))
            cv.line([(cx - 0.18, 0.36), (cx + 0.18, 0.36)], 0.04, K)
        elif eyes in ("sad", "cry", "worried"):
            cv.poly([(cx - 0.22, 0.2), (cx + 0.22, 0.2), (cx + s * 0.22, 0.42), (cx - s * 0.22, 0.3)], skin)
            cv.line([(cx - s * 0.2, 0.3), (cx + s * 0.2, 0.42)], 0.04, K)
    # the grin: a white capsule of teeth across the bottom
    cv.ell(0.5, 0.8, 0.47, 0.15, K)
    cv.ell(0.5, 0.8, 0.44, 0.12, W)
    for k in range(-3, 4):
        cv.line([(0.5 + k * 0.11, 0.7), (0.5 + k * 0.11, 0.9)], 0.012, (170, 170, 180))
    cv.line([(0.08, 0.8), (0.92, 0.8)], 0.012, (170, 170, 180))
    if mouth in ("open", "grin", "small"):
        cv.ell(0.5, 0.82, 0.3, 0.07, (150, 20, 30))


def dk(cv, eyes, mouth):
    fur, dfur, tan = (118, 52, 14), (70, 30, 8), (252, 196, 130)
    cv.rect(0, 0, 1, 1, tan)
    cv.rect(0, 0, 1, 0.32, dfur)
    cv.rect(0, 0, 0.45, 0.48, fur)
    cv.poly([(0.78, 0.55), (1, 0.5), (1, 1), (0.84, 1)], fur)
    for s, cx in ((-1, 0.58), (1, 0.86)):
        if eyes in ("closed", "sleep", "x", "dizzy"):
            eye(cv, cx, 0.13, 0.1, 0.09, s, eyes, tan)
            continue
        cv.ell(cx, 0.13, 0.115, 0.1, K)
        cv.ell(cx, 0.135, 0.095, 0.08, W)
        cv.ell(cx, 0.135, 0.045, 0.05, (110, 50, 10))
        cv.ell(cx, 0.135, 0.022, 0.026, K)
        if eyes in ("half", "smug", "sad", "cry", "worried"):
            cv.rect(cx - 0.12, 0.02, cx + 0.12, 0.12, tan)
            cv.line([(cx - 0.1, 0.12), (cx + 0.1, 0.12)], 0.03, K)
        elif eyes == "angry":
            cv.line([(cx + s * 0.1, 0.02), (cx - s * 0.1, 0.1)], 0.045, K)
    for x in (0.3, 0.42):                                          # nostrils
        cv.ell(x, 0.6, 0.022, 0.035, (150, 90, 50))
    cv.arc(0.36, 0.7, 0.34, 0.14, 20, 160, 0.03, (150, 80, 40))      # the smile line
    if mouth:
        _mouth(cv, 0.36, 0.86, 0.16, mouth)


def wario_low(cv, eyes, mouth):
    """The far-away model's face: upright, hair corner, heavy brows, zigzag moustache over a grin."""
    cv.poly([(0, 0), (0.5, 0), (0.3, 0.14), (0, 0.24)], (110, 60, 10))
    for s, cx in ((-1, 0.25), (1, 0.6)):
        cv.poly([(cx - s * 0.2, 0.2), (cx + s * 0.2, 0.3), (cx + s * 0.18, 0.42), (cx - s * 0.2, 0.36)], K)
        if eyes in ("closed", "sleep", "x", "dizzy"):
            eye(cv, cx, 0.5, 0.12, 0.1, s, eyes, (250, 190, 150))
            continue
        cv.ell(cx, 0.5, 0.15, 0.13, K)
        cv.ell(cx, 0.51, 0.12, 0.1, (130, 170, 230))
        cv.ell(cx, 0.5, 0.1, 0.08, W)
        cv.ell(cx - s * 0.03, 0.5, 0.04, 0.045, K)
    zig = [(0.0, 0.66), (0.1, 0.6), (0.2, 0.68), (0.3, 0.6), (0.43, 0.66), (0.56, 0.6), (0.66, 0.68), (0.76, 0.6), (0.86, 0.66)]
    cv.poly(zig + [(0.86, 0.8), (0.43, 0.76), (0.0, 0.8)], K)
    cv.poly([(0.04, 0.78), (0.82, 0.78), (0.7, 0.95), (0.16, 0.95)], K)
    cv.poly([(0.08, 0.8), (0.78, 0.8), (0.68, 0.92), (0.18, 0.92)], W)
    for k in range(1, 6):
        cv.line([(0.08 + k * 0.117, 0.8), (0.08 + k * 0.117, 0.92)], 0.012, (170, 170, 180))
    cv.ell(0.95, 0.5, 0.07, 0.12, (220, 150, 110))


def dk_low(cv, eyes, mouth):
    """The far-away model's face strip (64x32): fur, a tan mask round the eyes and a tan muzzle."""
    tan = (252, 196, 130)
    cv.ell(0.5, 0.42, 0.26, 0.3, tan)
    cv.ell(0.5, 0.82, 0.36, 0.3, tan)
    for s, cx in ((-1, 0.42), (1, 0.58)):
        if eyes in ("closed", "sleep", "x", "dizzy"):
            eye(cv, cx, 0.42, 0.06, 0.12, s, eyes, tan)
            continue
        cv.ell(cx, 0.42, 0.065, 0.14, K)
        cv.ell(cx, 0.43, 0.05, 0.11, W)
        cv.ell(cx - s * 0.01, 0.44, 0.022, 0.05, K)
    for x in (0.46, 0.54):
        cv.ell(x, 0.7, 0.012, 0.03, (150, 90, 50))
    cv.arc(0.5, 0.78, 0.26, 0.14, 20, 160, 0.02, (150, 80, 40))


# far-away ("low") models: painter, base colour (None = the kept colour grid), the part of the texture the face fills
LOW = {"luigi": (luigi, None, (0.0, 0.0, 0.8, 1.0)), "yoshi": (yoshi, (0, 168, 0), (0, 0, 1, 1)),
       "wario": (wario_low, None, (0, 0, 1, 1)), "dk": (dk_low, (118, 52, 14), (0, 0, 1, 1)),
       "mario": (mario, SKIN, (0, 0, 1, 1)), "peach": (peach, (252, 204, 186), (0, 0, 1, 1))}


def low_face(who):
    fn, base, box = LOW[who]

    def paint(w, h, d, alpha):
        b = base
        if b is None:
            n = int(round(len(d["grid"]) ** 0.5))
            b = np.asarray(d["grid"], np.uint8).reshape(n, n, 4)[..., :3]
        cv = Canvas(w, h, b, box)
        if who == "luigi":                      # skin under the face part
            cv.rect(0, 0, 1.25, 0.72, SKIN)
        fn(cv, "open", None)
        return cv.out(w, h)
    return paint


PLAYERS = {"mario": (mario, SKIN, 0), "luigi": (luigi, SKIN, 0), "peach": (peach, (252, 204, 186), 0),
           "yoshi": (yoshi, (0, 168, 0), 0), "wario": (wario, (250, 190, 150), 1), "dk": (dk, (252, 196, 130), 0)}


def face(who, eyes="open", mouth=None):
    fn, base, quarter = PLAYERS[who]

    def paint(w, h, d, alpha):
        cv = Canvas(w, h, base) if not quarter else Canvas(h, w, base)
        fn(cv, eyes, mouth)
        im = cv.out(w, h) if not quarter else np.rot90(cv.out(h, w), quarter)
        return np.ascontiguousarray(im)
    return paint


# expression files of every player directory: (file, pack image) -> (eyes, mouth)
EXPRESSIONS = {(222, 0): ("closed", None), (223, 0): ("half", None), (223, 1): ("closed", None),
               (224, 0): ("open", "small"), (225, 0): ("sad", None), (226, 0): ("angry", None),
               (227, 0): ("worried", None), (228, 0): ("dizzy", "small"), (229, 0): ("cry", None),
               (230, 0): ("x", None), (231, 0): ("smug", "small"), (232, 0): ("open", "open"),
               (233, 0): ("angry", None), (234, 0): ("angry", None), (235, 0): ("open", "open"),
               (235, 1): ("half", "open"), (235, 2): ("closed", "open")}
DIRS = {2: "mario", 3: "luigi", 4: "yoshi", 5: "wario", 6: "dk", 7: "peach"}


if __name__ == "__main__":
    import sys
    cells = []
    for who in PLAYERS:
        for eyes, mouth in (("open", None), ("half", None), ("closed", None), ("sad", None), ("angry", None),
                            ("worried", None), ("dizzy", "small"), ("cry", None), ("x", None), ("open", "open")):
            cells.append(face(who, eyes, mouth)(64, 64, None, None))
    sheet = np.zeros((6 * 66, 10 * 66, 4), np.uint8)
    for i, c in enumerate(cells):
        sheet[(i // 10) * 66:(i // 10) * 66 + 64, (i % 10) * 66:(i % 10) * 66 + 64] = c
    Image.fromarray(sheet).convert("RGB").resize((10 * 66 * 2, 6 * 66 * 2), Image.NEAREST).save(sys.argv[1])
