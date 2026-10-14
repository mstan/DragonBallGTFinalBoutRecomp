# Checkpoint and resumed work

Resumed by the owner on 2026-10-14 from `36ba6d1`; the owner subsequently
authorized Sol 6.1 subagents with adversarial review for this task. The record
below describes the original checkpoint. Current evidence is appended to
`validation/README.md` and `docs/WIDESCREEN.md`; the port remains incomplete.

Current owner scope (2026-10-14): park audio replacement investigation and
HLE/precaching. Finish the demonstrated widescreen backdrop gap, run a short
targeted smoke, then use quick human visual/audio review. The owner heard the
latest host-audio smoke and said it sounded okay. These parked features are
unfinished, not implicitly accepted or removed from the longer-term backlog.

Latest priority update: fix the owner-reported moving-camera background flicker
now, original audio extraction/inventory next, recorded replacement later.
Loading work remains deferred. The newer motion report supersedes any claim
that the earlier short visual acceptance proves stable cloud coverage.

The owner subsequently reported a narrow blue-city background (stage 6).
The hook now recognizes the eleven disc-certified stage layouts, including
eleven-row panoramas, stages without a G4 suffix and stage 3's alternate OT.
Independent Sol 6.1 review executed the actual MIPS producer for 88 asset/bank/
scroll cases and passed. The native rebuild and live stage 1/2/4/5 checks pass;
all eleven stages have not been visited live. Legacy city saves restore outside
combat, so city visual confirmation remains the owner's quick check.
Recomp-ui is open with the updated build. Voice work has not started.

The moving-camera defect is now repaired in the title hook: odd-scroll FT4
edge strips and sprites are validated as one complete background, using packet
UVs so queued submissions do not depend on current source scroll. The final
44-second replay has covered clouds in twelve composed captures and returns to
4:3; independent review passes. Recomp-ui is reopened for the owner's check.
No audio extraction or replacement work occurred during this repair.

The resumed backdrop fix passed composed 16:9/21:9 captures, return to 4:3,
and a short moving demo scene. The owner then reviewed the visible session and
answered "Looks okay." The framework now pins
`f9c287f523428aea816fb91cd4ec7d499dcdea8a`, which includes the landed CD fix and adds
guarded opaque-sprite background tags. Title guards recognize the complete
scrolling cloud composite while excluding nearby effects. Guest culling and
packet admission are unchanged. The widescreen feature remains an elective,
default-disabled preview; memory cards and win/progression remain open.
The sprite extension is in [upstream PR #663](https://github.com/RetroPortingToolKit/psxrecomp/pull/663),
merged as `f9c287f5` on 2026-10-14 after CD PR #657 merged as `2fca087a`.
The merged source tree exactly matches the tested `a36754b7` revision. Its
three focused renderer tests and Final Bout rebuild pass. Brief composed
captures verify the backdrop and 4:3 return;
persistent digital input resumes the restored demo scene. See validation for
the exact evidence and limits. The visible review session exited
normally, and its temporary widescreen mod selection was restored.

## Original paused checkpoint (2026-10-13)

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
