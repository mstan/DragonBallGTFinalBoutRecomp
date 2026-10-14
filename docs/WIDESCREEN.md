# Final Bout widescreen preview

Status: default-disabled **0.1.0 preview**, awaiting full culling, scene and HUD
qualification. Tracking: `beads-q6ao`, [GitHub #2](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/2).
The owner accepted a quick visible clouds/HUD/motion review on 2026-10-14;
broader compatibility claims remain outside that acceptance.

## Implementation and evidence

The mod selects native-wide presentation at 16:9 or adaptive window aspect,
currently capped at 21:9. The GTE activity detector identifies 3D frames. The
mod does not change guest GTE projection, packets, RAM or timing. No guest
culling predicate has been widened.

A generated function-entry hook at static PsyQ DMA submit `0x80028D80` walks
the submitted list with alignment, RAM bounds, packet-size and iteration
limits. `game.toml` opts this function into generated hook dispatch. The package
explicitly selects both its activation plugin and its packet hook.

Combat packet identity is guarded by 512-pixel display width and four exact
instructions in the observed combat overlay. Only qualified packet types at
known title addresses are offered to the renderer, whose tags additionally
check full command contents and freshness. The guards are independent of the
selected fighter and do not rely on a stale overlay address alone.

- HUD base `0x80072A14`, two banks of `0x30C` bytes. The call at `0x80054018`
  initializes the first bank; `0x80054020..68` copies it into the second.
  `0x80054754..68` selects the active bank using scratchpad buffer index.
- VS and PAUSE sprite roles are centred. Other sprites and health/energy G4s
  anchor by their signed combat X coordinate (draw offset is +256). Hidden
  fields at X=512 stay beyond the right reveal. Dynamic fields require broader
  gameplay review before this classification is considered complete.
- Sky/floor G4 pairs at `0x801D0000/24` and `0x801D3000/24` are stretched in the
  renderer. The hook verifies full authored width (-256..256), opaque G4 type,
  packet length, and equal left/right colours. It does not stretch arbitrary
  polygons in those pools.

The native-wide route was chosen after direct comparison with projection
squash. Untagged squash stretched the HUD; native-wide revealed the world but
left the authored gradients narrow. Explicit tags address those measured
problems without copying another game's addresses or cull constants.

## Checkpoint validation and limitations

`build-release/widescreen-preview-20261013` uses the native release build, a
hidden full presenter, a Goku/Frieza combat save, and temporary adaptive mod
selection. Resizing 960x720 -> 1280x720 -> 1680x720 -> 960x720 reports reveal
widths 0 -> 170 -> 384 -> 0. Composed `present_shot` captures, rather than
pre-present high-resolution captures, verify aspect and HUD placement. The
16:9 sample has 7,257 HUD tag hits and 512 background hits, with no rejected,
stale or guard-mismatched tags. The runtime exits normally via TCP at frame
1,904, zero unsupported instructions, in 31.3 seconds.

The 21:9 capture lands on a white scene with visible fighters/HUD. The stage
has animated flashes, but this sample alone cannot establish whether it is
normal. Record a sequence and compare before claiming full 21:9 visuals pass.
The test also does not establish complete pause/result glyph coverage, culling,
all stages/characters, menu/movie transitions, or renderer/backend support.
Those are explicit follow-ups, not waived requirements.

Executable SHA-256:
`a334c592ee6be2dc54e2e68d347e284f84e21e1c36c865673e499518b5febcac`.
The temporary mod state was restored byte-for-byte. The elective feature remains
disabled by default; the CD correctness fix remains enabled by default.

Earlier local profile directories are `widescreen-profile-20261013` (RAM,
primitive census, DMA history, disassembly) and `widescreen-diagnostic-20261013`
(composed comparison of native-wide and squash). Their media stays out of Git.

## Resumed investigation, 2026-10-14

The white scene is a stage flash, rather than a demonstrated widescreen defect.
In `build-release/widescreen-sequence-diagnostic-20261014`, mod-off 4:3 frame
sequence image `07` shows the same white background with fighters/HUD preserved
as adaptive 21:9 image `08`. Both then fade through gray and return to the rocky
stage. This comparison uses the original framing path in the same recomp build;
it is not an independent hardware/emulator fidelity comparison.

The two serial runs use the checkpoint executable above, fixed effective 5x
resolution, hidden full presentation, dummy audio and composed captures with
completion receipts. They exit through `tcp_quit`, with zero unsupported
instructions, at frames 1,331 and 2,355 (22.0 and 38.6 seconds). The diagnostic
sets `PSX_DEBUG_TOGGLES=0`, `PSX_DYNRES=0` and a 60-second starvation threshold.
It is visual evidence, not default-runtime stability or audible-audio acceptance.
Two earlier capture attempts hit the default watchdog; they remain recorded in
the validation notes and shared observation issue, without an assigned cause.

Adaptive 4:3/16:9/21:9/4:3 sequences show covered backgrounds, edge HUD placement,
and return to mode zero. No stale, rejected or mismatched tags were reported.
Each size restores the same slot before sampling, so this establishes
resize-plus-restore behavior, not uninterrupted live-resize compatibility.
Animation timing differs between samples; pixel identity is not established.

### Culling boundaries independently checked

Two independent offline audits of the captured combat overlay agree that
`0x8004020C` dispatches model primitive groups to builders in
`0x800402D4..0x80041B84`. The 18 builders reject nonpositive NCLIP MAC0 and
advance preassigned packet storage even on rejection (for example, `+0x58`
at `0x800403EC`, and `+0x98` at `0x80041B74`). No horizontal extent predicate
was found inside that interval. This does not exclude object admission or
other effect/render paths, and it is not a reason to disable backface culling.

The apparent `abs(projected X) > 256` checks at `0x8006DD18/40` also control
player flags and orientation/action state. Widening them based on local window
aspect would change gameplay. They are not qualified rendering hooks.

Ordering-table descriptors at `0x800A9E08/30/58/80/A8/D8` describe
2,048/64/1,024/1,024/4/4 depth buckets, respectively. Multiple primitives share
a bucket; these counts do not prove packet capacity. The 480 records beginning
at `0x8007329C`, stride `0x30`, are paired packet storage, not a proven actor
limit. Guest admission remains unchanged pending an actual rendering defect
and a complete capacity argument.

### Scrolling cloud composite fix

The green Goku/Goku demo stage exposed a real gap: its tiled cloud strip stayed
inside the authored width while the surrounding scene widened. Its panorama
object at `0x800A9BDC` points to a 32-column by four-row map of 32-pixel tiles
at `0x800A9C00`; the producer draws a scrolling 512x128 slice of that source.
Repeating the visible slice would incorrectly repeat half the panorama.

The title hook now validates the producer instructions, object/map layout,
actual texture atlas, four continuous rows spanning -256..256, exact opaque
sprite commands, dimensions and DMA links. Up to 72 cloud primitives plus the adjacent
G4 must match before any are tagged. The pool walk is bounded to its 0x3000-byte
bank. Earlier effects can shift the composite, so fixed pool-base identity is
insufficient: the sampled sky starts at `0x801D3078` and its gradient at
`0x801D36D8`, after five excluded effect packets.

Framework commit `d9f0964d5c0cb981eeb206dff2c92f683741c3d6` narrowly extends
the existing background service to opaque variable textured rectangles
(0x64/65). Full-command/address/freshness guards and canonical rendering remain
intact. Only the native-wide mirror stretches the qualified composite. The
title does not change guest RAM, GTE, timing, culling or object admission.
The shared extension is [PR #663](https://github.com/RetroPortingToolKit/psxrecomp/pull/663).
After CD PR #657 merged, the same patch was rebased onto master `d3db61b1` as
`a36754b7`. Its review diff contains only the sprite extension, API documentation
and tests. The focused renderer tests and a short Final Bout replay pass on
the updated base; no further visual campaign was requested. PR #663 merged as
`f9c287f523428aea816fb91cd4ec7d499dcdea8a`; the merged source tree exactly
matches the tested rebased head, and Final Bout now pins the landed revision.

The short composed-capture replay in `build-release/sky-fix-20261014` verifies
cloud coverage at 16:9/21:9 and identity at 4:3, then resumes the demo briefly.
It exits normally in 25.05 seconds at frame 1,530, zero unsupported instructions,
with the default watchdog. The owner subsequently accepted the visible review.
See [validation](../validation/README.md#cloud-backdrop-fix-and-human-acceptance-2026-10-14)
for the executable hash, counters and exact acceptance limits.

### Moving-camera parity fix

The owner's subsequent Trunks/Goku captures exposed alternating full-width and
authored-width clouds. The earlier paused/brief motion smoke did not establish
continuous background coverage. A targeted moving Goku/Goku replay reproduces
the same gap, including five of twelve composed captures.

The producer at `0x8002101C..0x80021188` uses an opaque, one-pixel FT4 strip at
the start of each row when horizontal source scroll is odd, then draws the
even-aligned sprites. The old sprite-only guard rejected these legitimate
mixed layouts. Aligned, cropped-even and cropped-odd composites contain
64/68/72 cloud primitives; an odd crop of 31 leaves the first edge with no
first sprite. The hook now validates each producer-defined layout, exact map
order, atlas/UV/page data, geometry and links before tagging the whole composite.
The unused high halves of FT4 UV2/UV3 are padding, not identity fields.

PsyQ can queue the DMA callback (`0x80029090` enqueue, `0x80029254` callback).
The completed packets can therefore refer to an earlier source scroll than the
current object. The hook derives at most 32 possible origins from serialized
UVs and the fixed map, then proves all four rows and the adjacent gradient.
Candidate failure leaves no tags. It does not cache or alter guest state.
The existing instruction/object/vertical-layout, RAM/bank and packet guards
remain; guest culling is unchanged. This is a title fix using the landed renderer
service, with no shared engine change.

The final short camera replay shows covered clouds in all twelve composed
captures, including odd scroll positions, and returns to 4:3 mode zero. The
independent Sol 6.1 review found no remaining blocker. See the validation record
for the exact run and hash. Broader stage/culling qualification is still separate.

### Stage layout coverage

The owner's subsequent Goku/L.Goku blue-city capture is stage 6. The earlier
four-row cloud guard could not recognize its eleven-row panorama. A separate
stage 4 capture also exposed a valid panorama with no following G4. These are
different authored layouts, beyond the earlier green-stage parity repair.

The stage descriptor table at `0x800545CC`, stride 20, identifies eleven HAIKEI
resource groups. Independently decoding the supplied disc with the game's
`0x8001663C` decoder establishes these layouts; the decoded stage 2 map/atlas
matches captured combat RAM byte for byte. All tiles are 32x32 and every map
index fits its own atlas. Dimensions below describe the source map; the game
draws a scrolling 512-pixel-wide slice.

| Stage ID | Map columns x rows | Atlas entries | Following G4s |
| --- | --- | --- | --- |
| 0 | 32x3 | 48 | 1 |
| 1 | 32x6 | 96 | 0 |
| 2 | 32x4 | 128 | 1 |
| 3 | 16x2 | 2 | 1 |
| 4 | 32x11 | 96 | 0 |
| 5 | 16x2 | 2 | 2 |
| 6 | 24x11 | 112 | 1 |
| 7 | 24x11 | 112 | 1 |
| 8 | 32x3 | 48 | 1 |
| 9 | 32x7 | 96 | 0 |
| 10 | 32x2 | 36 | 3 |

The hook matches each exact stage's resource headers, object dimensions,
origin/scale/pointers and actual atlas count. It proves the complete panorama
and the stage's expected G4 suffix before tagging. Stages 1/4/9 legitimately
have no G4 suffix; adjacent effect packets remain excluded. Stage 3 uses its
verified alternate ordering-table terminal. Stage 5 disables the panorama in
the initializer and stays excluded; its original gradient handling remains.
Submitted packet Y now supplies the vertical origin, just as serialized UVs
supply source X, so queued camera updates cannot invalidate a completed packet.

The largest panorama has 198 primitives and occupies 4,928 bytes. Even adding
the maximum three G4s gives 5,036 bytes, below the existing 12,288-byte bank.
This is recognition of existing guest packets, not wider guest admission or a
packet-buffer expansion. No shared engine, guest RAM/GTE or culling change.

Independent Sol 6.1 review executed the actual captured MIPS initializer and
panorama producer against all eleven assets, both banks and four scroll crops:
88 serialized layouts match the audit, including odd strips and wraparound.
Boundary checks and seventeen malformed cases pass. This is offline packet
coverage, not eleven live stage visits.

The rebuilt native hook was exercised on stages 1/2/4/5, with composed captures
at 16:9/21:9 and a return to 4:3. Green and the tall gradient-free panorama cover
the displayed width; the disabled-panorama stage retains gradient coverage.
Legacy city snapshots restore to a title/selection screen with leftover combat
RAM and cannot establish a live city pass. A bounded attempt to select a city
fixture instead reached stages 1/5; its filenames do not establish stage identity.
The owner's quick city visual check is pending. Other stage visits, terrain
culling at the reveal edges and broader gameplay remain unqualified. Recomp-ui
is reopened for that check; see validation for the exact evidence and hash.
