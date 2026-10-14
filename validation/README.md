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

## Native overlay and reference investigation, 2026-10-13

The supported CLI rebuild now stages `overlay_toolchain/` beside the product.
The previous manual build lacked it. Dependencies and generated game sources
remain at the recorded pins; no runtime correctness patch has been applied.
Rebuilt executable SHA-256:
`fc894b5ac823e8938aca45d77cd9ff32e0992bfeaa608e13d421c58e76888b3b`.
Rebuild command, with the native toolchain environment and two build jobs:

```powershell
python psxrecomp/psxrecomp_cli.py rebuild --config game.toml --project-root . --build-dir build-release --no-pgo --cmake-extra=-DPSX_DEBUG_TOOLS=ON
```

An isolated Beetle PSX reference run used the same bundled OpenBIOS bytes,
local disc and blank memory card. It reached rendered Goku-versus-Goku combat
through Battle / COM Battle and responded to pause. Its callback verifier at
`0x1F6C` remained valid code. This establishes that this BIOS/disc combination
can enter combat; it does not compare the original Piccolo failure exactly.
Reference evidence is in `build-release/oracle-openbios-20261013/`.

The original freeze dump contains the actual corrupting writes, not just an
unsupported-opcode report. At frame 20,692, guest store `0x80042CBC` copies
script words to a destination repeatedly read from `s3+0x10`. The failing
object is at `0x800A8FEC`; its destination field is `0x800A8FFC`. The copy
starts at `0x800A8ED4`, reaches that field after 75 words and overwrites it
with zero. The next destination becomes `0x12C`; another 1,995 words overwrite
low RAM through `0x2054`, including the BIOS verifier. The exception dispatcher
then calls that destroyed code. The source of the invalid script/copy length
remains unresolved. Raising a reserved-instruction exception alone would not
repair this corruption. Extracted trace subsets are kept with the original
ignored evidence, and `beads-6058.2` remains open.

The rebuilt runtime has now rendered Goku-versus-L.Goku using the interpreter
and Goku-versus-Vegeta with native overlays enabled. A 5x OpenGL capture is
2560 by 1200 and visibly resolves polygon edges at the higher resolution.
This is stronger evidence than the earlier FMV capture, but native/1080p/4K
comparisons, effects and pacing qualification remain outstanding.

The first staged-toolchain session appeared to stop accepting title input.
It advanced after diagnostic `overlay_native_off`; after native execution
was enabled again it accepted input and entered combat. That association is
not yet a demonstrated cause. Shared issue `beads-eio.3.347` records the
observation. No disabled-native workaround is enabled in the product.
The mixed diagnostic session ended normally at frame 69,526 with
`exit_origin=tcp_quit`, zero unsupported midblock instructions, 6,511,487
native overlay dispatches and 2,133,904 interpreted dispatches. Low-RAM write
tracing found no verifier changes after BIOS initialization.

A separate warm-cache run used no diagnostic execution switches. Its bounded
driver matched the main-menu and character-selection images, entered
Goku-versus-L.Goku combat, captured sustained animation and 5x output, and
ended normally at frame 6,091 with zero unsupported instructions and
1,135,261 native overlay dispatches. Injected attack/pause commands alone do
not establish that every input was consumed; visual control validation remains
open. Local evidence and drivers are in `build-release/native-baseline-20261013/`
and `build-release/warm-native-20261013/`.

These are partial baseline results. The original failing pairing, broader
transition coverage, complete matches/results, local versus, audible audio and memory-card
save/load still require qualification. Widescreen/HUD/culling, loading HLE,
netplay and both audio phases remain open.

A subsequent cold-cache run also reached rendered Goku-versus-Trunks combat
without execution switches: frame 5,942, normal TCP quit, zero unsupported
instructions, 8,290 native and 210,502 interpreted overlay dispatches. The
previous warm cache was preserved under a separate title-specific directory;
no other game's cache was touched. The first cold test stopped too early when
the guest temporarily disabled display during loading. The revised driver
tolerates that state for up to 30 seconds. Evidence:
`build-release/cold-native-20261013/` and
`build-release/cold-native-retry-20261013/`.

**Initial control concern (`beads-6058.3`, corrected below).** In the independent
`build-release/input-audit-20261013/` Goku-versus-Boo run, sustained Start for
120 guest frames, release for 120, and another 120-frame hold reached virtual
port 1 (`pad_status`: connected digital controller, buttons `0xFFF7`). The
fight appeared to continue without a visible pause. The reference run had
paused on Start. These screenshots were insufficient to establish an input
defect; subsequent trace and visual checks below supersede that conclusion.

The follow-up `build-release/pad-trace-20261013/` run confirms that SIO receives
the held Start bytes (`41 5A F7 FF` poll payload) and returns to `41 5A FF FF`
on release. OpenBIOS's buffer pointer table at `0xAEDC` names port buffers
`0x8003BC00` and `0x8003BC28`. This narrows the investigation beyond host input
injection: next compare those buffers and the game's input consumer against
the reference. No game-specific Ghidra program is currently in the headless
registry; these addresses were verified from the local code and RAM captures.

The original Goku-versus-Piccolo failure **reproduced with native overlays
enabled** in `build-release/pad-consumer-20261013/`: frame 4,475, unexpected
guest return, identical unsupported word/PC and callback context, after
166,987 native and 64,372 interpreted overlay dispatches. Staging the overlay
toolchain therefore does not resolve this defect. A controlled player-one
Piccolo selection (Down, Right four times, Cross) subsequently reached
Piccolo-versus-Pan combat in `build-release/piccolo-source-20261013/`. Fighter
role or pairing is now part of the reproduction matrix; do not classify all
Piccolo use as broken.

The pause investigation now has positive evidence. In
`build-release/pause-edge-audit-20261013/`, interpreted execution stores the
Start edge at `0x800A9CE8`, sets pause flag `0x800A868C` to one at frame 4,499
(store PC `0x8006A22C`), and clears it on the second press at frame 5,479
(store PC `0x8006A180`). `released.png` visibly shows PAUSE; the final capture
shows resumed combat. Earlier conclusions drawn from isolated captures were
premature. There is no demonstrated input conversion or pause logic defect.

An independent `build-release/native-pause-proof-20261013/` run uses the
default native overlay path without execution switches. Six samples across
held Start and released Start retain pause flag one, and `released-1.png`
visibly shows PAUSE. The second press clears the flag and animation resumes.
It exits normally by TCP quit at frame 8,676, with zero unsupported instructions
and 1,751,471 native overlay dispatches. No runtime patch was required.
Movement/attack and two-port qualification remain separate open checks.

## CD sector corruption fixed (2026-10-13)

The invalid COM script was already corrupt before the copy loop. Final Bout's
streaming decompressor reads a three-sector file at LBAs 18209 through 18211.
At compressed ring offset `0x1000`, it should receive `D1 E1 D5 06` from sector
18211. The failing runtime instead delivered `50 73 64 70` (the next file's
`Psdp` header) from sector 18212. That changes a back-reference offset and
removes the script terminator, leading to the previously documented low-RAM
corruption. Timing traces show sector 18212 pending behind 18211, with zero
lost INT1 notifications; absence of lost interrupts did not imply correct data.

The shared controller now separates the announced decoder slot from the
BFRD-latched FIFO. Pending notifications cannot redirect bytes already requested
for DMA. Multi-sector DMA retains automatic refills, including an arrival in
the middle of draining a sector. Explicit BFRD rearming can reload the retained
announced sector after software clears its FIFO. No timing or speed workaround
is enabled for the game.

The CD state section preserves its legacy prefix and appends the decoder ring,
indices and pending notification deadline. Preflight accepts the old format and
validates the extension before restoring machine state. Tests cover delayed
notification between BFRD and DMA, both DMA refill cases, BFRD rearming, legacy
and current snapshots, pending deadline restoration and malformed extensions.
The new controller test fails against the original implementation. Adversarial
review added a mid-drain arrival case that failed the first candidate fix and
passes after the refill correction. Release CTest: `cdrom_sector_fifo_test`,
`cdrom_irq_mask_test`, and `cdrom_lid_state_test`: 3/3 passed.

Local game evidence (default native overlays, no execution switches):

- `com-fifo-warm-20261013`: old failing slot 2 loads, script begins with the
  expected descending words 8 through 1 and its terminator, sustained
  Goku/Piccolo combat, frame 5,097, normal TCP quit, zero unsupported instructions,
  902,448 native overlay dispatches.
- `com-fifo-fresh-20261013`: boot, main menu, COM selection, Goku/Piccolo combat;
  frame 13,512, normal TCP quit, zero unsupported instructions, 2,575,047 native
  overlay dispatches. Selection-only states were used to vary the random CPU
  opponent; no combat or RAM state from the old build was loaded. Movement,
  a projectile, PAUSE and resumed combat are captured. This uses a warm native
  cache and is not a claim of cold-cache qualification for the patch.
- `com-fifo-round-20261013`: restores a newly saved combat state, reaches Goku's
  defeat and CONTINUE countdown, then returns to the opening movie; frame
  12,149, normal TCP quit, zero unsupported instructions, 1,915,410 native
  dispatches. Save-state restoration is distinct from memory-card save/load,
  which remains unqualified.

All directories above are under ignored `build-release/`. An earlier heavily
traced candidate run (`com-fifo-rearm-20261013`) corrected the script but stopped
under the starvation watchdog at frame 1,889; subsequent runs did not reproduce
it. That observation is retained for investigation, not counted as a passing
run or explained away as proven compilation overhead. Full roster/stage coverage,
win/progression, two-port local versus, audible audio and memory-card saves are
still open. Widescreen/HUD/culling, loading HLE, netplay and audio work remain
separate phases.

Final reviewed-patch replay: `com-fifo-final-20261013`, frame 10,448, normal
TCP quit, zero unsupported instructions and 1,078,532 native overlay dispatches.
The tested executable SHA-256 is
`aa43ee2540c88baee70a430995c69beaaade1c7712f6ba1881b550556e95f62f7`.

## Local versus and light netplay smoke (2026-10-13)

`build-release/local-versus-resume-20261013` completes the interrupted local
versus route: two separate digital ports, player-two selection, Goku/Frieza
combat and independent direction inputs. Pad snapshots show only the intended
port held for each input. Normal TCP quit at frame 7,243, zero unsupported
instructions. This is virtual-controller validation, not a physical-device test.

The requested light two-peer integration smoke passes in
`build-release/netplay-smoke-input-20261013`: native-overlay OpenGL peers on
loopback, rollback enabled, correct two-player selection, Goku/Goku combat,
independent direction inputs and a host-initiated shared save/load. Both peers
report successful slot-1 load receipts (generation 2), return to combat, and
remain active with no reported desync; post-load confirmed ticks advance to
212/215. Both exit normally through TCP quit, at frames 4,274/4,267, with zero
unsupported instructions, in 58.3 seconds. Runtime digest samples agree between
peers. No recomp-net changes were needed. Public lobby/NAT traversal and adverse
network conditions were outside this owner-approved smoke scope.

The first netplay harness used short transient inputs and stayed at character
selection. Its automatic completion flag was not sufficient: visual review
rejected its combat claim. Persistent digital-controller input with explicit
release corrected the harness. Only the second run counts as combat validation.


## Widescreen checkpoint and pause (2026-10-13)

The default-disabled preview builds and executes its native function-entry hook.
The hidden-presenter smoke in `build-release/widescreen-preview-20261013` shows
edge-anchored HUD, wider world and repaired gradient coverage at 16:9, and live
4:3/16:9/21:9/4:3 mode transitions. Normal TCP quit at frame 1,904, zero
unsupported instructions. The 21:9 white-scene sample needs a sequence/reference
check; complete culling, stages, effects and menu/movie validation remain open.
See [implementation and limits](../docs/WIDESCREEN.md).

The owner requested a checkpoint and pause. The private repository and linked
follow-up issues are recorded in [CHECKPOINT.md](../docs/CHECKPOINT.md). No audio
extraction or replacement has begun. No runtime test process was left running.

## Resumed widescreen investigation (2026-10-14)

The owner authorized resumption and Sol 6.1 workers with adversarial review.
The checkout, submodule pin and executable hash matched the documented
checkpoint. Upstream CD PR #657 remains open and unmerged. Central Beads push
completed successfully in 47 seconds with the supported wrapper.

The inconclusive 21:9 white frame is now explained by the stage flash: composed
mod-off 4:3 and adaptive 21:9 sequences both show white, gray fade, and recovery
with fighters/HUD preserved. Independent visual review agreed. Evidence and
scope are in [WIDESCREEN.md](../docs/WIDESCREEN.md#resumed-investigation-2026-10-14).
This covers the restored Goku/Frieza scene only; it does not qualify camera
extremes, other stages, dynamic effects, transitions, or full culling.

Two earlier mod-off sequence attempts remain failed/inconclusive:
`build-release/widescreen-sequence-20261014` and
`build-release/widescreen-sequence-retry-20261014`. Both hit the starvation
watchdog around capture/restoration activity, with no unsupported instructions.
The earlier automatic slow-frame stack is not a stack of the eventual abort;
neither a guest corruption nor a native compiler cause is established. The
successful diagnostic sequence used a longer watchdog, disabled live debug
video toggles and fixed resolution. It cannot erase those failures or serve
as default-runtime stability evidence. Shared observation `beads-eio.3.347`
remains open.

The culling audit rejected changing apparent horizontal checks that also mutate
gameplay state. No guest culling change was made. Audio extraction and FuniDub
implementation remain deferred behind the open core requirements.

The subsequent rebuilt native smoke (`build-release/core-resume-20261014`)
boots through the movie/title and menus into Goku/Goku demo combat at effective
5x, accepts pause, and completes a state save receipt. Review of the visible
`DEMO ON` indicator corrected the initial controlled-combat/attack claim:
this run establishes scene rendering, not player-controlled combat. It uses
real host audio output, the default watchdog and disabled live debug video
toggles. It exits normally via TCP at frame 10,334, zero unsupported
instructions, after 172.25 seconds. Host audio is active with nonzero samples
and zero reported underruns; the owner heard this run and said it sounded okay.
That accepts the sampled audio, without claiming every cue was checked.

The short smoke found an actual stage-specific widescreen gap: the green
Goku/Goku stage's tiled cloud sky stops at the authored horizontal edges.
The stage uses a different backdrop packet layout from the previously tested
rocky stage. This is a targeted follow-up under `beads-q6ao`, not grounds for
an exhaustive QA campaign. The owner explicitly requested quick human visual
and audio review after rudimentary checks.

Smoke executable SHA-256:
`bdccd714c70cfa489ca63407c81d28a162343b3dbfcb5c7be9dd61a74b7d55c9`.

## Cloud-backdrop fix and human acceptance (2026-10-14)

The framework extension accepts explicitly tagged opaque variable textured
rectangles through the existing guarded background service. Three targeted
native tests passed: `gpu_textured_dot_nw_shift_exec_test`,
`gpu_render_pass_provenance_test`, and `ws_hud_anchor_test`. Independent Sol 6.1
review and parent review found no blocker in the final engine/title changes.
Review rejected an earlier fixed-player-side HUD proposal because it would
expose hidden fields at X=512; the final code retains signed-X anchoring.

The README CLI rebuild completed with two jobs and staged the native overlay
toolchain. `build-release/sky-fix-20261014` restores the paused green-stage demo
with a completion receipt, captures composed 16:9/21:9/4:3 presentations, then
resumes briefly at 21:9. Clouds now cover the former flat side strips, the HUD
remains edge anchored, and 4:3 returns to identity. Normal `tcp_quit` at frame
1,530, exit code zero, 25.05 seconds, no unsupported instructions or forced
termination. This uses real host audio, fixed effective 5x, default watchdog,
and `PSX_DEBUG_TOGGLES=0` / `PSX_DYNRES=0`.

Final background statistics: 5,443 tag calls, 15,638 hits, zero rejected tags
or content mismatches, and 1,025 stale lookups rejected by the existing
freshness guard. These counts are not a claim of zero stale lookups. No visible
backdrop gap was found in the paused or moving captures.

`build-release/human-review-20261014` then opens the same scene in a visible
window. The owner answered "Looks okay" to the quick clouds/HUD/motion review.
Together with the earlier audible-audio acceptance, this meets the owner's
requested lightweight review for these changes. It does not establish memory
cards, wins/progression, full roster/stage coverage or widened guest culling.
No broad netplay retest was performed. HLE/precaching and audio replacement
investigation are parked by the owner.
The visible session exited normally through TCP after 112.39 seconds, with no
forced termination. Its launcher restored the temporary mod selection.

Tested executable SHA-256:
`c959bd543b7ebd2f803256c18404da8fcd323018036032ec55ab48d8807b0713`.

## Upstream CD adoption and PR #663 rebase (2026-10-14)

Verified CD PR #657 merged at `2fca087a1bb65fa2aabf88891a2f0777467893b2`
on 2026-10-14. The owner assigned its four-title regression work to another
session. PR #663 is now based on master `d3db61b199e07e757526a2fa1881fd15c95b3659`,
with rebased head `a36754b7eeda86768393eb6bb55af44540ea0aa5`. Its diff remains
three files: the opaque-sprite acceptance condition, API documentation and
targeted tests. All three renderer tests listed above passed again on this
base. The README CLI rebuild succeeded at two jobs and staged overlay_toolchain.

`build-release/widescreen-upstream-adoption-20261014` restores the paused demo
with a successful receipt and verifies composed 16:9/21:9 sky coverage and
4:3 identity. Normal TCP quit, exit zero, frame 1,166, 21.72 seconds, zero
unsupported instructions. Its short Start injection did not demonstrate
resume. A bounded follow-up (`widescreen-upstream-motion-20261014`) confirmed
the pause flag remained set; missing PAUSE text alone is not resume evidence.

`build-release/widescreen-upstream-input-20261014` uses persistent digital
input with explicit neutral/release. Start changes the guest pause flag at
`0x800A868C` from 1 to 0; composed captures show continued demo motion and
effects. Normal TCP quit, exit zero, frame 1,563, 26.23 seconds, zero unsupported
instructions or forced termination. This validates restoration and resume of
the existing demo state, not controlled combat or a new CD-transition route.
The earlier short-input result does not establish an engine input defect.

All runs use fixed effective 5x, real host audio, default watchdog, and
`PSX_DEBUG_TOGGLES=0` / `PSX_DYNRES=0`. Temporary mod selections were restored.
The owner reaffirmed that general working behavior is sufficient and requested
no further validation campaign. Earlier human acceptance remains recorded;
HLE/precaching and audio replacement remain parked.

Updated executable SHA-256:
`05fa9b95a6a830c3ae9f462f0a9cc20c28182099bab19178cbf7f352a885794e`.

PR #663 merged on 2026-10-14 at
`f9c287f523428aea816fb91cd4ec7d499dcdea8a`. A full Git tree comparison against
the tested `a36754b7` head is identical. The project adopts the landed commit
in its submodule and framework_pins.txt; no additional QA campaign is needed
for a commit identity change with the same source tree.
