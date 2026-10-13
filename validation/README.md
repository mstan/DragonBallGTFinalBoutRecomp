# Initial validation record

Date: 2026-10-12. Owning setup issue: `beads-jsz8`; game epic: `beads-6058`.

## Independently verified source

The primary agent read the supplied BIN directly, independently of the scaffold
worker and the framework disc probe. No dialogue/audio was extracted.

| Field | Observed value |
| --- | --- |
| Cue layout | One MODE2/2352 track |
| BIN size | 158,811,744 bytes / 67,522 raw sectors |
| ISO volume | `DRAGON_BALL_FB` |
| Boot | `SLUS_004.93;1` |
| Boot extent / file size | LBA 48,451 / 190,464 bytes |
| EXE signature | `PS-X EXE` |
| Load / entry / text size | `0x80010000` / `0x80010B98` / `0x0002E000` |
| SYSTEM.CNF stack | `0x801FFF00` (separate from the EXE header field) |
| EXE header stack | `0x801FFFF0`, size `0`; matches the probed configuration |
| MD5 | `2f869f926514278b72ffbd671e69b9f7` |
| SHA-1 | `8a2373f133788256cba64a1a0ba9fbb4b4667f71` |
| SHA-256 | `2f9d475fa089bed3f77a3344ea23af0663b30ffe9a2bc0b803bcae389480a15b` |
| CRC32 | `24433280` |
| Extracted EXE SHA-256 | `507f132cdcbb635bbbf7a75e15c62a9d0d51e22ce4432828da784ec03b67cbcc` |
| TOC fingerprint | `51195bfbf616d0713aadd890761af2eb489f8f2629e8a06d64f7d839df7722ae` |
| Initial seeds | 298 boot-EXE JAL/entry candidates; not complete overlay coverage |

These values identify the supplied image; they are not a claim of comparison
against an external dump database. A one-track cue is not evidence by itself
that another track is missing.

## Review

The owner authorized GPT-6.1 Sol subagents for implementation and conventions
research, followed by adversarial review. Findings addressed during setup:

- The sibling framework checkout was an old unrelated feature branch. Select
  upstream master commits for this project instead of inheriting its state.
- The Windows scaffolder inserted embedded UTF-8 BOM characters into CMake
  token blocks; remove them before configure.
- A conditional netplay toggle could silently produce a build without the
  required dependency; require its presence explicitly.
- Windows README examples used ambiguous PATH commands; replace them with
  explicit native Git/Python paths.
- Project metadata incorrectly used an icon filename as the project name;
  correct it to `DragonBallGTFinalBoutRecomp`.
- The generated release wrapper automatically waived overlay-cache checks by
  claiming a committed static AOT shard that this title does not have. Remove
  that waiver and retain the shared packager's validation. `bash -n` passed;
  release packaging itself has not been validated or performed.
- Current upstream templates describe committed generated-C releases. This
  local project keeps generated game/BIOS code and original media ignored;
  no release/CI/publication was requested or created.

The separate documentation review found no concrete medium/high severity issue
in the requirements or deferred audio design. Root review independently checked
the selected framework's internal-resolution parser and source-disc identity.
Final scaffold review found the medium packaging-waiver issue and low metadata
issue above; both were corrected. It found no current build-wiring blocker,
dirty dependency, or reliance on scratch repositories/shared Git objects.

## Bring-up result

The native recompiler emitters built with RetComM clang toolchain 1.0.14.
The primary agent independently compared probe/config identity with the source
audit and reconstructed the boot EXE directly from raw sectors: extraction was
byte-exact and its SHA-256 matched. The two-player setting and one-track netplay
fingerprint gate also passed inspection.

CLI Generate completed using the locally built pinned emitters and staged disc:
2,982 emitted functions, 10 game C shards, and 748 dispatch entries. The generated
marker is `generated/SLUS_004.93_dispatch.c`. Generated code remains ignored.
The log includes out-of-function branch/fallthrough warnings; successful emission
does not prove those paths or streamed overlays execute correctly.

The Windows Release runtime build passed with debug tools enabled. Output:
`build-release/DragonBallGTFinalBout_Recompiled.exe` (20,001,792 bytes).
Configuration confirmed generated game C, bundled OpenBIOS, SDL3 recomp-ui,
recomp-net/ICE, retcomm-rbengine and `PSX_MAX_PLAYERS=2`. Exact dependency pins
are recorded in `framework_pins.txt`.

A bounded hidden-OpenGL smoke reached the opening movie. The primary agent
independently inspected the captured 320x240 frame, telemetry and exit report.
At the 35-second sample: frame 2,990; 3,623,657 static dispatch hits; zero reported
dispatch or segment misses; 701 MDEC decodes; active XA; 5,870 CD data-ready
events and 5,579 delivered CD interrupts. The runtime exited with code 0 through
`tcp_quit` at frame 3,001, after 37.062 seconds.

OpenGL initialized at 5x internal scale for the 1080p preset. The captured movie
was native 24-bit scanout, so the high-resolution capture command correctly
reported that scanout mode unsupported. This is not a 3D-resolution comparison.
Headless mode disabled host audio and physical controllers; XA activity is not
proof of audible output. No overlay coverage claim follows from this short run.

The first smoke harness reused an idle debug socket and lost its connection
while frame telemetry kept advancing. Retrying with a fresh connection per
command obtained the evidence above. A missing quit reply is not a failed quit:
the process exit code and `exit_origin=tcp_quit` confirm orderly shutdown.

Local evidence: `build-recompiler/configure.log`, `build-recompiler/build.log`,
`build-recompiler/generate.log`, `build-release/configure.log`,
`build-release/build.log`, and `build-release/smoke-retry/` (JSON, logs and PNG).

Menus, combat, audible audio, saves, higher-resolution 3D comparisons, adaptive
widescreen, loading HLE/precache and multiplayer matches remain unvalidated.
Those requirements remain open in their owning Beads issues. Audio extraction
and replacement are deferred; the owner's reference links and the Nova research
audit are preserved in `docs/REFERENCE_NOTES.md`.

Local logs/captures belong in ignored `build*/` or `validation/local/`.
