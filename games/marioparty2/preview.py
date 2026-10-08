"""DIRTY ROOM dev tool: retail | clean pairs for one MainFS directory without building a ROM.

    python -m games.marioparty2.preview <out.png> <dir>[/<lo>-<hi>] [--cell 64] [--page N] [--todo]

Label yellow = briefed / typeset, grey = default rendering. --todo shows only the default ones.
Retail images come from the work-dir cache (mainfs.pkl); the sheet goes to the work dir, never the repo.
"""
import json
import os
import pickle
import sys

from PIL import Image, ImageDraw

from . import briefs, generate, images

PKL = "D:/n64work/mp2work/work/mainfs.pkl"


def _fit(rgba, cell):
    im = Image.fromarray(rgba, "RGBA")
    bg = Image.new("RGBA", im.size, (70, 70, 90, 255))
    bg.alpha_composite(im)
    s = min(cell / im.width, cell / im.height)
    return bg.convert("RGB").resize((max(1, int(im.width * s)), max(1, int(im.height * s))),
                                    Image.NEAREST if s >= 1 else Image.BILINEAR)


def main(argv):
    out, sel = argv[1], argv[2]
    cell = int(argv[argv.index("--cell") + 1]) if "--cell" in argv else 64
    page = int(argv[argv.index("--page") + 1]) if "--page" in argv else 0
    d, _, fr = sel.partition("/")
    lo, _, hi = fr.partition("-")
    d, lo = int(d), int(lo) if lo else 0
    hi = int(hi) if hi else (lo if fr else 10 ** 6)
    files = pickle.load(open(PKL, "rb"))[d]
    tex = json.load(open(os.path.join(generate.SPEC, "textures.json")))
    cells = []
    for f in range(lo, min(hi, len(files) - 1) + 1):
        ims = images.find(files[f]["raw"])
        if not ims:
            continue
        new = generate.images_of(d, f, files[f]["raw"], tex, (briefs.paint,))
        for im in ims:
            key = f"{d}/{f}/{im.key}"
            done = key in briefs.B or key in briefs.T
            if "--todo" in argv and done:
                continue
            cells.append((f"{f}/{im.key} {im.w}x{im.h}", im.rgba, new[im.key], done))
    cols = max(1, 1560 // (2 * cell + 8))
    per = cols * max(1, 1500 // (cell + 12))
    total = len(cells)
    cells = cells[page * per:(page + 1) * per]
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (2 * cell + 8), max(1, rows) * (cell + 12)), (24, 24, 28))
    dr = ImageDraw.Draw(sheet)
    for i, (label, a, b, done) in enumerate(cells):
        x, y = (i % cols) * (2 * cell + 8), (i // cols) * (cell + 12)
        dr.text((x + 1, y), label[:(2 * cell) // 6], fill=(255, 255, 0) if done else (170, 170, 170))
        sheet.paste(_fit(a, cell), (x, y + 11))
        sheet.paste(_fit(b, cell), (x + cell + 2, y + 11))
    sheet.save(out)
    print(f"preview: {out} {sheet.size}, {len(cells)} of {total} images of dir {d} (page {page} of {(total + per - 1) // per})")


if __name__ == "__main__":
    main(sys.argv)
