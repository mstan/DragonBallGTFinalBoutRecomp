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

## Controller mode restriction (2026-10-14)

The owner's visible physical-controller boot reported "Controller 1 port is
not connected properly." Its local settings selected Analog for the DualSense,
overriding the title's Digital default. The existing engine/UI contract supports
`[controller] lock_mode = true`: this build now declares that restriction beside
`default_mode = "digital"`. The device picker stays available; the incompatible
mode selector is hidden, and the runtime clamps stale preferences even for a
direct boot. No engine or recomp-ui change, regeneration or rebuild is required
for this runtime configuration change. The launcher is reopened for the owner's
controller and widescreen checks. This records the observed warning and the
configuration correction; successful physical gameplay remains a human check.

## Moving-camera cloud flicker repair (2026-10-14)

The owner's Trunks/Goku screenshots demonstrate a real intermittent backdrop
defect after the earlier visual acceptance. The targeted moving Goku/Goku replay
in `build-release/sky-camera-before-20261014` reproduces narrow clouds in five
of twelve composed captures. Thirty-six object/packet snapshots establish that
odd horizontal source scroll introduces a 40-byte, one-pixel FT4 strip at each
row start. The sprite-only guard rejected these valid mixed composites.

The Sol 6.1 worker updated the title hook to validate FT4 edges, sprites, the
exact map/atlas sequence, geometry and links as one bounded composite. Independent
review identified PsyQ's queued DMA callback: current object source scroll can
differ from submitted packets. The final implementation derives bounded origin
candidates from packet UVs and requires the complete four-row/gradient proof
before tagging. Guest data, GTE, culling and the shared renderer are unchanged.

A bounded offline packet audit accepts all 36 snapshots and both banks, plus
the earlier shifted-pool capture. Nine malformed packet/map/link cases reject;
aligned crop zero and crop 31 with an FT4-only first edge pass. Recognition is
unchanged when live source scroll is varied independently. The independent
review and parent review found no remaining blocker in the final implementation.

The README CLI rebuild succeeded with two jobs and staged overlay_toolchain.
`build-release/sky-camera-final-20261014` restores the same demo with a completion
receipt, resumes through persistent digital input, samples moving-camera/effect
activity, and returns from 21:9 to 4:3. All twelve composed captures show covered
clouds; return mode is zero with zero reveal. Normal TCP quit at frame 2,663,
exit zero, 43.91 seconds, zero unsupported instructions, no forced termination.
The run uses fixed effective 5x, real host audio, default watchdog and
`PSX_DEBUG_TOGGLES=0` / `PSX_DYNRES=0`. Owner mod selection is restored byte-for-byte.

This is a focused green-stage demo rendering regression, not complete-game or
controlled-combat acceptance. Recomp-ui is reopened for a brief owner check.
Intermediate `sky-camera-after-20261014` captures are retained; the final run
includes the queue-independent refinement and the 4:3 return check.

Updated priorities are background repair now, original voice extraction/inventory
next, recorded replacement later. Loading HLE/precaching is deferred and no
longer blocks extraction. No audio was extracted during this task.

Final executable SHA-256:
`eb820d17e4a2d70d498f7d178f37033cec30f843c4a402061e9abdc4e6bc4490`.

## Additional stage backdrop layouts (2026-10-14)

The owner reported the blue-city backdrop still occupying the authored width.
The prior green-stage guard covered only four rows; this stage has eleven.
The independent asset inventory certifies eleven stage IDs and eight map sizes
from the actual HAIKEI resources and the stage descriptor table at `800545CC`.
The title hook now matches each exact layout/atlas, stage-specific G4 counts
and stage 3's alternate OT. Submitted packet Y replaces live camera Y in the
composite proof. The largest existing panorama is 4,928 bytes / 198 primitives;
even three G4s fit within the existing 0x3000-byte packet bank. No guest packet
admission, culling, RAM/GTE or shared engine change.

`build-release/stage-background-offline-20261014` retains the decoder/audit and
independent Sol 6.1 review. Eighty-eight source-derived cases cover eleven
assets, both banks and crops 0/2/1/31 at map wraparound. Exact bank-end cases
accept; one-word crossings and seventeen packet/map/object mutations reject.
Queued source-X/object-Y/camera-Y changes preserve recognition. The independent
review executes the actual captured MIPS initializer and producer in Unicorn;
its serialized packet words agree for all 88 cases. Stage 5's enabled synthetic
cases are explicitly counterfactual: the actual initializer disables its
panorama, which the hook continues to reject. This is offline serialization
coverage, not native C-hook or eleven-stage runtime acceptance.

The README native CLI rebuild passed with two jobs and staged overlay_toolchain.
`build-release/stage-background-before-20261014` revealed that legacy city slots
1/2 actually restore to title/selection with leftover city packets, display320
and no combat tags. They are source-only evidence, not city visual acceptance.
Its slot 3 is an actual stage 4 fight with an eleven-row, gradient-free panorama;
the old guard leaves that backdrop narrow.

`build-release/stage-background-final-20261014` reaches a fresh stage 1 fight,
display512, effective5x and native-wide margin170. Its composed capture shows
covered mountain background with 3,264 sky tag calls and 8,704 background hits,
zero rejected/mismatched/stale background tags at that sample. An attract-mode
city search was stopped through normal runtime quit; it did not capture city6.
Runtime exit zero in 192.67 seconds, no forced termination. The finder helper's
connection error follows that deliberate quit and is not a game failure.

`build-release/stage-background-city-final-20261014` attempts an isolated city
selection-table override, but the route subsequently reaches stage 5. The
`city-motion-*` filenames therefore denote stage 5, as their metadata records;
they do not prove city6. No such override is in the product. The final targeted
sequence restores known slots with completion receipts and captures three
moving samples each of stage 4 (tall panorama/no G4), stage 2 (green clouds)
and stage 5 (disabled panorama/gradients) at 21:9, then returns to 4:3 mode0,
margin0. The backgrounds cover the displayed width. Final counters report
102,032 background hits, zero rejected/mismatched tags and 264 stale lookups
rejected by the existing freshness guard. Stage 4's terrain has an abrupt edge
in the reveal; world admission/culling fidelity is not accepted by this check.
Normal TCP exit zero at frame12,600, 209.70 seconds, no forced termination or
reported unsupported instructions. All these native runs use real host audio,
fixed effective5x, the default watchdog, debug toggles0 and dynamic resolution0.
Temporary mod state is restored byte-for-byte; isolated saves stay ignored.

The owner launcher is reopened in `build-release/owner-stage-background-20261014`
with the current personal mod/device settings, without injected input or a
test-state load. All eleven source layouts were checked, but live checks cover
stages1/2/4/5 only; city6 and other live stage visits remain unaccepted. No audio
extraction/replacement or loading enhancement work was performed.

Executable SHA-256:
`3b1b54820dff3f33c1b3815981e6ea4258294a4a1b3aa61a1d72cb3c301ea8fb`.

## Retained native-wide composites during resolution changes (2026-10-14)

The owner reports occasional green-stage background overlap/flicker and permits
closing the game for work. Read-only `owner-stage-background-20261014/watch-*`
captures landed in the opening movie; they do not reproduce a combat defect.
That visible session exits normally at frame44,729 after 811.33 seconds. Its
closing diagnostics report dynamic resolution disabled, zero automatic up/down
steps and zero native-wide reallocations. It therefore does not establish the
cause of the owner's intermittent symptom.

Independent review found a separate GL scale-step correctness bug: `dyn_apply`
uses a margins-only condition that omits the full-background-composite latch,
although presentation correctly forbids canonical centre copying in that mode.
The cleared new FBO loses its centre until redraw. Framework branch
`work/native-wide-dynres-composite`, commit `28e12c737252036ac406263f230b7934f2fe9afa`,
reuses `wide_center_is_canonical()` for rescale column selection. Shared Beads
ownership is `beads-h696`; [PR #665](https://github.com/RetroPortingToolKit/psxrecomp/pull/665)
merged upstream on 2026-10-14 as `6e177accccef7460a9cb9f5c1e40bc0144452d1c`.
The merge tree exactly matches the tested commit, which is retained in upstream
history. The local game already pins this landed commit;
CD and sprite correctness fixes remain included and enabled.

The bounded `run_gl_scale_invariance.py --steps-only` check runs on the native
Windows Clang22/SDL3/NVIDIA GL3.3 toolchain. Existing canonical scale/mask checks
pass49/49; the added two-bank retained-composite checks pass25/25. The new test
compares every pixel at 3x -> 5x -> 3x before redraw and verifies native VRAM
unchanged. A negative control changing only the production condition back to
the original leaves canonical checks passing but fails the new regression with
4,096,000 centre pixel mismatches per bank. Fixed source bytes are restored.
Standalone test adapters were updated for current renderer APIs; independent
review verified types and guards for the six embedding fixtures. The first
attempt's missing-symbol link failure is retained separately, not counted as
a passing run. No broad title or renderer matrix was run.

Evidence remains ignored under
`F:/Projects/psxrecomp/worktrees/native-wide-dynres-composite/build/`:
`dynres-composite-fixed/scale-4nrgv68c/receipt.json` and
`dynres-composite-original/scale-g5c964xn/receipt.json`.

The README native rebuild passes at two jobs. The isolated
`build-release/wide-dynres-smoke-20261014` run restores the green demo with a
completion receipt, checks explicit 3x/5x/3x steps inside one handler, then
captures 21:9 and returns to 4:3. Every scale step succeeds with unchanged
guest-visible VRAM hash `d4d0224ff7c4ee4c`; restored scale5, mismatches0. Composed
captures show covered background; final mode0/margin0. Normal TCP exit zero at
frame1,149 after18.80 seconds, no forced termination or reported unsupported
instructions. Default watchdog, real host audio, dynamic resolution enabled
for this targeted step check, debug toggles0. Mod state restored byte-for-byte.

Recomp-ui is reopened without injected inputs or a test-state load in
`build-release/owner-wide-dynres-20261014`. The rare owner-reported overlap
remains unresolved; this separate scale-step fix is not claimed as its cure.

Updated executable SHA-256:
`5fc0ccea337b762fb16ecde5faddc3e112e67aed8041cf2acabbb85731769a2b`.

## First audio-replacement investigation (2026-10-14)

The owner resumed audio investigation and accepted a short BT3 source reel with
"those are all good," after asking for VLC playback/replay controls. The reel is
three ADX dialogue candidates and one short Sony-bank sample, not an installed
voice pack. Original victory examples still have unverified playback pitch.

`tools/audio/probe_sources.py` rechecks the exact original track SHA-1, the
donor PVD/AFS-table identities and pinned AFL metadata, then writes local
inventories. Eight synthetic malformed-container/alias/extra-record tests pass.
Nine local FFmpeg examples decode with exact expected sample counts/rates and
nonzero PCM. The untrimmed ADX negative control produces 59,008 frames where
the header declares 58,994; the probe's header-based trim yields 58,994.

Direct source inspection finds 54 nonlooping victory candidates, 54 battle XA
groups and six other XA groups; these are not an established dialogue count.
Four inspected donor voice packs each contain 57 bounded Sony-wave candidates;
one of those short samples decodes at its actual 16 kHz header rate. Full original
cue inventory, actor/event matching and reinjection remain open. No runtime,
launcher, netplay or game-configuration changes were made. Evidence/media remain
ignored under `analysis/audio-investigation-20261014/`; the source procedure,
hashes and limitations are described in [the audio report](../docs/AUDIO_INVESTIGATION.md).

## FuniDub native preparation and first game integration (2026-10-15)

Framework `fd6b89cc` and recomp-ui `1fa1f24` are exact detached dependency pins.
Their generic support is in ready upstream PRs
[psxrecomp #667](https://github.com/RetroPortingToolKit/psxrecomp/pull/667) and
[recomp-ui #100](https://github.com/RetroPortingToolKit/recomp-ui/pull/100).
Native Windows Clang generation/rebuild passes through the README CLI, two jobs,
including the full frontend and staged overlay toolchain. Executable SHA-256:
`178e622f278d310520b85e8eecaf9e0a96e18f8c78b9f9cf2990f3a2e04a7b08`.

Native codec bounds/timing/reproducibility tests pass; four real ADX outputs match
FFmpeg 7.1 at their declared lengths. The first pack replaces 277 selected SPU
candidates, is 14,563,328 bytes, and hashes to
`ae0d041f62b6dee7f6f084a60b0d9566a9c34e7f71f67e2ee9087a99ac0d1715`.
All 277 changed cues are nonzero; original flag bytes and every unmapped byte
remain unchanged. No converted cue has PCM rail samples. Sol 6.1 independent
checks cover all target extents, raw-body boundaries, donor identities and
sample-fit bounds. Era/form substitutions and shared attack/charge aliases are
explicit in the source-only recipe. This is not complete voice coverage.

The actual media provider resolves three verified immutable overlays. Cancel at
roughly 30% publishes no derived binding. A changed recipe identity rebuilds;
malformed receipts and corrupted pack bytes repair to the same expected output
hash. Unsupported recipe versions fail while preserving the previous pack.
The final qualified receipt probe hits. The Windows deep-path failure found in
the first provider attempt is fixed by hashing the complete cache identity into
one directory component. Cached-file validation exceptions now cause repair.

The real hidden launcher shows progress and Cancel, closes safely during cold
preparation, then completes preparation and displays FuniDub with its ISO picker.
`build-audio-review/launcher-first`, `launcher-prepared` and `game-smoke/mods.png`
retain composed frontend evidence. Personal mod/settings files are restored
byte-for-byte by each harness; all media and captures remain ignored.

Two default-watchdog attempts abort: FuniDub-on at frame 13,445 during combat
loading, and FuniDub-off at frame 4,651 during the title/demo route. Both report
zero unsupported instructions. Independent reinspection confirms all 277 sample
writes stay inside uncompressed SPU resources, with no compressed/XA overlap.
These observations extend the existing qualified stall report (`beads-eio.3.347`,
GitHub #7); no compiler cause or FuniDub regression is established.

The subsequent `build-audio-review/game-qualified` run uses
`PSX_STARVATION_TIMEOUT_US=30000000` diagnostically, with `PSX_HOST_MUTE=1` and
`SDL_AUDIODRIVER=dummy`. It cold-boots through the launcher, menus and selection
to Goku/Boo combat. A live SPU-RAM capture matches 512 replacement bytes for each
of Goku's nine and Boo's eight mapped combat waves. Save slot 1 reports generation
1 / last_ok 1; its load reports generation 2 / last_ok 1, and subsequent frames
and composed captures advance. Normal exit is zero. The extended watchdog is
not a production fix or default-performance acceptance. The capture is live;
legacy TCP pause/continue commands are removed and did not pause this run.

XA attack audio, unclassified sounds and 46 spoken-fit gaps remain original.
The earlier donor reel approval does not establish acceptance of every new edit,
menu/victory trigger, mixed output or actor/transcript. A 19.38-second original
XA reel is available for brief human classification, with hashes/timecodes.
No new game-compatibility, full-roster or exhaustive netplay claim is made.

### Source verification fallback and content admission

The later native build pins framework `f3236362` and recomp-ui `1fa1f24`, with
executable SHA-256
`67fd282d0acb8b73401407c1d78a350f09b76af8f1dec90fc36c42a131349167`.
The README rebuild route passes with two jobs and stages the native overlay
toolchain. The initial resource-overlay change in PR #667 has landed; the
subsequent content-identity fixes and Windows fallback are additional changes.

Rapid rewrite probes found Windows file-ID/size/timestamps can remain identical
after a same-size rewrite with restored mtime. The framework therefore declines
cheap Windows file identity and takes its existing full-verification path;
[PR #669](https://github.com/RetroPortingToolKit/psxrecomp/pull/669) tracks that
correctness fix. Both worker-enabled and legacy `mod_runtime_test` pass,
including cold-offer/direct-commit fingerprint agreement and rejection of
same-path source changes. POSIX identities are unchanged.

The updated title provider verifies every selected source payload and the fixed
pack hash before reusing encoded bytes without qualified stamps. Its native
checks pass: cold preparation 15,007 ms, receipt repair 3,420 ms, pack repair
2,970 ms, unsupported-recipe rejection 393 ms, declined cheap probe 17 ms, and
source-verified pack reuse 662 ms. All successful paths retain the expected pack
hash. These are local preparation timings, not faster game loading. They
supersede the earlier Windows qualified-receipt-probe observation above.

The bounded muted two-peer gate in `build-audio-review/net-content` passes:
matching FuniDub selections reach ticks 128/133 with no reported desync;
FuniDub-on/off remains at tick zero with `content_mismatch` on both peers,
unchanged after another second. All four processes exit zero. This checks
content admission only, without repeating the accepted match/save-load smoke.
Earlier harness attempts omitted the executable's bundled BIOS companion and
spent their time budget copying the toolchain; those are not passing evidence.

### Enforced save-slot isolation

Adversarial review found `save_compatibility = "isolated"` was previously parsed
without a runtime consumer. Framework `c91331ff67c8797a5c0a74332e019f143bdb0270`
now derives normal slot filenames and all sidecars from the installed verified
plan whenever a resolved package declares isolation. It retains the historical
paths for ordinary plans and leaves memory cards unchanged. Changing scope
cancels pending operations; invalid scope and truncated paths fail closed.
This is filename isolation, not state-header rejection of manually copied files
or explicit developer path/blob loads. Trusted title-profile construction does
not currently add settings packages to the ordinary resolved package list;
Final Bout has no such profile and uses the verified resource plan.

Both full worker/legacy mod-runtime suites and the assert-enabled save-state
policy fixture pass. The final README native rebuild passes with two jobs and
stages 357 overlay-toolchain files. Executable SHA-256:
`9ae81b2a2a772049cd690dcefa2c671120e924d23e5684bac1de80bef8296911`.

`build-audio-review/state-scope` performs two short cold runs with muted output
and the diagnostic 30-second watchdog allowance. FuniDub-on save/load reports
generations 1/2, both `last_ok = 1`, using a filename containing the full plan
hash. FuniDub-off cannot find an ordinary slot 1 (`last_ok = 0`), then saves it
successfully alongside the isolated slot (`last_ok = 1`). Both exit zero, and
personal settings/mod selections are restored byte-for-byte. These are early
game save-path checks, not another combat or default-performance campaign.

A 23.31-second converted-pack reel with ten combat/menu/victory examples is
open paused in VLC. Exact cue order, clock ratios, pack offsets and hashes are
retained under ignored `build-audio-review/final-reel`. It applies no extra
edits beyond the recipe. Owner review of this reel remains pending; prior donor
sample approval is not recorded as acceptance of the converted pack.

### Thirteen additional intact mappings

Bounded donor follow-up found shorter alternate-form recordings for eight
unmapped slots and complete Kid Boo exertions for five more. The current recipe
therefore covers 290/323 selected SPU candidates (159 combat, 89 menu, 42 victory),
with 33 selected menu/victory gaps. XA and unclassified audio remain original.
Vegeta's era, Trunks' sword variant, Frieza's full-power form and Boo's
cross-context substitutions are explicit; no new transcript or actor acceptance
is claimed.

Independent Sol 6.1 review rereads donor PVD/AFS tables and all thirteen payloads,
checks source hashes, nonrepeating terminal flags and exact-rational fit against
the original tables. All eight ADX additions retain their full declared PCM;
Boo trims only near-zero margins, with no excerpts. Existing 277 recipe records
and encoded cue bytes are unchanged. The final recipe SHA-256 is
`feb6c51c068f8b111d12f76599b88b33dd6731868adf173d2094265d5cef84d5`.

The native builder produces 14,563,328 bytes, SHA-256
`20af0a00107eec23d870da7848f7553826c61f364ca85a3f163aa2075942b428`.
Full-pack verification finds all 290 changed cues nonzero, unchanged original
flags and unmapped bytes, maximum decoded peak 26,898 and zero rail samples.
The eight Python parser checks still pass. The actual native provider prepares
and verifies all three updated overlays; evidence is
`analysis/audio-investigation-20261014/{build-pack-v2.log,pack-verification-v2.json,provider-v2-prepare.log}`.
Only catalog data/curation changed; the compiled executable remains `9ae81b2a`.
The updated catalog is staged beside it. The ten earlier audition examples
remain byte-identical; their 23-second reel still represents those current edits.
No additional game/netplay campaign was repeated for these bounded data edits.

## Extended FuniDub voice coverage (2026-10-15)

The current source-only recipe replaces 386/389 selected candidates: 159 ordinary
combat, 108 introductions, 54 battle wins, 17 tournament wins, two additional SPU
attack calls and 46 script-associated XA channels. Two tiny Kid Buu menu slots
retain originals; FINISH17 also retains its original because state 171 switches
to DEMOXA53 after 11 normal interpreter ticks. The nominal 22 VBlanks/~0.367 s
interval does not establish usable PCM time across asynchronous CD commands.
Seven unreferenced XA channels, shared/looping effects and unclassified audio
remain original. Explicit generic/form/context substitutions are in the recipe.

Independent Sol 6.1 discovery/review checked caller/pitch/table identities, all
source extents, intact added performances and age/form/context notes. The tracked
XA inventory reproduces 18 script tables, 54 stream identities and 29 DEMOXA event
associations directly from the disc. Offline local ASR supplies ignored research
hypotheses only, never shipped transcripts or synthesized speech.

Native codec tests and a real XA pilot pass. The pilot preserves 4,945 other
sectors and 143 selected-sector controls/reserved tails, agrees byte-for-byte
with FFmpeg and rejects wrong coding, oversized window, invalid insertion and
duplicate-channel recipes. Four complete original XA streams at both rates
match FFmpeg PCM. The updated builder reproduces the prior 290-cue pack exactly.
The final 386-cue pack is 72,184,832 bytes, SHA-256
`56be7a893f913efb193d4de694fec76af11c28df36bbd736418d3fa1a23eaa76`;
recipe SHA-256 is
`3d4f3a3a6018fe00a3bbc414281d2cb7b57e58001914fa981cd19ddd9c855acf`.
Full-pack verification finds every replacement changed/nonzero, unchanged
unmapped bytes and SPU flags, preserved XA controls/reserved bytes/EDC convention,
maximum decoded peak 26,898 and zero PCM rail samples. The native provider resolves
all eight overlays: cold preparation 10,281 ms; source-verified reuse 1,578 ms. These are
preparation measurements, not game loading improvements.

The README CLI two-job Windows release rebuild and 357-file native toolchain
stage pass; executable SHA-256 is
`6a97f23fcf0c27992c773936739199b8e32342ef35849a332f9f5ff4c054f1bf`.
The first bounded drive did not reach an attack cue before its deadline; it
closed without claiming XA coverage. The corrected muted natural-demo run
reaches a changed DEMOXA01 sector at LBA 23,890/channel 9/frame 6,622 and verifies all
2,048 inspected user bytes against the actual prepared pack, differing from the
stock disc (prefix SHA-256
`5cfc8c5692c25c377d1b208957f4c2cf5d7833044a1a5940c5989f5c002c4a4e`).
Native XA delivery events occur concurrently (file 1/channel 5), and the CD input
audio tap is active. This proves the raw-overlay read/delivery path, not an
audible semantic judgment or that the inspected interleaved channel was the
selected decoder channel. Save/load generations 1/2 complete with `last_ok=1` in
scope `77811b58ffba9ea7a8bb112a60d7855831c87f0f5c9640e231cc500ee2d67b0f`;
frames resume through 6,734 and the native report exits normally via TCP at 6,755,
with zero unsupported instructions, zero segment misses and no degraded compile.
The run uses the existing 30-second diagnostic watchdog allowance and generates
an automatic freeze diagnostic at frame 4,824; it does not close the separately
tracked stall issue or qualify default-watchdog performance. Demo GAME OVER
screens are not manual win/progression evidence.

Local evidence is under ignored `build-audio-review/extended/`. The 23-second
original/replacement comparison reel is open paused in VLC; owner listening is
pending. XA window classification, subtle synchronization and complete-game
coverage are not established by these byte checks. No broad netplay campaign or
HLE/loading work was repeated. Game processes exit; owner settings/mod selection
are restored, and the preexisting game.toml preference remains unstaged. No media,
transcripts, packs, saves or generated code are included in Git.

The final bounded shared-bank audit regenerates three tables and verifies 22
finite local WAV/ASR records. No confirmed omitted spoken announcer/menu cue
emerges; common combat waves 13/14 remain ambiguous vocal/effect candidates and
are preserved. The resident instrument bank's loops, varying pitches and music
callers support preserving it. Negative ASR does not prove speech absence;
menu instrument 3's reference decode does not establish native pitch. Receipt:
`build-audio-review/local-asr/shared-audit/scope-audit.json`, SHA-256
`c554f7d69578192e2dee0ff925d2afe561b160a7626b6340c13edacb843cf70f`.

### Owner feedback refinements, 2026-10-15

The owner accepts the in-game combat grunts/effects. Sound-test 000/001 and
002/003 repeated because distinct CHARSEL slots reused the same donors, not
because the original selector aliases them. The updated recipe changes only
five intros: Goku variants 0/1 use US2 49180/49187; Pan variant 0 uses 55174 while
variant 1 retains 55175; Piccolo variants 1/6 use 51187/51183. Piccolo variant 1
now has 2.249 seconds of speech against the original 2.313, replacing 1.155.
Variant 6 improves to 3.159 against 5.509; its remaining mouth-animation gap is
explicit. All are intact performances, without word cuts or time stretching.
New donor wording is an offline-ASR hypothesis awaiting listening/context review.

Native preparation and full verification pass for the 72,184,832-byte pack,
SHA-256 `1cc22741f158c096bac7173bbbc4cfeae9dafee829de8044d4879143473330f1`.
All 381 other cue records and all pack bytes outside the five intro extents
remain identical. SPU flags, three retained-original gaps and XA data are
unchanged; no PCM rail samples occur. Independent Sol 6.1 review verifies the
source hashes, exact integer fits and form/context qualifications. Evidence:
`build-audio-review/menu-refine/` and the local source-discovery reports.
The actual launcher media provider also prepares/verifies all eight overlays
for the new recipe, fingerprint
`5b68cbfb8d2bb4ede09ae5ee3b96a844dfe23092fecf9ce1265852f6b33efe19`.

The red-sky/teal-floor KO/result rectangle is a separate title-side widescreen
bug: stage 5 disables its panorama and the old fixed-address gradient recognizer
misses the pair after pause/result packets shift it in the buffer. The existing
archived `city-21-9` GAME OVER capture reproduces the report. No shared engine
change or dependency bump is needed. Exact submitted-pair recognition passes an
independent native fixture against eleven archived RAM images/thirty pairs,
including malformed and stale-list rejection and 4:3 identity.

Native Windows CLI rebuild and overlay-toolchain staging pass with two jobs.
The final 9.25-second muted hidden-presenter replay loads the affected result save
with completion receipts and captures 16:9/21:9/4:3. Sky/floor fill the wide frame;
4:3 returns to mode zero. At 21:9 there are 344 background hits, zero rejected,
stale or mismatched background tags. Normal TCP exit is frame 556, zero
unsupported instructions or degraded compilation. Executable SHA-256:
`8ae9ac2740782413ab153d11f4fcc179797c80579b5ae1510f757ce585b1cef4`.
Evidence: `build-audio-review/effects-stage5/`. The rendering replay disables
FuniDub to use the ordinary original-audio save and restores owner settings/mod
selection byte-for-byte. It is result-rendering evidence, not manual progression
or revised-intro listening acceptance. Broader rendering qualification and the
earlier rare overlap remain open. Loading work stays parked.

### FuniDub startup-cache correction, 2026-10-15

The owner reported long repeated audio preparation. The pack was already cached,
but Windows' deliberately unqualified file identities forced a miss in the fast
probe, and the warm provider revalidated all source payloads on every commit.
That repeatedly read the owner's BT3 ISO over SMB. The provider now identifies
the cache using only local recipe/manifest data, verifies its receipt plus exact
pack size/SHA-256, and reuses it without opening/resolving source images. Missing,
corrupt or outdated packs retain the original fully verified build/repair path.
Changing an ISO selection does not claim to validate that new source when the
existing fixed pack is reused. No audio bytes, recipes, overlays, content
fingerprints, framework/UI pins or Windows identity guarantees change.

The actual pinned package-manager/provider helper measures 6.093 seconds before
and 1.109 seconds afterward for warm preparation plus eight-overlay resolution;
the new cache probe plus resolution takes 0.688 seconds. All yield the unchanged
FuniDub fingerprint
`5b68cbfb8d2bb4ede09ae5ee3b96a844dfe23092fecf9ce1265852f6b33efe19`.
This is a local sample, not a general end-to-end launch-time guarantee.

The native provider regression covers initial preparation, warm probe/preparation
with both sources removed and no builder/disc-resolver call, same-size corruption
with restored write time, failed offline repair, successful repair and recipe
invalidation. The portable `check_audio` target passes it and the existing codec
checks. Independent Sol 6.1 review finds no blocker. The two-job CLI release
rebuild and toolchain staging also pass.

A muted hidden-presenter startup temporarily points the persisted BT3 selection
at an absent local ISO. It still reaches frame 302, with the actual provider
reporting 210,568 microseconds, then exits normally via TCP at frame 303 with
zero unsupported instructions/degraded compilation. Owner settings and source
selection are restored byte-for-byte. Executable SHA-256:
`c72851e25d0a13574ff07fac610aaa41b3bda987bc295777812161a8b1ea0bc7`.
Evidence is under ignored `build-audio-review/cache-startup/`. This is startup
cache validation, not another combat/audio audition or a loading-HLE campaign.

The pinned Windows framework still cannot issue metadata-only readiness tickets,
so normal disc/resource/overlay verification can queue a brief preparation panel
on automatic preparation, Play and runtime handoff. This fix removes repeated
source-media verification; it does not claim to eliminate that panel entirely.
