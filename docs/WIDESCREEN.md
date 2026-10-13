# Final Bout widescreen preview

Status: default-disabled **0.1.0 preview**, awaiting full culling, scene and HUD
qualification. Tracking: `beads-q6ao`, [GitHub #2](https://github.com/mstan/DragonBallGTFinalBoutRecomp/issues/2).

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
