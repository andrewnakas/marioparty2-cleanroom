# Mario Party 2 clean room: status

## State (2026-10-08)
- Pipeline ported from the finished Mario Party 1 clean room (`D:/n64work/marioparty-cleanroom`): clean ROM =
  retail program + every picture and sound regenerated, played in the browser by EmulatorJS (mupen64plus_next).
- Dev builds boot in headless Edge: intro, dialog font readable, audio flowing with all 903 samples regenerated.
- Not yet published: waiting for the full build (pictures) + taint 0.

## Decisions (logged as made)
- ROM `Mario Party 2 (USA).z64` sha1 166eda1c… (copied from `D:/n64work/marioparty2/private/`, another session's
  local work dir; that dir is left untouched). Work dir for this session: `D:/n64work/mp2work/` (rom, work, build,
  devsite, site, sheets, shots, dirty, practice). Nothing is built on C:.
- **Web route = 3: clean ROM + WASM N64 emulator** (EmulatorJS 4.2.3 + mupen64plus_next, `ports/ejs`). Why: no PC
  port; the decomp (mariopartyrd/marioparty2) is splat-based, 88% of the ROM is still binary blobs and it extracts
  no assets, so there is nothing to compile for the web. Same route and tools as Mario Party 1.
- **Kept as facts**: program, text bank, model geometry and motion (FORM without bitmaps/palettes, MTNX), layout /
  path tables, background metadata, sequences, envelopes, key maps, loop points, effect tables.
  Regenerated: every pixel and every sample.
- Containers (PartyPlanner64 docs + own census): MainFS 0x41DD30 (77 dirs, 4484 files; compression 0/1 as MP1
  plus type 2 "slide" = u32 size + yaz0-like stream with 32-bit code words: own encoder in `native/mplz.c`),
  backgrounds 0x1164160 (67 boards/scenes, 4141 tiles), animated tiles 0x16EC470 (109 raw tiles, LZ type 3),
  audio 0x1750450 (MBF0 music bank, 253 waves; SBF0 x2 effects, 650 waves; all VADPCM with 4 predictors).
- **Pictures are "HVQ-MPS 1.1"** (not MP1's HVQ2). The game's library: init `func_80096C10`, setup
  `func_80096708(header)` (Huffman trees), decode `func_80096188(data, out, stride, work)`. Clean ROM: our CRQ
  decoder sits over the library code, the decode entry jumps to it, the setup call returns at once, header files
  keep only magic + picture size. Board tiles are `HVQS` + CRQ. Dirty side: the retail decoder runs under Unicorn
  once to take the 4x4 colour grid per tile (cache in the work dir).
- 2xx BMP1 bitmaps carry a second bitmap after the first (found by the census): both are regenerated.
- **Briefs**: 444 images are shared with Mario Party 1 (same size, mode and colour grid: `tools/m1_match.py`,
  `m1_map.json`) and reuse its briefs (fonts, digits, names, START/FINISH, coins, stars, NPC faces...).
  Player faces are new in this game (full 64x64 face textures, 13 costumes + 17 expressions per player):
  painted by `faces2.py` (near and far models).
- ROM-DB: the core's "Mario Party 2 (U) [f1] (PAL)" slot is pointed at our ROM's MD5 (EEPROM 4 KB, rumble).
- Dev server port 8242, CDP port 9352. Headless runs are muted.

## Tools
- `games/marioparty2/`: `mainfs.py`, `images.py`, `hvqfs.py`, `audio.py`, `romtool.py`, `extract_spec.py`
  (dirty), `hvq_dirty.py` (dirty), `generate.py` (clean), `briefs.py` (MP1 library) + `briefs2.py` (MP2 tables) +
  `faces2.py`, `taint.py`, `voices.py`.
- Dev (dirty): `preview.py` (retail|clean pairs for a dir without building), `atlas.py`, `look.py` (boot +
  contact sheet), `voice_scan.py`.

## Next
See the end of this file after each session.
