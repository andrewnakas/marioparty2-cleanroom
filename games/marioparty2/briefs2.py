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
    # ---- dir 0: HUD fonts and words not shared with Mario Party 1
    digit, count, orange = g["_DIGIT"], g["_COUNT"], g["_ORANGE"]
    for i in range(10):
        T[f"0/47/p{i}"] = ("O" if i == 0 else str(i), *digit, {"th": 0.85, "pad": 1})
        T[f"0/69/p{i}"] = ("O" if i == 0 else str(i), [150, 255, 90], [20, 190, 20], [40, 10, 110], {"th": 0.9})
    T["0/47/p10"] = ("x", *digit, {"th": 0.8, "pad": 2})
    for i, c in enumerate("54321O"):
        T[f"0/48/p{i}"] = (c, *count, {"th": 1.7, "slant": 0.18, "pad": 2})
    for f, th, pad in ((59, 1.3, 1), (60, 2.0, 2)):
        for i, ch in ((1, "!"), (2, "-"), (3, "?"), (4, "-"), (5, "'"), (6, "."), (7, ",")):
            if f"0/{f}/p{i}" in tex:
                T[f"0/{f}/p{i}"] = (ch, *orange, {"th": th, "pad": pad})
    for i, ch in enumerate("abcdefghijklmnopqrstuvwxyz"):
        T[f"0/68/p{i}"] = (ch, *orange, {"th": 1.2})
    T["0/69/p11"] = ('"', [150, 255, 90], [20, 190, 20], [40, 10, 110], {"th": 0.9})
    T["0/69/p12"] = ("m", [150, 255, 90], [20, 190, 20], [40, 10, 110], {"th": 0.9})
    T["0/69/p13"] = ("cm", [150, 255, 90], [20, 190, 20], [40, 10, 110], {"th": 0.8, "pad": 0})
    white = ([255, 255, 255], [236, 236, 240], [24, 24, 40])
    for f, name in ((70, "MARIO"), (71, "LUIGI"), (72, "PEACH"), (73, "YOSHI"), (74, "DK"), (75, "WARIO"), (76, "BOWSER"),
                    (77, "STAR(S)"), (78, "COIN(S)"), (79, "TOAD")):
        T[f"0/{f}/p0"] = (name, *white, {"th": 0.75, "align": "left", "edge_px": 0.0, "pad": 0})
    # ---- dir 9 (mode select, mini-game land): player portraits, turn counts
    port, over, brief = g["_PORTRAIT"], g["over"], g["brief"]
    for i, who in enumerate(("mario", "luigi", "peach", "yoshi", "wario", "dk")):
        for k in ("p0", "p1"):
            if f"9/{148 + i}/{k}" in tex:
                B[f"9/{148 + i}/{k}"] = port[who]
        B[f"9/{65 + i}/p0"] = port[who]
    for f, nums in ((112, ("20", "35", "50")), (127, ("10", "20", "30"))):
        for i, n in enumerate(nums):
            B[f"9/{f}/b{11 + i}"] = over(brief([44, 40, 150]), n, [255, 214, 60], [244, 110, 0], [60, 14, 20], (0.04, 0.12, 0.96, 0.88), th=2.2)
    # ---- dir 10 (boards): words read off the retail contact sheet, set in our own lettering
    red, grn, pnk = ([255, 120, 90], [226, 20, 10], [255, 250, 240]), ([150, 240, 90], [10, 150, 30], [255, 250, 240]), \
        ([255, 170, 210], [240, 70, 150], [255, 250, 240])
    lime, pur, yel = ([200, 255, 110], [80, 200, 20], [255, 250, 240]), ([220, 130, 250], [130, 30, 200], [255, 250, 240]), \
        ([255, 240, 90], [250, 170, 0], [255, 250, 240])
    dark = ([120, 120, 160], [20, 20, 40], [255, 250, 240])
    gold = ([255, 244, 120], [240, 150, 0], [90, 30, 0])
    thin = ([255, 255, 255], [240, 240, 240], [20, 20, 40])
    name = g["_NAME"]
    words = {
        14: ("YOU ARE THE", ([255, 255, 255], [190, 190, 200], [30, 30, 40]), {"th": 1.2}),
        15: ("SUPERSTAR!", gold, {"th": 1.8}),
        18: ("MARIO START", red, {"th": 1.6}), 19: ("LUIGI START", grn, {"th": 1.6}), 20: ("PEACH START", pnk, {"th": 1.6}),
        21: ("YOSHI START", lime, {"th": 1.6}), 22: ("WARIO START", pur, {"th": 1.6}), 23: ("DONKEY START", yel, {"th": 1.6}),
        28: ("BOWSER EVENT", ([80, 220, 160], [0, 110, 120], [10, 20, 60]), {"th": 1.5}),
        167: ("MINI-GAME STADIUM", gold, {"th": 1.4}),
        198: ("Lite Play      Turns", thin, {"th": 0.8, "edge_px": 0.0}),
        199: ("Standard Play      Turns", thin, {"th": 0.8, "edge_px": 0.0}),
        200: ("Full Play      Turns", thin, {"th": 0.8, "edge_px": 0.0}),
        201: ("Turn", thin, {"th": 0.8, "edge_px": 0.0}),
        209: ("1st", pur, {"th": 1.4}), 210: ("2nd", pur, {"th": 1.4}), 211: ("3rd", pur, {"th": 1.4}), 212: ("4th", pur, {"th": 1.4}),
        277: ("Lite Play", thin, {"th": 0.8, "edge_px": 0.0}), 278: ("Standard Play", thin, {"th": 0.8, "edge_px": 0.0}),
        279: ("Full Play", thin, {"th": 0.8, "edge_px": 0.0}),
        306: ("No item", thin, {"th": 0.8, "edge_px": 0.0}),
        307: ("MARIO START", red, {"th": 1.6}), 308: ("LUIGI START", grn, {"th": 1.6}), 309: ("PEACH START", pnk, {"th": 1.6}),
        310: ("YOSHI START", lime, {"th": 1.6}), 311: ("WARIO START", pur, {"th": 1.6}), 312: ("DK START", yel, {"th": 1.6}),
        313: ("BOWSER START", dark, {"th": 1.6}),
        380: ("WESTERN LAND", ([255, 220, 150], [200, 110, 40], [70, 30, 10]), {"th": 1.3}),
        381: ("PIRATE LAND", ([255, 240, 140], [240, 150, 30], [90, 40, 10]), {"th": 1.3}),
        382: ("HORROR LAND", ([255, 160, 80], [220, 40, 20], [60, 10, 80]), {"th": 1.3}),
        383: ("SPACE LAND", ([255, 250, 120], [250, 160, 0], [200, 20, 20]), {"th": 1.3}),
        384: ("MYSTERY LAND", ([240, 250, 250], [130, 200, 190], [60, 60, 80]), {"th": 1.3}),
        385: ("BOWSER LAND", ([255, 240, 90], [250, 120, 0], [150, 10, 10]), {"th": 1.3}),
        386: ("MINI-GAME STADIUM", ([150, 220, 255], [30, 110, 240], [20, 20, 90]), {"th": 1.1}),
        387: ("MINI-GAME COASTER", ([150, 255, 190], [20, 180, 110], [20, 60, 40]), {"th": 1.1}),
        464: ("MARIO", name, {}), 465: ("LUIGI", name, {}), 466: ("PEACH", name, {}), 467: ("YOSHI", name, {}),
        468: ("WARIO", name, {}), 469: ("DK", name, {}),
        544: ("BOWSER PARADE", ([255, 240, 200], [200, 150, 90], [70, 40, 20]), {"th": 1.5}),
    }
    for f, (text, col, opt) in words.items():
        T[f"10/{f}/p0"] = (text, *col, opt)
    # digits
    for i in range(10):
        n = "O" if i == 0 else str(i)
        T[f"10/203/p{i}"] = (n, [255, 255, 255], [230, 230, 240], [30, 30, 50], {"th": 0.7})
        T[f"10/213/p{i}"] = (n, [255, 255, 255], [230, 230, 240], [30, 30, 50], {"th": 1.4, "slant": 0.15})
        T[f"10/222/p{i}"] = (n, [255, 255, 255], [230, 230, 240], [30, 30, 60], {"th": 0.9})
        T[f"10/223/p{i}"] = (n, [255, 90, 60], [220, 10, 10], [50, 10, 20], {"th": 0.9})
        T[f"10/363/p{i}"] = (n, *digit, {"th": 0.9, "pad": 1})
    for i, ch in ((10, "x"), (11, "+"), (12, "-")):
        T[f"10/363/p{i}"] = (ch, *digit, {"th": 0.9, "pad": 1})
    for i, r in enumerate(("1st", "2nd", "3rd", "4th")):
        T[f"10/360/p{i}"] = (r, *(gold, ([170, 220, 255], [40, 110, 240], [20, 20, 90]), ([255, 190, 150], [220, 90, 40], [80, 20, 0]),
                                  ([210, 210, 220], [120, 120, 140], [30, 30, 40]))[i], {"th": 1.2, "slant": 0.1})
    T["10/361/p0"] = ("COM", [255, 255, 255], [220, 220, 230], [20, 20, 40], {"th": 1.0})
    # dice block faces 1..10
    for i in range(10):
        B[f"10/4/p{i}"] = over(brief([250, 250, 255], {"outline": 1, "c": [60, 40, 160]}), "1O" if i == 9 else str(i + 1),
                               [200, 120, 255], [90, 30, 200], [250, 250, 255], (0.14, 0.12, 0.86, 0.88), th=2.4)
    # HUD portraits (three moods each) and the small heads
    for i, who in enumerate(("mario", "luigi", "peach", "yoshi", "wario", "dk")):
        for k in range(3):
            B[f"10/{271 + i}/p{k}"] = port[who]
        B[f"10/{181 + i}/p0"] = port[who]
    # ---- words in the menu, minigame and title directories
    ww = [255, 255, 255]
    mask = (ww, ww, ww)
    big = ([255, 230, 60], [250, 150, 0], [60, 20, 130])
    plate = ([255, 250, 120], [250, 180, 20], [200, 40, 20])
    for key, text, col, opt in (
            ("9/78", "TIMES PLAYED", plate, {"th": 0.9}), ("9/79", "TIMES WON", plate, {"th": 0.9}),
            ("9/82", "MINI-GAME RECORDS", ([200, 255, 120], [90, 200, 30], [20, 60, 120]), {"th": 0.8}),
            ("9/83", "DRIVER'S ED RECORDS", ([255, 250, 120], [250, 200, 20], [20, 60, 160]), {"th": 0.9}),
            ("9/137", "BONUS", ([255, 255, 255], [220, 255, 220], [10, 120, 30]), {"th": 1.5}),
            ("9/138", "NO BONUS", ([255, 255, 255], [220, 255, 220], [10, 120, 30]), {"th": 1.3}),
            ("9/214", "BATTLE MODE", ([255, 250, 120], [250, 190, 20], [200, 60, 10]), {"th": 1.6}),
            ("9/215", "DUEL MODE", ([255, 250, 120], [250, 190, 20], [200, 60, 10]), {"th": 1.6}),
            ("9/216", "3-WIN MATCH", ([255, 255, 200], [250, 220, 60], [20, 70, 200]), {"th": 1.3}),
            ("9/217", "5-WIN MATCH", ([255, 255, 200], [250, 220, 60], [20, 70, 200]), {"th": 1.3}),
            ("9/218", "7-WIN MATCH", ([255, 255, 200], [250, 220, 60], [20, 70, 200]), {"th": 1.3}),
            ("9/219", "4-PLAYER GAME", ([255, 255, 120], [240, 220, 20], [20, 110, 30]), {"th": 0.9}),
            ("9/220", "1 VS 3 GAME", ([255, 240, 160], [250, 200, 60], [200, 20, 20]), {"th": 0.9}),
            ("9/221", "2 VS 2 GAME", ([255, 220, 250], [250, 160, 230], [170, 30, 150]), {"th": 0.9}),
            ("9/222", "BATTLE GAME", ([220, 255, 160], [160, 240, 60], [20, 130, 60]), {"th": 0.9}),
            ("9/250", "PRACTICE", big, {"th": 1.0}), ("9/251", "QUIT    PRACTICE", big, {"th": 1.0}),
            ("11/20", "GAME RULES", ([255, 160, 190], [240, 60, 120], [255, 255, 255]), {"th": 0.8, "edge_px": 0.0}),
            ("11/21", "CONTROLS (1)", ([255, 160, 190], [240, 60, 120], [255, 255, 255]), {"th": 0.8, "edge_px": 0.0}),
            ("11/22", "CONTROLS (2)", ([255, 160, 190], [240, 60, 120], [255, 255, 255]), {"th": 0.8, "edge_px": 0.0}),
            ("11/24", "CONTROLS", ([255, 160, 190], [240, 60, 120], [255, 255, 255]), {"th": 0.8, "edge_px": 0.0}),
            ("11/25", "ITEM EXPLANATION", ([255, 160, 190], [240, 60, 120], [255, 255, 255]), {"th": 0.7, "edge_px": 0.0}),
            ("11/28", "COIN BATTLE", ([255, 160, 190], [240, 60, 120], [255, 255, 255]), {"th": 0.8, "edge_px": 0.0}),
            ("11/34", "PRACTICE", ([255, 255, 255], [255, 220, 230], [220, 40, 90]), {"th": 0.8}),
            ("11/35", "QUIT", ([255, 255, 255], [255, 220, 230], [220, 40, 90]), {"th": 0.9}),
            ("11/216", "PAUSE", big, {"th": 1.2}),
            ("11/217", "FINISH", big, {"th": 2.4}), ("11/218", "FINISH", mask, {"th": 2.4}),
            ("11/219", "TIME UP", big, {"th": 2.4}), ("11/220", "TIME UP", mask, {"th": 2.4}),
            ("11/221", "GOAL", big, {"th": 2.4}), ("11/222", "GOAL", mask, {"th": 2.4}),
            ("11/223", "DRAW", big, {"th": 2.4}), ("11/224", "DRAW", mask, {"th": 2.4}),
            ("11/225", "MISS!", big, {"th": 2.4}), ("11/226", "MISS!", mask, {"th": 2.4}),
            ("13/0", "CLEAR!", big, {"th": 2.4}), ("13/1", "CLEAR!", mask, {"th": 2.4}),
            ("13/2", "GAME OVER", big, {"th": 1.8}), ("13/3", "GAME OVER", mask, {"th": 1.8}),
            ("14/20", "PRESS START", ([255, 120, 60], [220, 20, 10], [250, 240, 200]), {"th": 1.2}),
            ("14/25", "NO CONTROLLER", ([255, 230, 60], [250, 150, 0], [60, 20, 130]), {"th": 1.2}),
            ("14/26", "(C) 1999 Nintendo / HUDSON SOFT", ([255, 255, 255], [240, 240, 240], [0, 0, 0]), {"th": 0.6})):
        if key + "/p0" in tex:
            T[key + "/p0"] = (text, *col, opt)
    for f, r in ((2, "1st"), (3, "2nd"), (4, "3rd"), (5, "4th")):
        for k, t in tex.items():
            if k.startswith(f"12/{f}/") and t["w"] >= 2 * t["h"] - 8 and t["w"] > t["h"]:
                rr = r if k.endswith("b7") else "4th"
                B[k] = over(brief([252, 252, 252], {"outline": 1, "c": [40, 150, 60]}), rr, [255, 170, 60], [230, 40, 20], [255, 255, 255],
                            (0.04, 0.1, 0.96, 0.9), th=1.6)
