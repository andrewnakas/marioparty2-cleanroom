"""Mario Party 2 framed portraits (dir 0, 40x40): the hosts, Bowser's costumes, enemies, and the framed item squares.

Each picture is a white frame on black with a bust drawn from a description (no retail pixels). Who is in which
file was read off the dirty contact sheet. `brief(name)` returns a brief function for briefs.B.
"""
import numpy as np

from cleanroom.gfx import facepaint
from .faces2 import Canvas, K, W

FRAME = 0.06


def _frame(cv, bg=(10, 10, 14)):
    cv.rect(0, 0, 1, 1, W)
    cv.rect(FRAME, FRAME, 1 - FRAME, 1 - FRAME, bg)


def _eyes(cv, y, dx, rx, ry, iris=K, cx=0.5, white=W, look=0.0):
    for s in (-1, 1):
        x = cx + s * dx
        cv.ell(x, y, rx, ry, K)
        cv.ell(x, y, rx * 0.8, ry * 0.85, white)
        cv.ell(x + look * rx, y + ry * 0.15, rx * 0.42, ry * 0.5, iris)


# ---------------------------------------------------------------- busts (unit square inside the frame)

def koopa(cv, shell=(40, 160, 40), head=(250, 214, 60)):
    cv.ell(0.5, 1.02, 0.42, 0.3, shell)
    cv.ell(0.5, 0.98, 0.3, 0.2, W)
    cv.ell(0.5, 0.52, 0.3, 0.36, head)
    cv.ell(0.7, 0.66, 0.2, 0.13, head)                     # beak
    cv.line([(0.6, 0.72), (0.86, 0.7)], 0.02, (150, 100, 0))
    _eyes(cv, 0.42, 0.09, 0.08, 0.14, cx=0.56, look=0.3)


def toad(cv, cap=(250, 250, 250), spot=(226, 30, 30), vest=(30, 70, 220)):
    cv.ell(0.5, 1.0, 0.34, 0.24, vest)
    cv.ell(0.5, 0.66, 0.24, 0.22, (252, 214, 180))
    cv.ell(0.5, 0.36, 0.46, 0.3, cap)
    cv.rect(0.04, 0.36, 0.96, 0.46, cap)
    for x, y, r in ((0.5, 0.22, 0.12), (0.16, 0.38, 0.09), (0.84, 0.38, 0.09)):
        cv.ell(x, y, r, r * 0.9, spot)
    _eyes(cv, 0.66, 0.08, 0.045, 0.08)
    cv.arc(0.5, 0.78, 0.06, 0.04, 20, 160, 0.02, (160, 60, 40))


def bowser(cv, hat=None):
    shell, face, hair = (40, 150, 40), (240, 220, 120), (230, 50, 30)
    cv.ell(0.5, 1.04, 0.46, 0.26, shell)
    for s in (-1, 1):                                      # horns
        cv.poly([(0.5 + s * 0.24, 0.3), (0.5 + s * 0.44, 0.04), (0.5 + s * 0.34, 0.36)], (250, 246, 230))
    cv.ell(0.5, 0.52, 0.34, 0.32, (90, 170, 40))
    cv.ell(0.5, 0.7, 0.3, 0.2, face)                       # muzzle
    cv.poly([(0.32, 0.2), (0.4, 0.04), (0.5, 0.16), (0.6, 0.04), (0.68, 0.2)], hair)
    for s in (-1, 1):
        cv.poly([(0.5 + s * 0.06, 0.36), (0.5 + s * 0.26, 0.3), (0.5 + s * 0.24, 0.38)], hair)   # brows
    _eyes(cv, 0.45, 0.12, 0.07, 0.08, iris=(200, 30, 20))
    cv.ell(0.5, 0.8, 0.16, 0.08, (150, 20, 20))
    for s in (-1, 1):
        cv.poly([(0.5 + s * 0.1, 0.74), (0.5 + s * 0.14, 0.74), (0.5 + s * 0.12, 0.82)], W)  # fangs
    if hat == "cowboy":
        cv.ell(0.5, 0.2, 0.5, 0.08, (120, 70, 30))
        cv.ell(0.5, 0.1, 0.24, 0.12, (140, 84, 36))
    elif hat == "pirate":
        cv.ell(0.5, 0.16, 0.42, 0.14, (20, 30, 90))
        cv.ell(0.5, 0.14, 0.06, 0.05, W)
    elif hat == "pharaoh":
        cv.poly([(0.16, 0.42), (0.26, 0.04), (0.74, 0.04), (0.84, 0.42), (0.66, 0.22), (0.34, 0.22)], (60, 90, 200))
        for y in (0.1, 0.18, 0.26):
            cv.line([(0.24, y + 0.06), (0.76, y + 0.06)], 0.02, (250, 210, 40))


def goomba(cv):
    cv.ell(0.5, 0.55, 0.44, 0.38, (150, 80, 30))
    cv.ell(0.5, 0.86, 0.3, 0.16, (240, 200, 150))
    for s in (-1, 1):
        cv.line([(0.5 + s * 0.06, 0.32), (0.5 + s * 0.26, 0.24)], 0.05, K)
    _eyes(cv, 0.48, 0.12, 0.08, 0.13)
    for s in (-1, 1):
        cv.poly([(0.5 + s * 0.12, 0.76), (0.5 + s * 0.2, 0.76), (0.5 + s * 0.16, 0.66)], W)


def boo(cv, big=False):
    cv.ell(0.5, 0.54, 0.42, 0.42, (248, 248, 252))
    cv.ell(0.2, 0.62, 0.08, 0.06, (248, 248, 252))
    for s in (-1, 1):
        cv.ell(0.5 + s * 0.13, 0.42, 0.05, 0.1, K)
    cv.ell(0.5, 0.7, 0.18 if big else 0.12, 0.11, (180, 20, 60))
    cv.ell(0.5, 0.76, 0.1 if big else 0.06, 0.04, (250, 120, 150))
    for s in (-1, 1):
        cv.poly([(0.5 + s * 0.04, 0.62), (0.5 + s * 0.1, 0.62), (0.5 + s * 0.07, 0.69)], W)


def shyguy(cv, robe=(220, 30, 30), mask=(250, 250, 250)):
    cv.ell(0.5, 0.6, 0.42, 0.44, robe)
    cv.ell(0.5, 0.52, 0.3, 0.34, mask)
    for s in (-1, 1):
        cv.ell(0.5 + s * 0.1, 0.42, 0.05, 0.08, K)
    cv.ell(0.5, 0.68, 0.07, 0.07, K)


def bobomb(cv, body=(226, 30, 30)):
    cv.ell(0.5, 0.58, 0.4, 0.4, body)
    cv.ell(0.36, 0.42, 0.1, 0.08, (255, 160, 160))
    cv.rect(0.44, 0.08, 0.56, 0.2, (90, 90, 100))
    cv.line([(0.5, 0.08), (0.56, 0.0)], 0.03, (200, 180, 140))
    for s in (-1, 1):
        cv.ell(0.5 + s * 0.12, 0.56, 0.05, 0.1, W)
        cv.ell(0.5 + s * 0.12, 0.58, 0.025, 0.06, K)


def stone(cv, col=(60, 100, 220), helmet=False):
    if helmet:
        cv.ell(0.5, 0.42, 0.44, 0.34, (200, 200, 210))
        cv.rect(0.1, 0.5, 0.9, 0.96, (40, 40, 50))
        cv.poly([(0.5, 0.0), (0.6, 0.12), (0.4, 0.12)], (230, 230, 240))
        _eyes(cv, 0.72, 0.16, 0.08, 0.08)
        return
    cv.rect(0.08, 0.1, 0.92, 0.96, col)
    dark = tuple(int(v * 0.55) for v in col)
    for s in (-1, 1):
        cv.line([(0.5 + s * 0.06, 0.34), (0.5 + s * 0.32, 0.26)], 0.05, dark)
    _eyes(cv, 0.46, 0.16, 0.09, 0.1, iris=(220, 30, 30))
    cv.ell(0.5, 0.76, 0.18, 0.06, dark)


def shark(cv):
    cv.poly([(0.06, 0.7), (0.4, 0.3), (0.56, 0.02), (0.66, 0.32), (0.96, 0.5), (0.7, 0.86), (0.2, 0.86)], (60, 110, 200))
    cv.poly([(0.2, 0.8), (0.7, 0.8), (0.86, 0.6)], W)
    cv.ell(0.56, 0.5, 0.05, 0.05, K)
    for k in range(4):
        x = 0.36 + k * 0.1
        cv.poly([(x, 0.8), (x + 0.04, 0.72), (x + 0.08, 0.8)], W)


def eye(cv):
    cv.ell(0.5, 0.5, 0.42, 0.42, (248, 248, 252))
    cv.ell(0.5, 0.52, 0.22, 0.22, (30, 60, 200))
    cv.ell(0.5, 0.52, 0.1, 0.1, K)
    cv.ell(0.44, 0.44, 0.04, 0.04, W)


def kamek(cv):
    cv.ell(0.5, 0.4, 0.4, 0.36, (40, 80, 200))
    cv.ell(0.5, 0.66, 0.3, 0.26, (250, 214, 60))
    for s in (-1, 1):
        cv.ell(0.5 + s * 0.13, 0.56, 0.1, 0.1, K)
        cv.ell(0.5 + s * 0.13, 0.56, 0.08, 0.08, (220, 240, 255))
        cv.ell(0.5 + s * 0.13, 0.58, 0.03, 0.04, K)
    cv.ell(0.5, 0.8, 0.14, 0.06, (240, 170, 40))


def kid(cv, goggles=False):
    cv.ell(0.5, 1.0, 0.4, 0.26, (250, 214, 60))
    cv.ell(0.5, 0.56, 0.36, 0.34, (250, 220, 120))
    cv.poly([(0.38, 0.24), (0.46, 0.04), (0.56, 0.2), (0.64, 0.06), (0.66, 0.26)], (220, 40, 30))
    for s in (-1, 1):
        cv.poly([(0.5 + s * 0.26, 0.3), (0.5 + s * 0.42, 0.12), (0.5 + s * 0.34, 0.36)], W)
    if goggles:
        for s in (-1, 1):
            cv.ell(0.5 + s * 0.13, 0.46, 0.11, 0.11, (180, 180, 190))
            cv.ell(0.5 + s * 0.13, 0.46, 0.08, 0.08, (220, 240, 255))
    _eyes(cv, 0.46, 0.13, 0.06, 0.08)
    cv.ell(0.5, 0.74, 0.12, 0.07, (170, 30, 30))


PAINTERS = {
    92: lambda c: koopa(c, shell=(250, 200, 40)), 93: koopa, 94: toad, 95: bowser, 96: bowser, 97: goomba,
    98: boo, 99: lambda c: koopa(c, shell=(220, 220, 220)), 100: shyguy, 101: bobomb,
    102: lambda c: bowser(c, "cowboy"), 103: lambda c: bowser(c, "pirate"), 104: bowser,
    105: lambda c: shyguy(c, robe=(250, 250, 250), mask=(226, 40, 40)), 106: lambda c: stone(c, helmet=True),
    120: shark, 121: stone, 122: lambda c: shyguy(c, robe=(240, 240, 240), mask=(250, 250, 250)),
    123: lambda c: kid(c, goggles=True), 124: kid, 125: kamek, 126: lambda c: bowser(c, "pharaoh"), 127: bowser,
    128: bowser, 129: eye, 130: lambda c: stone(c, col=(140, 140, 150)), 131: lambda c: boo(c, big=True),
    132: lambda c: toad(c, cap=(250, 250, 250), spot=(40, 170, 120), vest=(240, 130, 30)),
}


def portrait(f):
    fn = PAINTERS[f]

    def paint(w, h, d, alpha):
        cv = Canvas(w, h, (10, 10, 14))
        _frame(cv)
        inner = Canvas(w, h, (10, 10, 14), (FRAME, FRAME, 1 - FRAME, 1 - FRAME))
        inner.im, inner.d = cv.im, cv.d
        fn(inner)
        out = cv.out(w, h)
        if alpha is not None:
            out[..., 3] = np.where(alpha > 64, 255, 0)
        return out
    return paint


def framed_item(item_brief):
    """An item brief (painted with an oval outline) inside the white frame on black."""
    def paint(w, h, d, alpha):
        n = int(w * (1 - 2 * FRAME) * 0.86)
        ys, xs = np.mgrid[0:n, 0:n]
        disc = ((((xs + 0.5) / n - 0.5) / 0.46) ** 2 + (((ys + 0.5) / n - 0.5) / 0.46) ** 2 <= 1) * 255
        if callable(item_brief):
            it = np.asarray(item_brief(n, n, None, disc.astype(np.float32)), np.float32)
            it[..., 3] = np.minimum(it[..., 3], disc)
        else:
            it = facepaint.render(item_brief, n, n, alpha=disc.astype(np.float32), seed=w * 31 + h)
        cv = Canvas(w, h, (10, 10, 14))
        _frame(cv)
        out = cv.out(w, h).astype(np.float32)
        y0 = x0 = (w - n) // 2
        a = it[..., 3:4] / 255
        out[y0:y0 + n, x0:x0 + n, :3] = out[y0:y0 + n, x0:x0 + n, :3] * (1 - a) + it[..., :3] * a
        if alpha is not None:
            out[..., 3] = np.where(alpha > 64, 255, 0)
        return np.clip(out, 0, 255).astype(np.uint8)
    return paint
