# Taint report

clean ROM sha1 `30e99ff53f31ac7d5f6816bb6aaeeaf79f2e8f0f` (32 MB) vs the retail USA ROM.
Window 16 B, failing run >= 32 B.

| scan | retail windows indexed | clean streams with coincidences | longest shared run | failing |
|---|---|---|---|---|
| textures | 8945721 | 608 | 36 B | 6 |
| pictures | 22769364 | 158 | 38 B | 1 |
| samples | 23090921 | 39 | 20 B | 0 |
| raw image | 15453742 | 7 | 27 B | 0 |

| region | bytes | differing |
|---|---|---|
| header checksum | 8 | 8 |
| picture decoder (ours, over the HVQ-MPS decoder; its setup call returns) | 15760 | 12609 |
| MainFS | 13783200 | 13592703 |
| backgrounds | 5800720 | 5602478 |
| animated board tiles | 409568 | 405337 |
| audio (samples, codebooks, loop states) | 7187280 | 6498325 |
| tail (free in retail) | 1921120 | 0 |

- bytes differing outside those regions: **0**
- audio bytes differing outside sample data / codebooks / loop states: **0**
- waves whose stored bytes equal retail: **0** of 903
- images whose pixels equal retail (more than 4 byte values): **0**

Kept facts (not scanned): the program (boot, code, overlays: what the matching decomp builds; contains a 1-bit 16x16 font `font0` in its data), text bank, model geometry and motion (1320 FORM files without their bitmaps and palettes, 1731 MTNX motions, 106 other layout/path files), background metadata (tile counts, camera), sequences, envelopes, key maps, loop points, effect tables.

**7 failing.**

Failing streams:
- bg/16 at 4083: run 38 B
- 73/11/p0 at 2627: run 36 B
- 73/11/p4 at 3259: run 35 B
- 73/11/p5 at 2627: run 35 B
- 73/11/p6 at 2755: run 34 B
- 73/11/p7 at 2883: run 34 B
- 73/11/p3 at 2755: run 32 B
