# External research references

The owner supplied these references during setup on 2026-10-12. They are
research inputs; no code, patch, media or Ghidra database was imported.

The 2026-10-13 [FuniDub audit](FUNIDUB_RESEARCH.md) reviews the owner's research
ZIP, inspects the supplied BT3 ISO metadata, and pins verified community AFL
name lists and further format/context leads. No audio has been extracted.

## Brazilian translation/redub

The [audio design](VOICE_REPLACEMENT.md#owner-provided-research-leads) records
the [ByFTR forum thread](https://www.romhacking.net.br/index.php?topic=2166.0),
its matching source-disc CRC and tooling/coverage leads. Use it for the later
dialogue inventory and recorded-clip workflow. Extraction remains penultimate.

## NovaPowers project snapshot

Inspected [revision 4807432f2fb6da2d6d9a753bac318c4f4f11ee97](https://github.com/novapowers0/DB-Final-Bout-Recomp/tree/4807432f2fb6da2d6d9a753bac318c4f4f11ee97)
of the owner's [repository reference](https://github.com/novapowers0/DB-Final-Bout-Recomp).
The [license](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/LICENSE) is MIT, copyright 2026 NovaPowers.
Preserve applicable notices if code is reused later.

Its complete tree has ten source helpers under
[`ghidra_proj/`](https://github.com/novapowers0/DB-Final-Bout-Recomp/tree/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/ghidra_proj),
without `.gpr`, `.rep` or annotation-export files. No dialogue codec,
bank/sample-ID/speaker map or audio-trigger inventory was found in the inspected
material. Source-level investigation tools may still help profiling.

### Useful authored leads to reproduce

The [technical notes](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/AGENTS.md) describe
`/MENU/STEP00.BIN`, `STEP01.BIN`, `STEP02.BIN`, `STEP03.BIN`,
`STEP40.BIN` and `STEP999.BIN`. A combat member is reported at STEP40 file
offset `0x22060`, size `0x12354`, mapped at `0x80060000`.
Historical captures starting at `0x80068000`/`0x8006A000` can be partial
views of that member. Original capture evidence is private: reproduce exact
bytes and mapping against our disc before using these addresses.

The [configuration](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/game.toml) lists overlay entries at six load bases
(`0x80060000`, `0x80068000`, `0x8006A000`, `0x8003F000`,
`0x80047000`, `0x80056000`). Those lists have no `bytes_crc`
qualification. Same address alone is insufficient identity for overlay reuse.

[`tools/analyze_session.py`](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/tools/analyze_session.py) and
[`analyze_latest_session.py`](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/tools/analyze_latest_session.py)
are leads for capture/PC inventories and freeze reports. Treat instruction
patterns as candidates, not proven renderer or audio functions.

The [combat-transition investigation](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/PLAN_SOLUCION_CRASH_Y_COMBATE.md)
identifies a Little Goku/Piccolo regression route. Check our framework's existing
Reserved Instruction behavior before proposing any shared-runtime change.
The author's specific transition fix remained manually unvalidated in this snapshot.

### Adversarial review observations

- [Boot seeds](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/seeds/ghidra_funcs.txt) match our 298 entries exactly.
  [`symbols.toml`](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/symbols.toml) calls `0x80010000` BootEntry;
  our independently verified entry is `0x80010B98`. Do not import that label.
- Ghidra `list_funcs.java`/`list_funcs.py` enumerate functions and hardware
  references; they are helpers, not established annotated function maps.
- [`ram_dump.py`](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/ghidra_proj/ram_dump.py) skips failed read blocks.
  A reused dumper must preserve address offsets and explicitly mark unread data.
- [`scan_mips.py`](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/ghidra_proj/scan_mips.py) has hardcoded paths and
  incomplete/incorrect instruction/address decoding. Verify candidates with the
  real disassembler. [`scan_ws.py`](https://github.com/novapowers0/DB-Final-Bout-Recomp/blob/4807432f2fb6da2d6d9a753bac318c4f4f11ee97/ghidra_proj/scan_ws.py) uses stale
  signatures relative to the later combat notes.
- RAM-probing helpers assume localhost port 4370; the offline verifier assumes
  an older cache namespace. Adapt them to the selected runtime instead of
  executing unchanged scripts.

Use the configured headless Ghidra MCP workflow for future analysis and commit
human annotation exports only. Track core/overlay follow-up in `beads-2x2x`
and `beads-aubo`; deferred audio inventory remains `beads-bqsp`.
