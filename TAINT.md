# Taint report

clean ROM sha1 `dcdc77bfc2d9e3137f9b6d9f8c95699312d400b1` (32 MB) vs the retail USA ROM.
Window 16 B, failing run >= 32 B.

| scan | retail windows indexed | clean streams with coincidences | longest shared run | failing |
|---|---|---|---|---|
| textures | 8945721 | 593 | 46 B | 12 |
| pictures | 22769364 | 157 | 38 B | 2 |
| samples | 23090921 | 44 | 21 B | 0 |
| raw image | 15453742 | 8 | 45 B | 2 |

| region | bytes | differing |
|---|---|---|
| header checksum | 8 | 8 |
| picture decoder (ours, over the HVQ-MPS decoder; its setup call returns) | 15760 | 12609 |
| MainFS | 13783200 | 13597483 |
| backgrounds | 5800720 | 5511201 |
| animated board tiles | 409568 | 405337 |
| audio (samples, codebooks, loop states) | 7187280 | 6520978 |
| tail (free in retail) | 1921120 | 0 |

- bytes differing outside those regions: **0**
- audio bytes differing outside sample data / codebooks / loop states: **0**
- waves whose stored bytes equal retail: **0** of 903
- images whose pixels equal retail (more than 4 byte values): **0**

Kept facts (not scanned): the program (boot, code, overlays: what the matching decomp builds; contains a 1-bit 16x16 font `font0` in its data), text bank, model geometry and motion (1320 FORM files without their bitmaps and palettes, 1731 MTNX motions, 106 other layout/path files), background metadata (tile counts, camera), sequences, envelopes, key maps, loop points, effect tables.

**16 failing.**

Failing streams:
- 15/9/p2 at 9: run 46 B
- 15/9/p1 at 997: run 45 B
- rom@0x41dd30 at 90973: run 45 B
- 15/7/p2 at 0: run 42 B
- rom@0x61dd30 at 45542: run 39 B
- 15/8/p1 at 475: run 38 B
- 15/8/p2 at 15: run 38 B
- 35/20/p0 at 837: run 38 B
- 35/20/p1 at 965: run 38 B
- 35/20/p2 at 1035: run 38 B
- bg/21 at 22: run 38 B
- 35/19/p2 at 11: run 37 B
- 15/7/p1 at 182: run 36 B
- bg/19 at 2802: run 34 B
- 15/7/p0 at 1257: run 33 B
- 35/19/p1 at 219: run 33 B
