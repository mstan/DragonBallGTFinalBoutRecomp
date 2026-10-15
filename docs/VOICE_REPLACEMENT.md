# Recorded dialogue replacement

This is the design contract for FuniDub. The owner resumed audio-replacement
investigation on 2026-10-14 after the visible widescreen review. Original cue
inventory (`beads-bqsp`) precedes curated donor mapping and recorded-clip
replacement (`beads-vbfi`). Loading enhancements remain parked. The first local
extraction/decode results and their limits are in [the investigation](AUDIO_INVESTIGATION.md);
the original investigation is retained as historical evidence. The native
builder now produces a verified local pack from a source-only recipe. Launcher
integration works locally; see [FuniDub](FUNIDUB.md) for current coverage and
remaining listening/compatibility limits.

The requested direction is a Funimation-cast performance assembled from existing
recordings, for example Sean Schemmel and Chris Sabat. No voice cloning,
generated dialogue or synthesized performances are part of the project.
The owner has supplied a Budokai Tenkaichi 3 USA PS2 ISO as the preferred first
donor. TV media remains a possible later source if measured coverage gaps need
it. See the [FuniDub research audit](FUNIDUB_RESEARCH.md).

## First: inventory the supplied game

Inspect this exact USA disc before making claims about its language, dub or
cast. Menu announcements, in-fight lines, character calls, attack shouts,
grunts, results and any relevant movie dialogue may use different storage
paths or performers. The owner's recollection is a research lead, not an
asset classification.

Extract originals locally and preserve them unchanged. Each cue needs a stable
ID and the following metadata:

- Disc/executable identity; archive/file/stream/channel and original offset;
  source hash, codec, sample rate, channels, duration and loop behavior.
- Character/speaker confidence, language, transcript/translation confidence,
  menu/fight/context and runtime trigger.
- Concurrency, cancellation, interrupt/loop behavior and any gameplay
  dependency on completion; ambiguous, shared, duplicate and missing cues.
- Extractor version/command and a playback spot-check result.

Map aliases and reused samples before deciding the number of replacement lines.
Silence, music and effects should not be classified as dialogue merely because
they share a bank. Keep all ripped audio in ignored local storage.

## Then: find existing performances

Use subtitles and transcripts to find candidate scenes, followed by listening.
Subtitles do not establish speaker, dub version, word boundaries, or whether a
clean spoken track exists. Preserve source release/dub/cast identity so clips
from different performances are not silently mixed.

For every candidate and final excerpt retain source media hash, episode/game
and release identifier, source timecodes/sample boundaries, transcript,
character/performer, background music/effect contamination, intended target
cue and rationale. Record all edits as a reproducible recipe.

Prefer intact phrases where practical. Non-generative trimming, fades, joins,
gain/loudness matching and conventional cleanup can support editing. Never
invent missing words or performances with generated voices. Artistic liberties
should be visible in the mapping and reviewed by the owner. Where no suitable
clip exists, keep the original cue and mark the gap.

The owner permits suitable generic BT3 introductions and combat grunts rather
than requiring literal 1:1 wording for every cue. Record these as substitutions
with their target context and semantic fit. The expected small voice inventory
is a lead to confirm during extraction, not a coverage claim.

## Delivery and checks

Use an optional reversible resource pack with original-audio fallback; do not
overwrite the only original asset. Keep downloaded/supplied recordings, private
subtitles, extracted clips and built packs outside Git. Source/config and
provenance recipes can be versioned without redistributing the recordings.

Validate coverage in menus and actual fights; audition edits for intelligibility,
clipping, abrupt changes, background contamination and consistent loudness.
Preserve interruptions, timing, channels and completion behavior. A longer clip
must not delay a gameplay event. Test repeated attacks, overlapping speakers,
pause, scene transitions, save/load and rollback without duplicated playback.

Confirm the pinned netplay resource-plan rules and content matching. Do not
assume a working offline voice pack is safe online. Record unavailable source
media and unmatched cues honestly rather than substituting generated speech.

## FuniDub launcher contract

Owner direction, 2026-10-13: the optional feature is named **FuniDub**. Once
the base game is set up, the user chooses their supported Budokai Tenkaichi 3
ISO and the launcher performs extraction, conversion and mapping locally.
The owner reaffirmed core gameplay validation before audio implementation.
The native implementation follows this flow; UI/game validation remains open.

1. Select **FuniDub** and choose the BT3 ISO. Validate supported release and
   content fingerprints before starting; a filename or serial alone is
   insufficient. Explain unsupported/mismatched media in plain language.
2. Show preparation progress and cancellation. Read the original media without
   modifying it. Use a staged local cache; resume only previously verified
   outputs and publish the pack atomically after validation.
3. Extract the entries required by the reviewed recipe, decode and apply its
   recorded trims/fades/gain/resampling, then bind outputs to verified Final
   Bout cues. End users do not perform the research/matching step and do not
   need online speech lookup, external archive editors or manual clip assembly.
4. Show readiness and any uncovered cues. Keep original audio for documented
   gaps. Do not report full coverage when it is partial. A failed preparation
   preserves the last working pack and original playback.
5. Enable or disable FuniDub reversibly in the launcher. Cache keys include
   target/donor fingerprints, mapping and builder/decoder versions. Changing
   the recipe or input invalidates affected outputs; missing/corrupt files
   trigger repair or original fallback rather than broken playback.

Before implementing this flow, developers must complete both inventories and
curate the map. Give donor assets stable archive/index/subentry identifiers and
hashes independent of community filenames. Preserve language, speaker/form,
actor verification, transcript, semantic fit, duration, contamination and
review status. Map each target event to source entries and sample-based edit
recipes; distinguish exact matches, approved substitutions, nonverbal sounds,
intentional omissions and gaps. No generated or cloned voices fill gaps.

Support both long dialogue and the short combat-sound path after verifying
their actual formats. The BT3 roster/name list alone does not prove every
Final Bout cue or period-specific performance is available. First measure
single-ISO coverage before requesting other media.

Choose reinjection after tracing real Final Bout playback. Evaluate a guarded
guest resource replacement or host presentation hook against timing, original
voice suppression, mixing and cancellation; do not assume a universal WAV
override exists. Preserve guest completion semantics and memory/state behavior.
Never rewrite either supplied ISO as the normal launcher workflow.

Validation must cover interrupted preparation, changed donor, corrupt cache,
mapping-version changes, no pack, partial coverage and uninstall; then actual
menu/intro/attack/victory playback, overlapping voices, pause/transitions and
save/load. A menu label or successful decode is insufficient. Qualify rollback
and content negotiation before enabling online use: host-only playback must
not duplicate on resimulation, while guest resource changes need the shared
runtime's deterministic content matching.

Ship extraction code and curated recipes, with appropriate source attribution.
Donor recordings, original recordings and built packs remain local and ignored.

## Owner-provided research leads

Added during setup on 2026-10-12:

- [ByFTR's Brazilian translation/redub](https://www.romhacking.net.br/index.php?topic=2166.0)
  reports episode-sourced replacement for pre-fight dialogue, cinematic specials,
  victories and tournament completion. Close-range specials and other sounds
  were excluded. Its target is SLUS_004.93 with CRC32 `24433280`, matching this
  disc. Listed tools include dbgt-tool, MummGGTool, strVagEditor, MFAudio, PSound
  and Audacity. Credits identify Denim for compression/ASM and Mumm-Ra for audio
  tooling. This is a useful inventory/format lead, not proof of full coverage.
- [NovaPowers' Final Bout recomp](https://github.com/novapowers0/DB-Final-Bout-Recomp)
  is a lead for existing Ghidra analysis, symbols, discovery tools and prior
  runtime investigations. Inspect the actual artifacts and their revision
  before importing any labels or drawing audio-format conclusions.

See [REFERENCE_NOTES.md](REFERENCE_NOTES.md) for the pinned Nova research audit,
overlay/profile leads and script defects to account for before reuse.

At the extraction phase, use these leads to identify banks, compression and
dialogue categories, then correlate original-disc data with actual menu/fight
triggers. If comparing a redub patch later, keep original and patched copies
separate and record exact hashes and patch provenance. Do not contact authors,
import databases, apply patches, or start audio extraction as part of this
initial setup. The later metadata-only BT3 audit is recorded separately in
[FUNIDUB_RESEARCH.md](FUNIDUB_RESEARCH.md). Subsequent authorized local example
extraction is recorded in [AUDIO_INVESTIGATION.md](AUDIO_INVESTIGATION.md).
