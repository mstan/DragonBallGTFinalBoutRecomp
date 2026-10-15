# FuniDub source investigation — 2026-10-14

This report preserves the first investigation. The subsequent verified tables
are [original cues](VOICE_ORIGINAL_TABLES.md) and [BT3 donor events](VOICE_DONOR_TABLES.md).
The current implementation and its coverage limits are in [FuniDub](FUNIDUB.md).

The owner resumed audio-replacement investigation after the visible widescreen
review. This first pass verifies storage formats, local extraction and available
engine primitives. It does not install replacements or implement the launcher.
Original cue inventory precedes curated donor matching and reinjection. Loading
HLE/precaching remains parked; remaining gameplay acceptance is tracked separately.

## Source identity and scope

The local SLUS-00493 raw track is reverified in full against SHA-1
`8a2373f133788256cba64a1a0ba9fbb4b4667f71`. Its ISO directory has 23 files.
The report also records the full raw-track SHA-256.

The supplied BT3 image is 3,020,816,384 bytes. Its PVD and both AFS tables match
the fingerprints in [the initial metadata audit](FUNIDUB_RESEARCH.md). The AFL
labels are checked against their previously recorded SHA-256 values. Selected
archive entries and their extracted subresources receive independent hashes.
The full donor ISO has not been hashed; these observations validate the inspected
metadata/payloads, not every byte of the image or every community label.

All extracted material, WAVs, JSON inventories and audition clips remain under
ignored `analysis/audio-investigation-20261014/`. Only tooling and this report
belong in Git. No ISO, guest memory, game configuration or framework pin changes.

## What the actual Final Bout disc contains

| Resource | Direct observation | Remaining interpretation |
| --- | --- | --- |
| `BATTLE/BTWINV.DAT` | 54 nonlooping PSX ADPCM candidate regions, valid aligned frames, paired end/sentinel blocks | Speaker/order, runtime cue IDs and SPU playback pitch |
| `BATTLE/DEMOXA01.STR` | 16 XA file/channel/coding groups, mono 37,800 Hz, 4-bit | Event boundaries and speakers inside each channel |
| `BATTLE/DEMOXA02.STR` | 16 equivalent groups | Same |
| `BATTLE/DEMOXA03.STR` | Four equivalent groups | Same |
| `BATTLE/FINISH.STR` | 18 groups, mono 18,900 Hz, 4-bit | Same |
| `TITLE/BTCHARA.DAT`, `TITLE/CHARSEL.BIN` | Mixed resources, including `Psdp` compressed blocks; not whole-file flat VAB banks | Separate real sample extents and correlate their loader/voice tables |
| `TITLE/TENKAWIN.BIN`, `TITLE/VABDATA.BIN` | Aligned ADPCM with looping and nonlooping flags | Classify contents and recover the driver tables; not added to the victory-voice count |
| Opening, logo and credits STRs | Six other XA groups, included in the metadata inventory | Content not classified as dialogue/music/effects |

The four battle resources contain **54 XA groups**. Terminal submode flags must
be folded into the same file/channel/coding identity; counting them separately
incorrectly doubles the count. An XA channel is not necessarily a single spoken
line. A decoded DEMOXA03 channel lasts 41.3867 seconds, and needs event-level
segmentation before assigning cue identities.

Three victory candidates decode successfully. Their ADPCM sample counts are
exact, but the standalone WAV wrapper assumes 44,100 Hz because the raw bank
does not declare playback pitch. Those filenames and receipts explicitly mark
pitch unverified; their provisional WAV durations must not become mapping facts.
The candidate IDs use file offsets, not guessed character names.

The [original HCS investigation](https://hcs64.com/mboard/forumlong.php?showthread=58576)
was a useful file-location lead. Its track/speaker descriptions remain leads;
this report's counts and formats come from the supplied disc. The earlier
[Brazilian redub author's account](https://www.romhacking.net.br/index.php?topic=2166.0)
also distinguishes replaced lines from omitted close-range sounds. Neither is
imported as an established cue map.

## BT3 has both donor paths

Longer candidate lines are ADX entries in `PZS3US2`. The four previously inspected
entries now decode locally: 49574, 49874, 55174 and 62874, with community labels
for GT Goku forms, Pan and Baby Vegeta. They are mono 24 kHz. Actor, form,
transcript and suitability remain unverified until listening/context review.

The first archive also has **161 English-labelled character voice PAKs**. Four
actual entries were inspected in detail:

| US1 index | Community label | Observed structure |
| --- | --- | --- |
| 3194 | `Goku_0_Voice_US.pak` | Three PAK members: ADPCM body, Sony IECS header, sequence data |
| 3201 | `GT_Goku_0_Voice_US.pak` | Same |
| 3204 | `GT_Goku_3_Voice_US.pak` | Same |
| 3257 | `Pan_Voice_US.pak` | Same |

Each inspected HD/BD bank has a nominal Vagi count of 56 plus a populated extra
record: **57 bounded candidate waves**. Observed declared rates are 11,000,
11,025 and 16,000 Hz. These are candidate records, not 57 proven usable grunts or
unique lines. The sample/body/header boundaries, padding and hashes are recorded.

The Sony layout is corroborated by vgmstream's
[`hd_bd.c` at 7c520e8f](https://github.com/vgmstream/vgmstream/blob/7c520e8f9b078dfde2f84f1b5bcbad0c6c415806/src/meta/hd_bd.c).
Its optional extra record, aliases and body-end sentinel require explicit handling.
The research parser validates extents and retains aliases instead of inventing
new cue identities. US1/3201/wave 0 decodes to 5,236 samples at 16 kHz (0.32725 s).

`Battle_US.pak` is not the character voice container. Its name alone was an
insufficient lead; the actual English `*_Voice_US.pak` entries are the useful
short-sample path. Character names in the AFL remain community metadata.

## Decode results and reproducibility

The reproducible probe decodes **nine local examples**: three original victory
candidates, one original XA channel, one donor Sony wave and four donor ADXs.
Every output has the expected sample count/rate and nonzero PCM. Source hashes,
commands, FFmpeg version, PCM hashes, peaks and rail-valued sample counts are
recorded in `repro/inventory.json`. The decoder used was FFmpeg 7.1, native Windows.
This is automated format/decode evidence, not a listening or semantic match result.

FFmpeg's untrimmed ADX outputs initially contained 0/14/13/15 samples beyond the
four headers' declared counts. The probe applies `atrim=end_sample=<header count>`;
final counts are exactly 77,856 / 58,994 / 36,403 / 34,577. Do not make cue timing
depend on a decoder's block-padding convention. A few donor samples reach PCM
rails; no cleanup, gain matching or final edit has been curated yet.

Eight synthetic tests cover malformed/truncated PAK and ADX extents, Sony extra
records, aliases, sentinels and truncated bodies. They contain no game data.

```powershell
& 'C:\Users\Matthew\AppData\Local\Programs\Python\Python312\python.exe' -m unittest discover -s tools/audio

& 'C:\Users\Matthew\AppData\Local\Programs\Python\Python312\python.exe' tools/audio/probe_sources.py `
  --target-bin 'disc\Dragon Ball GT - Final Bout (USA).bin' `
  --donor-iso '\\Server\games\PS2\DVD\Dragon Ball Z - Budokai Tenkaichi 3 (USA) (En,Ja).iso' `
  --labels-dir analysis/funidub-audit `
  --out analysis/audio-investigation-20261014/repro `
  --ffmpeg 'C:\ffmpeg\bin\ffmpeg.exe'
```

Omit `--ffmpeg` for a metadata-only probe. The pinned AFL metadata files are the
inputs retained by the earlier audit, not extracted recordings. The current
probe is a developer research tool, not the promised end-user installer.

A roughly ten-second BT3 review reel is ready locally. It concatenates the
GT Goku 0/3 and Pan ADX examples and the short Sony wave, with 0.5-second gaps
and a documented 24 kHz mono review conversion. No words, performances or voices
were generated. Its source/edit recipe is `review-reel-recipe.json`; listening
was played on request, then opened visibly in VLC for the owner to replay.
The owner answered "those are all good." This accepts the sampled donor audio,
not a full cue map, every character's actor identity or complete pack coverage.

## Replacement approach to investigate next

The pinned framework already provides two relevant primitives:

- `psx_mod_spu_sample_bank` / `psx_mod_spu_bind_voice_bank`: immutable ADPCM banks
  selected before the original driver's KEYON. Bank IDs are included in SPU
  snapshot state. This is a candidate for short samples after finding actual
  title cue/voice hooks and preserving pitch, cancellation and end behavior.
- `psx_mod_append_disc_extent`: deterministic activation-time registration of
  verified raw Mode-2 resources. This is a candidate for XA-backed lines after
  tracing real CD seek/filter/range selection. It is not a universal WAV override.

These APIs are in the pinned `mod_plugins.h`; their presence does not establish
that either integration is complete. An external recording must not extend
gameplay waits or overwrite effects/music merely because it shares a bank.
Original behavior remains the fallback for gaps and unverified events.

Neither path should be assumed presentation-only. Guest completion, IRQ/end
flags, voice state and snapshot digests can depend on sample/stream behavior.
Before enabling a future pack online, agree a validated profile and final encoded
resource hashes before frame 0 and keep that selection fixed for the match.
Different tool versions or operating systems are not proof of identical content.
Any needed CPU/backend capability selection follows the shared netplay policy;
this investigation changes no handshake, runtime code or network pins.

Next: recover Final Bout's mixed-resource/sample tables, trace menu/fight/victory
events and original SPU pitch/CD ranges, then curate a small original-to-donor
review sheet. Suitable generic introductions/grunts are permitted substitutions,
not automatic exact matches. Full cue inventory and actual reinjection remain
open under `beads-bqsp` and `beads-vbfi`.
