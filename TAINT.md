# Taint report

clean ROM sha1 `87f666c76c51358cd7b0924c086f2b9f51f5f3dd` (32 MB) vs the retail USA ROM.
Window 16 B, failing run >= 32 B.

| scan | retail windows indexed | clean streams with coincidences | longest shared run | failing |
|---|---|---|---|---|
| textures | 8945721 | 571 | 31 B | 0 |
| pictures | 22769364 | 157 | 27 B | 0 |
| samples | 23090921 | 43 | 21 B | 0 |
| raw image | 15453742 | 6 | 27 B | 0 |

| region | bytes | differing |
|---|---|---|
| header checksum | 8 | 8 |
| picture decoder (ours, over the HVQ-MPS decoder; its setup call returns) | 15760 | 12609 |
| MainFS | 13783200 | 13593218 |
| backgrounds | 5800720 | 5511470 |
| animated board tiles | 409568 | 405337 |
| audio (samples, codebooks, loop states) | 7187280 | 6503787 |
| tail (free in retail) | 1921120 | 0 |

- bytes differing outside those regions: **0**
- audio bytes differing outside sample data / codebooks / loop states: **0**
- waves whose stored bytes equal retail: **0** of 903
- images whose pixels equal retail (more than 4 byte values): **0**

Kept facts (not scanned): the program (boot, code, overlays: what the matching decomp builds; contains a 1-bit 16x16 font `font0` in its data), text bank, model geometry and motion (1320 FORM files without their bitmaps and palettes, 1731 MTNX motions, 106 other layout/path files), background metadata (tile counts, camera), sequences, envelopes, key maps, loop points, effect tables.

**0 failing.**
