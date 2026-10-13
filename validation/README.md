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

## Gameplay check 2026-10-13

**Result: failed at the first selected fight.** This prevents treating the game
as playable and keeps the audio implementation gate closed. Owning baseline
issue: `beads-2x2x`; concrete defect: `beads-6058.2`. The owner explicitly chose core validation first and a
read-only audio research audit in parallel; no audio extraction was performed.

Tested the existing executable from project commit `31d8fff` with unchanged
dependency pins. Executable SHA-256:
`c7824ecfa7f55599f263152c50f9f32eb2c714d214d872de64e8d9801fd772a0`.
Hidden OpenGL, 1080p/5x, bundled OpenBIOS, original local USA CUE, offline,
debug port 4399, and isolated `build-release/baseline-20261013/saves`.
The headless route has no audible output or physical controller validation.

Observed and visually inspected:

| Route | Result |
| --- | --- |
| Opening movie to title | Passed; title includes a sound-menu prompt |
| Title to main menu | Passed with injected Start |
| Battle to COM Battle | Passed with injected Cross |
| Character selection | Passed; default Goku selected |
| Goku versus Piccolo screen | Passed |
| Transition to fight | Failed: unexpected end of guest execution |
| Attacks, results, return, saves, local versus, audible audio, netplay | Unvalidated |

Debug `press` uses active-low button words: Start `65527` for 20 frames,
Cross `49151` for 10 frames, with releases and screenshots between presses.
The main-menu selection needed two Cross presses (Battle, COM Battle), then
Cross to select Goku and confirm. Full wall times, frame responses and commands
are in `commands.jsonl`; the title can return to attract mode if left idle.
The one-off hidden launch and control scripts are preserved with the evidence.
No RAM edits, gameplay bypasses or forced stage transitions were used.

The last versus-screen checkpoint had 12,731,822 static hits and zero reported
dispatch misses. Those counters did not establish native overlay coverage:
the final report records 528,376 interpreted overlay dispatches and zero
native overlay dispatches. Startup explicitly reported no bundled
`build-release/overlay_toolchain`, using the existing interpreter fallback.
Qualify/stage the supported native overlay path in the next baseline work.

Final report at frame 20,692:

- Guest PC `0x00000000`, last tracked function `0x0000282C`, store PC
  `0x000028F0`; log reports execution completed, not a requested quit.
- `interp_unsupported.midblock_count=2`; latest unsupported instruction
  `0xFFFF0001` at `0x00002034`, reason `primary opcode`; reported block entry
  `0x8006DBFC`, entry RA `0x0000293C`, SP `0x00008548`.
- CPU EPC `0x80041E64`. These are diagnostic observations, not proven faulty
  hook addresses or a demonstrated causal explanation.
- The automatic freeze dump classified the stall as `hard_freeze`. Its host
  stack, resolved with the pinned toolchain's `llvm-addr2line`, was
  `SDL_SYS_WaitThread -> SDL_WaitThread_REAL -> overlay_capture_wait_pending
  -> shutdown_runtime -> main`. Thus the captured host stall is during
  shutdown waiting for capture work, not evidence of a live combat loop.
- The process eventually exited code 0 after 415.171 seconds, without the
  harness's 900-second cutoff. Report: `reason=atexit`, `exit_origin=unknown`.
  No quit command was issued. Exit code 0 does not make this gameplay test pass.

Local evidence: `build-release/baseline-20261013/` contains `launch.json`,
`runtime.log`, `commands.jsonl`, screenshots, `baseline-summary.json`,
`psx_last_run_report.json`, `freeze-summary.json`, the automatic full freeze
dump and `exit.json`. The early TCP connection refusal occurred before the
slow startup reached its debug listener; subsequent menu commands succeeded.

Next investigation: reproduce a bounded menu-to-fight route, inspect the
unsupported-instruction/OpenBIOS callback path and overlay transition, compare
against the reference execution, and separately account for capture shutdown
latency. Do not import Nova's claimed RI fix without establishing the same
cause, patch generated C, or hide a correctness repair behind an audio toggle.
