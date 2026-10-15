# FuniDub

FuniDub prepares recorded BT3 English voices locally from the user's USA
Budokai Tenkaichi 3 ISO. No audio is downloaded or distributed, and no voices
are generated or cloned. Both supplied game images remain unchanged.

## Use

Enable **Audio / FuniDub** in the launcher's Mods page and choose the supported
BT3 USA ISO. Preparation reports progress and supports cancellation. A verified
pack is reused; missing or corrupt content is rebuilt. Disable FuniDub to restore
original recordings. It uses separate save slots because samples enter guest
SPU memory. Disabling it returns to ordinary slots; memory cards remain shared.
There is no automatic save-state import between these slots.

## Coverage

The recipe replaces **386 of 389 selected voice candidates**:

| Original group | Replaced |
| --- | ---: |
| Ordinary combat sounds | 159 |
| Character introductions | 108 |
| Battle victory cues | 54 |
| Tournament victory cues | 17 |
| Additional SPU attack calls | 2 |
| Script-associated XA attack channels | 46 |

Three selected cues retain original audio:

| Cue | Reason |
| --- | --- |
| Kid Buu menu variants 2 and 4 | The 168/214 ms slots cannot hold a suitable complete same-form attack recording. Pain sounds were excluded. |
| FINISH channel 17, Baby meteor sequence | The game switches streams after 11 interpreter ticks; asynchronous CD start latency leaves its usable audio budget unqualified. |

Seven other XA channels have no recovered character-script association and
retain originals. Looping/shared effects, unclassified sounds and movie/music
assets also remain original. This denominator describes selected candidates,
not a claim that every sound or performer in the game has been audited.

The owner permits suitable generic introductions, victory lines and grunts.
These mappings are context substitutions, not literal translations. Named calls
are used where source evidence supports them; uncertain attacks use complete
generic attack phrases or exertions. Some short menu/victory slots also use
physical attack recordings. Each such choice records its original event
category and changed context. Adult GT Goku uses BT3 Goku (End); GT child Super
Saiyan Goku's silent short bank uses GT base child Goku recordings. Other
era/form substitutions are explicit in the recipe. No adult Goku voice is
silently assigned to child Goku.

## Preparation and validation

The portable native builder checks the original resource hashes, donor PVD/AFS
tables and every used payload. Integer decoding/resampling preserves exact SPU
pitch and XA sample rates. Gains, sample trims and fades are recorded. Spoken
candidates are intact phrases; ordinary combat exertions can use recorded
excerpts. No recording is time-stretched to fill a slot.

XA preparation retains full physical files and channel interleaving. It
preserves sector controls, filter identities, reserved bytes and the original
EDC convention, and re-encodes each selected channel with continuous predictor
history. Donor capacity excludes the original 30–35 seconds of zero tail.
Calls start at the beginning of their replacement window; native CD seek,
stop, cancellation and stream-switch commands remain unchanged. This does not
establish perfect animation sync or prove the overwritten audio contains no
embedded effects; short listening review remains appropriate.

The current pack is 72,184,832 bytes, SHA-256
`56be7a893f913efb193d4de694fec76af11c28df36bbd736418d3fa1a23eaa76`.
Full-pack checks find all 386 replacements nonzero, unchanged unmapped bytes,
unchanged SPU flags and XA controls/reserved bytes, valid present EDCs and no
PCM rail samples. Native XA decoding matches FFmpeg 7.1 byte for byte on four
whole original streams at both supported rates. The extended builder still
produces the prior 290-cue pack byte for byte. Independent review checked
source categories, form/age substitutions, exact fit and native timing; it
caught the short Baby stream-switch exception above.

The prior native launcher checks cover source selection, progress/Cancel,
closing during preparation and corrupt-cache repair. A representative muted
Goku/Buu combat run verifies replacement bytes in SPU RAM and save/load. That
run used a 30-second diagnostic watchdog allowance: both mod-on and mod-off
default-watchdog routes stalled, separately tracked in issue #7. A brief
two-peer gate admits matching packs and rejects different selections at frame
zero. Isolated save slots and return to ordinary slots also pass. Those checks
precede the expanded XA recipe. The expanded release build also passes a muted
natural-demo check: 2,048 bytes from a replaced XA sector match the prepared
pack, native XA deliveries occur, and save/load followed by resumed frames
succeeds. It exits normally with zero unsupported instructions or segment
misses. The diagnostic watchdog allowance and a generated freeze diagnostic
remain qualification limits; this is not a stall fix. Detailed evidence is in
`validation/README.md`. The owner's earlier donor reel approval does not
establish acceptance of every mapping. High-level listening remains open.

The framework installs eight immutable resource-backed overlays after checking
the exact disc identity and stock ranges. Prepared bytes participate in the
normal content fingerprint. No runtime voice hook, host-only playback or donor
path enters gameplay. Online use requires verified content-plan negotiation.

Windows timestamp-only identities are deliberately unqualified after rapid
rewrite collisions were reproduced. Cached preparation verifies the pack and
all selected source payloads there. This is preparation caching, not faster
game CD loading; HLE/precaching remains parked.

## Reproduction

Developer tools under `tools/audio/` reproduce inventory and curation. Generate
the original inventory with `inventory_original.py`, donor inventory/curation
with `inventory_donor.py` and `curate_donor.py`, and disc-only script/channel
metadata with `inventory_xa.py`. Run `curate_recipe.py` for the ordinary SPU
base, then `extend_recipe.py` with `extended_mappings.json` for tournament,
additional SPU and XA candidates. Its `--codec-check` argument takes the native
`codec_check` developer driver. `build_pack` prepares the pack; `verify_pack.py`
checks every declared replacement and all remaining bytes without playback.
Use `--help` for each Python tool's exact arguments. The end-user launcher
requires neither Python, FFmpeg nor speech recognition.

The standalone native developer tools have a CMake entry point:

```text
cmake -S tools/audio -B build-audio-tools -DCMAKE_BUILD_TYPE=Release
cmake --build build-audio-tools --parallel 2
cmake --build build-audio-tools --target check_audio --parallel 2
```

On Windows, invoke the explicit native toolchain executables as described in
the main README. Recipe format 2 adds `disc_raw` files and `xa_mono` targets;
XA records bind file/channel/coding/count/hash and a bounded sample window.
Optional insertion offsets must fit that window, including the entire resampled
recording. The bundled recipe uses start alignment. Builder version 3 separates
its verified cache identity from earlier preparations.

Only recipes, source hashes and code ship. Local audio, transcripts, inventories,
packs, receipts and audition reels remain in ignored analysis/build directories.
See `VOICE_ORIGINAL_TABLES.md` and `VOICE_DONOR_TABLES.md` for source evidence.
