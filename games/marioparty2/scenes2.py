"""Words that are part of pre-rendered pictures (title logo, land name signs, GOAL / START! boards).

The default picture is the kept colour grid, smooth; the lettering a sign carried is lost in it. Here the words
(read off the dirty contact sheet) are set again in our own stroke lettering over that smooth picture.

`hook(key, d)` is a generator hook for "bg/<n>": RGBA (ny*th, nx*tw, 4), top row first, or None.
"""
import numpy as np
from PIL import Image

from . import briefs

WHITE = ([255, 255, 255], [236, 236, 240], [10, 10, 20])
GOLD = ([255, 244, 120], [240, 150, 0], [90, 30, 0])

# background -> [(text, box x0 y0 x1 y1 in the picture, (top, bottom, edge), typeset options)]
SIGNS = {
    62: [("MARIO PARTY 2", (0.05, 0.1, 0.97, 0.42), ([255, 230, 70], [240, 60, 20], [30, 20, 120]), {"th": 3.2, "edge_px": 1.5}),
         ("(C) 1999, 2000 Nintendo / HUDSON SOFT", (0.18, 0.795, 0.94, 0.87), WHITE, {"th": 1.1})],
    4: [("WESTERN LAND", (0.2, 0.09, 0.76, 0.3), ([255, 236, 190], [214, 150, 80], [80, 40, 10]), {"th": 3.0})],
    5: [("BANK", (0.44, 0.2, 0.64, 0.36), ([255, 240, 150], [230, 160, 40], [60, 40, 10]), {"th": 2.4})],
    12: [("PIRATE LAND", (0.16, 0.22, 0.86, 0.5), ([255, 220, 120], [220, 110, 30], [70, 30, 10]), {"th": 4.0})],
    18: [("HORROR LAND", (0.04, 0.14, 0.96, 0.36), ([255, 190, 90], [230, 70, 20], [40, 10, 80]), {"th": 3.6})],
    26: [("SPACE LAND", (0.42, 0.18, 0.99, 0.38), ([200, 255, 120], [40, 220, 60], [10, 60, 20]), {"th": 3.0, "slant": 0.15})],
    39: [("BOWSER LAND", (0.16, 0.2, 0.78, 0.46), ([255, 150, 120], [220, 20, 20], [40, 60, 200]), {"th": 3.6})],
    44: [("MINI-GAME STADIUM", (0.02, 0.04, 0.98, 0.2), ([255, 255, 255], [250, 240, 200], [150, 110, 60]), {"th": 2.6})],
    56: [("GOAL", (0.32, 0.24, 0.68, 0.46), ([255, 250, 230], [230, 210, 170], [60, 40, 20]), {"th": 3.2})],
    57: [("GOAL", (0.31, 0.11, 0.56, 0.35), ([255, 255, 255], [255, 220, 220], [200, 20, 20]), {"th": 3.0})],
    58: [("GOAL", (0.3, 0.12, 0.7, 0.34), GOLD, {"th": 3.4})],
    60: [("START!", (0.2, 0.5, 0.8, 0.74), ([255, 200, 90], [240, 60, 120], [255, 255, 255]), {"th": 4.5, "edge_px": 2.0})],
}


def smooth(d):
    """The kept grid of a whole background as one smooth RGB picture (float32)."""
    tw, th, nx, ny, n = d["tw"], d["th"], d["nx"], d["ny"], d["tiles"]
    g = np.frombuffer(bytes.fromhex(d["grid"]), np.uint8).reshape(n, 4, 4, 3)
    mosaic = g.reshape(ny, nx, 4, 4, 3)[::-1].transpose(0, 2, 1, 3, 4).reshape(ny * 4, nx * 4, 3)
    return np.asarray(Image.fromarray(mosaic).resize((nx * tw, ny * th), Image.BICUBIC), np.float32)


def hook(key, d):
    if not key.startswith("bg/") or int(key[3:]) not in SIGNS or d["tiles"] != d["nx"] * d["ny"]:
        return None
    im = smooth(d)
    H, W = im.shape[:2]
    for text, (x0, y0, x1, y1), (top, bottom, edge), opt in SIGNS[int(key[3:])]:
        px, py, w, h = int(x0 * W), int(y0 * H), int((x1 - x0) * W), int((y1 - y0) * H)
        t = briefs.typeset(w, h, text, top, bottom, edge, **opt)
        a = t[..., 3:] / 255
        im[py:py + h, px:px + w] = im[py:py + h, px:px + w] * (1 - a) + t[..., :3] * a
    rgb = (np.clip(im, 0, 255).astype(np.uint8) >> 4) * 17          # 16 levels per channel, like every picture
    return np.dstack([rgb, np.full((H, W), 255, np.uint8)])


if __name__ == "__main__":
    import json
    import os
    import sys
    pic = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec", "pictures.json")))
    ims = [Image.fromarray(hook(f"bg/{b}", pic["bg"][b])).convert("RGB") for b in sorted(SIGNS)]
    sheet = Image.new("RGB", (4 * 322, ((len(ims) + 3) // 4) * 242))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 4) * 322, (i // 4) * 242))
    sheet.save(sys.argv[1])
