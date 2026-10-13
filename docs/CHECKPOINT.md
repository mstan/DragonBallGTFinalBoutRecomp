# Paused checkpoint: 2026-10-13

The owner requested a safe commit, private repository, follow-up issues, and a
pause. Work is paused after the first widescreen preview smoke; the overall port
is **not complete**. Source, configuration, annotations/recipes and validation
notes are tracked. Game media, generated code, local captures, saves and audio
remain ignored.

## Validated so far

- Windows release build and native-overlay toolchain; movie, menus and selection.
- Several combat routes at 5x internal resolution, movement/projectile,
  pause/resume, state restoration, defeat and CONTINUE.
- Local two-player combat and the owner-scoped light loopback netplay smoke:
  separate players, a match and host save/load, no reported desync.
- Default-disabled widescreen preview: native hook executes, 16:9 HUD fields
  anchor to the edges, sky/floor gradients cover the reveal, live window changes
  select 4:3/16:9/21:9 and return to identity mode. This is a narrow smoke,
  not culling or all-stage qualification.

The CD correction is a **psxrecomp engine fix**, pinned at
`348545a49f65b46eb25198b4a5230803233a9cf8` and submitted in
[upstream PR #657](https://github.com/RetroPortingToolKit/psxrecomp/pull/657).
It was open and mergeable, with no review/check results, at this checkpoint;
it has not been merged by this project.

## Follow-up issues

Beads remains the central tracker. The private repository issues provide a
reviewable backlog linked to those owning tasks. Framework observations retain
framework ownership even when surfaced by this title.

| Follow-up | Central task |
| --- | --- |
| [Complete core gameplay, memory-card and audio validation](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/1) | `beads-2x2x` |
| [Finish adaptive widescreen, culling and HUD validation](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/2) | `beads-q6ao` |
| [Qualify internal-resolution presets and renderer coverage](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/3) | `beads-rxvr` |
| [Implement measured loading HLE and precaching](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/4) | `beads-aubo` |
| [Extract and inventory original dialogue after core validation](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/5) | `beads-bqsp` |
| [Build FuniDub donor ISO mapping and reinjection workflow](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/6) | `beads-vbfi` |
| [Resolve or retire qualified native-overlay stall observations](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/7) | `beads-eio.3.347` |
| [Preserve saved registers in automatic freeze diagnostics](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/8) | `beads-eio.3.348` |
| [Track upstream CD FIFO PR and adopt the landed engine pin](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/9) | `beads-eio.3.349` |

Resume with widescreen/culling and the remaining core acceptance checks, then
loading improvements. The audio research audit is complete; original dialogue
extraction and FuniDub implementation have not started. Original extraction
stays penultimate, replacement last. Netplay coverage stays light unless a new
title integration change demonstrates a need for more.

Evidence is in [validation](../validation/README.md),
[widescreen notes](WIDESCREEN.md), and the ignored run directories named there.
The temporary widescreen mod selection was restored after the smoke run.
