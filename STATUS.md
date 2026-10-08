# Mario Party 2 clean room: status

## State (2026-10-08)
- **Published**: https://andrewnakas.github.io/marioparty2-cleanroom/ (repo `andrewnakas/marioparty2-cleanroom`, site on
  `gh-pages`).
- Clean ROM = retail program + every picture and sound regenerated: 6151 MainFS images, 67 backgrounds (4141
  tiles), 103 animated tiles, 89 stills, 903 waves. 32 MB. Our picture decoder replaces the HVQ-MPS decoder.
- **Taint: 0 failing** (`TAINT.md`): textures, pictures, samples, raw image, plus a map of every differing byte.
- Checked headless (muted): clean ROM boots, logos, title, Mario Land. Rules Land board (dice, turns, HUD) was
  walked on a dev build with retail backgrounds; audio level over a scripted run follows the retail pattern.
- Painted / typeset: six players' faces (near + far models, 17 expressions), HUD + menu portraits (MP1 busts),
  fonts, digits, names, ranks, COM, dice faces, START/FINISH/TIME UP/GOAL/DRAW/MISS/CLEAR/GAME OVER/PAUSE,
  mode and menu labels, land logos, button icons, title logo and land signs inside backgrounds (`scenes2.py`).
- Voices: 28 placeholder lines (Piper) in `games/marioparty2/voices/`; practice pack in
  `D:/n64work/mp2work/practice/` (announcer, mario, luigi, peach, wario + `SCRIPT.txt`).

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

## Taint notes
- 12 textures render with 8 levels (`generate.COARSE`) and backgrounds 19 and 21 have a shifted lattice
  (`generate.NUDGE`): each had one chance run of 33-46 B at 16 levels.
- The raw scan blanks files kept as they are (motions, path tables 10/64-80, glyph metrics) like the pack layout
  tables: they equal retail by design and are listed as kept facts.

## Headless testing notes
- Start (Enter) skips Toad's entrance in Mario Land; two or three Start presses then A. Scripts in `look.py` syntax.
- From the Mario Land hub on, the emulated frame counter (`frame=` in the heartbeat) advances about 1 per second in
  headless Edge. Measured the same on the clean ROM, a no-voice dev build and the dev build with retail pictures
  and sound; FB emulation off and the interpreter core do not change it; the anti-throttling browser flags are
  already set. So it is not caused by the regenerated assets, but the cause is not found, and deep walks (board
  turn, minigame) take many minutes headless. Not checked in a real browser: if the hub feels slow, tell me first.
- Walked so far on the clean ROM: logos, title, Mario Land, Toad's dialogs, choosing Rules Land, the pipe.
  The Rules Land board itself (dice, turns, HUD) was only seen on a dev build with retail pictures and sound.

## Next
1. Walk a full game on the clean ROM: mode select, a real board turn, a minigame, results.
2. Board backgrounds and the 89 minigame instruction pictures are a blur of the kept grid: draw paths / flat regions.
3. Space icons, framed item squares in dir 0, NPC portraits (0/92-132), intro arch signs (dir 14), mode badges in dir 9 (HARD/NORMAL/EASY,
   1P-4P/COM, BATTLE/TRIAL/DUEL), name plates 10/359-368.
4. Palette sharing: splash sprites 0/48/p8-12 turn green because they share 16 colours with typeset digits.
5. Voices: confirm speakers by ear; Yoshi and DK have no lines yet.

## For the morning
- Open https://andrewnakas.github.io/marioparty2-cleanroom/ : Enter = Start, X = A. First ROM download can take a
  minute. Tell me what looks wrong first.
- Known rough spots: backgrounds are blurred colour; many icons are colour blobs; Wario's face layout is a guess.
- To record voices: `D:/n64work/mp2work/practice/` (SCRIPT.txt + `practice_<who>_call_and_response.wav`). Lines marked
  (?) had their speaker and sometimes their words guessed by a speech recogniser: listen first.
- Another session's folder `D:/n64work/marioparty2/` (ROM-import emulator bridge) was left untouched.
