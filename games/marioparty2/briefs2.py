"""Mario Party 2 briefs: image key -> brief (painted) or typeset text. See briefs.py for the vocabulary."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def fill(B, T, M1B, M1T, g):
    # pictures this game shares with Mario Party 1 (same size, mode and colour grid: tools/m1_match.py)
    for k2, k1 in json.load(open(os.path.join(HERE, "m1_map.json"))).items():
        if k1 in M1T:
            T[k2] = M1T[k1]
        elif k1 in M1B:
            B[k2] = M1B[k1]
    # player faces (dirs 2-7): the head texture of every costume model (files 209-221) and the expression packs
    import numpy as np
    from . import faces2
    tex = json.load(open(os.path.join(HERE, "spec", "textures.json")))
    for d, who in faces2.DIRS.items():
        ref = np.asarray(tex[f"{d}/209/b7"]["grid"], np.float32)
        for k, t in tex.items():
            p = k.split("/")
            if int(p[0]) != d or not 209 <= int(p[1]) <= 221 or t["w"] != t["h"] or len(t["grid"]) != len(ref):
                continue
            if np.abs(np.asarray(t["grid"], np.float32) - ref).mean() < 14:
                B[k] = faces2.face(who)
        # the far-away models (211, 212, 214, 216, 218, 220) have their own head texture: every costume's copy
        # of it is found by its colour grid, starting from the one read off the contact sheet
        low = tex.get(f"{d}/211/b7")
        if low and f"{d}/211/b7" not in B:
            ref = np.asarray(low["grid"], np.float32)
            for k, t in tex.items():
                p = k.split("/")
                if int(p[0]) == d and 209 <= int(p[1]) <= 221 and (t["w"], t["h"]) == (low["w"], low["h"])                         and len(t["grid"]) == len(ref) and np.abs(np.asarray(t["grid"], np.float32) - ref).mean() < 8:
                    B[k] = faces2.low_face(who)
        for (f, n), (eyes, mouth) in faces2.EXPRESSIONS.items():
            if f"{d}/{f}/p{n}" in tex:
                B[f"{d}/{f}/p{n}"] = faces2.face(who, eyes, mouth)
