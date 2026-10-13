# Recorded dialogue replacement

This is a deferred design contract, not an extraction or replacement result.
Original dialogue extraction is the penultimate phase (`beads-bqsp`).
Recorded-clip replacement is the final phase (`beads-vbfi`), after the baseline,
resolution, loading, widescreen and netplay work is validated.

The requested direction is a Funimation-cast performance assembled from existing
recordings, for example Sean Schemmel and Chris Sabat. No voice cloning,
generated dialogue or synthesized performances are part of the project.
The owner will supply TV media later and may identify other game recordings.

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
initial setup. No reference code or media has been imported.
