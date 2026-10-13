# Project requirements

This is the acceptance contract for Final Bout's requested features. Progress
and dependencies belong in central Beads under `beads-6058`; this document is
not a second issue tracker.

| Work | Owning issue | Required evidence |
| --- | --- | --- |
| Initial project | `beads-jsz8` | Real disc identity, pinned dependencies, safe asset ignores, reproducible setup and honest validation record |
| Original gameplay | `beads-2x2x` | Cold boot, menus, selection, local versus, representative fights, audio/FMV, save/load |
| Internal resolution | `beads-rxvr` | Native/1080p/4K comparisons, effective scale telemetry, correct text/effects and acceptable pacing |
| Loading HLE and precache | `beads-aubo` | Verified caches and guarded adapters, differential correctness, measured cold/warm gains |
| Adaptive widescreen | `beads-q6ao` | Wider world visibility, correct culling/capacity/HUD/FMVs, live resize and return to 4:3 |
| Two-player recomp-net | `beads-1q31` | Independent peer input, rollback/digests, identity mismatch rejection, load/rematch and online checks |
| Original dialogue extraction | `beads-bqsp` | Complete cue inventory, reproducible local extraction, trigger and speaker mapping |
| Recorded-clip replacement | `beads-vbfi` | Owner-reviewed matching, source/edit provenance, reversible pack, audio and netplay validation |

The last two phases are ordered after all core features: extraction first,
replacement last. The owner supplied a BT3 USA PS2 ISO on 2026-10-13 and
reaffirmed core validation first. The optional final feature is **FuniDub**:
the launcher prepares a local replacement pack automatically from that ISO
using a reviewed mapping. See [the launcher contract](VOICE_REPLACEMENT.md#funidub-launcher-contract)
and [metadata/source audit](FUNIDUB_RESEARCH.md). Audio extraction remains deferred.

## Resolution and adaptive view

Use the shared renderer's `internal_resolution` presets. A larger window or
output image alone does not prove increased internal 3D resolution. Record both
requested and effective renderer scale, driver caps, frame pacing, and audio.

Adaptive widescreen must reveal more world geometry while keeping menus, text,
portraits, timer, grouped scores, health gauges and movies properly composed.
Exercise 4:3, 16:9, 21:9, narrow windows, live resizing and return to 4:3.
Document the supported aspect range. Account for actor/packet/draw-buffer
capacity before admitting more visible geometry; do not simply disable culling.
A generic stretch mode is not completion.

Toshinden's final ordering-table and panorama hooks are examples of the method,
not reusable Final Bout addresses. Reference its
`src/mods/toshinden_widescreen_plugin.c`,
`src/mods/toshinden_widescreen_backdrop.c`, and validation records.

## Loading

Separate host preparation from guest loader acceleration.

A host cache should return the exact verified bytes, including active disc
patches, while preserving guest-visible deadlines and CD state. Cache keys
must include source identity and content/mod plan. Test cold, warm, stale,
corrupt, missing and interrupted preparation. Publish cache files atomically.
The current framework has no general precache configuration switch.

Title HLE needs mapped reader, decompressor, scheduler, completion, destination,
sound-transfer and overlay boundaries. Guard known callers and code/layout;
retain original behavior for unknown cases and invalidate regenerated code
when guest executable memory changes. Preserve current match/gameplay state,
not a cached post-load snapshot. Keep speech, music and movies streaming until
their paths have separate evidence.

Tomba 2 references:
`src/mods/tomba2_seamless_prepare.cpp`,
`src/mods/tomba2_seamless.c`,
`docs/SEAMLESS_LOADING_SPIKE.md`, and `docs/PARITY_HLE.md`.
The shared `psx_mod_read_disc_file()` API reads mounted content without
advancing guest CD state. It is a building block, not a finished cache/HLE path.

Measure the same routes before and after: boot to menu, fighter/stage load,
retry/rematch, and transitions. Record hardware, disc location, cache state,
elapsed times, original-MIPS comparison results, and remaining bottlenecks.

## Netplay and state

Use the pinned shared recomp-net integration and two ordinary player ports
unless actual game evidence requires otherwise. A compiled lobby is not a
validated multiplayer session.

Match executable/build, disc identity/geometry, session BIOS, deterministic
options and verified mod/resource plan. The shared software GPU at native
resolution owns guest VRAM/GPUREAD/snapshots/digests; a high-resolution OpenGL
view can be presentation-only. Guest culling and loader adapters still need
deterministic policy independent of peer window size, cache readiness, disk
speed or unsnapshotted host state.

Prepare required resources before joining. Test save-state restoration and
hook rebinding. Compare core, GPU, SPU, MDEC, DMA, SIO and CD digest partitions
through forced prediction and rollback, including loads, rematches, movie
transitions, unequal local rendering scales and cache states. Validate content
mismatch rejection and restoration of offline settings.

Resource-mod support varies by framework version. Inspect the pinned
`runtime/src/mod_runtime.cpp` content-negotiation and verification paths before
qualifying the later voice pack. Preserve guest audio timing and suppress
duplicate presentation on resimulation.
