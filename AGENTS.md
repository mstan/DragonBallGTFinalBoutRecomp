# DragonBallGTFinalBoutRecomp

## Tracking and scope

Use the central Beads database at `F:\Software\beads\issues`; never initialize
a database in this repository. System epic: `beads-eio`. Game epic:
`beads-6058`. Initial scaffold: `beads-jsz8`. Search and claim the relevant
child issue before substantive work, update evidence, and close only validated
outcomes. The feature dependency graph lives in Beads.

Work solo unless the owner authorizes subagents for the current task. For the
initial setup, the owner explicitly requested GPT-6.1 Sol workers with
adversarial review. This does not authorize delegation on future tasks.

For the resumed 2026-10-14 task, the owner freshly authorized Sol 6.1 workers
with adversarial review. Keep QA proportionate: short automated smoke and
targeted regression checks, followed by the owner's quick high-level visual
and audio review. Do not run exhaustive roster/stage/rendering campaigns when
a quick human check is sufficient; expand only for concrete defects.

The owner's latest goal authorizes completing FuniDub from the supplied BT3 ISO,
including the local pack and launcher workflow after original cue discovery and
curated donor matching. Fresh Sol 6.1 subagents are authorized for bounded
parallel discovery, with adversarial review. The owner accepted the initial donor
reel in VLC. Original SPU tables/pitch and donor event categories are now traced;
277 selected SPU candidates have a reproducible local replacement recipe. In-game
audition and launcher qualification remain open. Read `docs/FUNIDUB.md` and the
original/donor table reports; `docs/AUDIO_INVESTIGATION.md` is historical.
Loading work stays parked. Defer high-level listening to a short owner review
when available; sample approval is not full replacement coverage approval.

## Source and dependency rules

- Target the supplied USA disc, `SLUS-00493`. Identity is in
  `game.toml`, `catalog_identity.json`, and `disc_probe.json`.
- Keep disc images, boot EXE, generated game C, retail BIOS, Ghidra databases,
  original/third-party audio, video, private subtitles, and extracted asset
  packs out of Git. Local media lives under ignored `disc/`, `analysis/`,
  or `local-media/`. Commit extraction/edit recipes and hashes when needed.
- Root submodules `psxrecomp/` and `recomp-ui/` and their nested gitlinks
  are the dependency pins. Do not inherit another worktree's dirty state or
  float dependency branches during a reproducible build.
- Read framework code/docs at the pinned revision; the sibling framework
  checkout may be on an older unrelated branch.
- Do not copy title-specific hooks, addresses, culling predicates, HUD packet
  layouts, loader bypasses, or controller assumptions from other games.
- Use the headless Ghidra MCP registry workflow if needed. Never launch its
  GUI or commit `.gpr`/`.rep`; export human annotations under
  `ghidra/annotations/`.

## Product requirements

The requested destination is higher internal resolution, faster loading through
verified HLE and precaching, adaptive widescreen, and two-player recomp-net.
Configuration or compilation alone is not gameplay validation. Maintain an
original/reference path for comparison. Correctness fixes work by default;
elective enhancements may be optional.

Internal-resolution settings belong in `game.toml [video]`.
`game_options.toml` is for reverse-engineered native game option persistence,
not arbitrary host settings. Never invent a generic precache setting.

Any PR touching recomp-net (including a pin) or netplay UI must retain existing
assignees and add GitHub user `TechnicallyComputers`.

The owner requested light netplay testing on 2026-10-13: trust the tested shared
recomp-net engine and check Final Bout's integration (separate player ports,
session startup, short versus match and a load/rematch). Broaden testing only
for a demonstrated title integration defect or newly introduced title hooks.

## Audio phase order

Complete and validate the core game work first. Then extract and catalog the
original dialogue as the penultimate phase. Existing-recording Funimation-cast
replacement is the final phase. Do not start either during scaffold work.

Replacement must use existing recorded excerpts, with source/hash/timecode and
edit provenance. No voice cloning or generated speech. Menu and in-fight cues
are both in scope; verify the actual supplied revision's language and cast.
The owner supplied a BT3 USA PS2 ISO on 2026-10-13 and named the feature
FuniDub: choose the ISO in the launcher, then prepare and map clips locally.
They explicitly reaffirmed core gameplay first, audio research now. The ZIP
and online AFLs are research leads, not validated target cue mappings.
TV media is a possible later source for measured gaps. See
`docs/VOICE_REPLACEMENT.md` and `docs/FUNIDUB_RESEARCH.md`.

## Windows

Use explicit native executables when PATH includes MSYS shims. Do not execute a
bare data path or mix shells for filesystem mutations. Verify the exact scoped
absolute target before recursive deletion; use PowerShell/.NET, never
`cmd /c del`, `rmdir`, `move`, `copy`, or `mklink`.
