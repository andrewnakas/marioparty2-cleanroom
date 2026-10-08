"""Match Mario Party 2 images to Mario Party 1 images that have a brief, by their kept facts (size, mode, colour grid).

    python tools/m1_match.py <mp1 textures.json> [max mean abs diff, default 10]

Writes games/marioparty2/m1_map.json {mp2 key: mp1 key}. Both sides are spec facts; no pixels involved.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from games.marioparty2 import briefs  # noqa: E402


def vec(d):
    return np.asarray(d["grid"], np.float32).ravel()


def main(argv):
    m1 = json.load(open(argv[1]))
    lim = float(argv[2]) if len(argv) > 2 else 10.0
    m2 = json.load(open("games/marioparty2/spec/textures.json"))
    want = [k for k in list(briefs.M1B) + list(briefs.M1T) if k in m1]
    by = {}
    for k in want:
        d = m1[k]
        by.setdefault((d["w"], d["h"], d["mode"], len(d["grid"])), []).append((k, vec(d)))
    out, dist = {}, []
    for k, d in m2.items():
        if "grid" not in d:
            continue
        c = by.get((d["w"], d["h"], d["mode"], len(d["grid"])))
        if not c:
            continue
        v = vec(d)
        best = min(((float(np.abs(v - cv).mean()), ck) for ck, cv in c if len(cv) == len(v)), default=None)
        if best and best[0] <= lim:
            out[k] = best[1]
            dist.append(best[0])
    json.dump(out, open("games/marioparty2/m1_map.json", "w"), indent=0, sort_keys=True)
    used = set(out.values())
    print(f"m1_match: {len(out)} MP2 images matched to {len(used)} of {len(want)} briefed MP1 images "
          f"(limit {lim}, median distance {np.median(dist) if dist else 0:.1f})")
    per = {}
    for k in out:
        per[k.split('/')[0]] = per.get(k.split('/')[0], 0) + 1
    print("per dir:", " ".join(f"{d}:{n}" for d, n in sorted(per.items(), key=lambda x: int(x[0]))))


if __name__ == "__main__":
    main(sys.argv)
