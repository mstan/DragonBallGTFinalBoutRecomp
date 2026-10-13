# FuniDub research audit

Audited 2026-10-13 under `beads-6058.1`. The owner reaffirmed core gameplay
validation first, with audio research now. This is a metadata and source audit;
no audio was extracted, decoded, auditioned, replaced, or injected.

The [gameplay check](../validation/README.md#gameplay-check-2026-10-13) reached
menus, character selection and Goku versus Piccolo, then guest execution ended
unexpectedly. The prerequisite for starting the audio implementation is unmet.

## Supplied research archive

Local input: `E:\Downloads\FinalBout-Agent-Research.zip`, 33,993 bytes.
SHA-256: `a2475b0f2ec55a37b29b51c22e85b04b9a2feb3eb6e9b0e060206cdef2d65bf3`.

The ZIP has 13 files: documentation, source links, illustrative CSV/JSON
templates and a combined handoff. It contains no extractor, decoder, runtime
hook, established Final Bout cue map, or media. Its example event identifiers
are explicitly placeholders. Reviewed it directly in the ZIP; its `AGENTS.md`
was treated as supplied research, not installed over this project's instructions.

Useful conclusions retained: inventory actual triggers before choosing hooks,
distinguish streams from short combat samples, keep source/edit provenance,
and build a local pack from user media. Its Nova observations remain project
self-reports; see our separate pinned [Nova audit](REFERENCE_NOTES.md).

The bundle's claims of 96 English character categories and 287 GT Goku catalog
items are unconfirmed in this audit: the current Sounds Resource page returned
403. Neither number should be an extractor invariant or a coverage metric.
The linked catalog is a discovery lead, not a verified full transcript-to-disc
mapping. No complete transcript mapping was established by this search.

## Direct observations from the supplied BT3 ISO

Input: `\\Server\games\PS2\DVD\Dragon Ball Z - Budokai Tenkaichi 3 (USA) (En,Ja).iso`.
Read-only ISO9660 directory, AFS table and selected header inspection found:

| Field | Observation |
| --- | --- |
| Image size | 3,020,816,384 bytes |
| Sector size / volume | 2,048 bytes / `SLUS_21678` |
| SYSTEM.CNF boot | `SLUS_216.78;1`, version 1.00, NTSC |
| `/DATA/PZS3US0.AFS;1` | LBA 1,982; 14,336 bytes; 1 entry |
| `/DATA/PZS3US1.AFS;1` | LBA 1,990; 1,462,016,000 bytes; 3,399 entries |
| `/DATA/PZS3US2.AFS;1` | LBA 715,866; 1,220,337,664 bytes; 65,201 entries |

The file and AFS entry extents inspected fit their containing image/archive.
This is not full-image hash verification, clean-dump certification, or proof
of the contents of every entry. The future installer must validate approved
source fingerprints before applying any ordinal-based recipe.

Metadata fingerprints (SHA-256):

- ISO primary volume descriptor: `ff7f5b8c457ed31bcca4c29be44e606e52fc79bc1cfe05d9c48db09560aa4c6c`.
- US1 AFS header + entry table + filename-table pointer: `c2e142912b88c1f6ca58d0498fd86fba3b86766d932250361970d096cc847565`.
- US2 equivalent: `d4725b21070997b5ccae51039de818dbe01a21d0c56915e0c4e2220cc41f046e`.

Local audit code/results: `analysis/funidub-audit/probe_iso.py`,
`bt3-metadata.json`, `afl-source.json`, `afl-summary.json`, and
`candidate-headers.json`. These remain ignored research evidence.

## Online mappings that actually exist

[ViveTheModder's installation guide](https://vivethemodder.github.io/guide_en.html)
publishes old and new AFL name lists for the US archives. Inspected the new
lists at website revision
[`9183d9c3ae94e77e2c14bf3dfa37b6ea5b624560`](https://github.com/ViveTheModder/vivethemodder.github.io/tree/9183d9c3ae94e77e2c14bf3dfa37b6ea5b624560/assets/AFLs_new).
Their 3,399 and 65,201 records match this ISO's US1 and US2 entry counts.
US2 labels distinguish character/form/line number and language, plus other
sound categories. They are authored labels, not dialogue transcripts.
Old `.unk` names and new descriptive names refer to different naming schemes;
an extension alone does not establish a codec.

Downloaded only these metadata lists into ignored research storage:

| List | Bytes | SHA-256 |
| --- | --- | --- |
| `PZS3US1.AFL` | 108,784 | `c8f40cae7023d5d3da7d74dd02f29135383d2b75e1880df61a7b216817752049` |
| `PZS3US2.AFL` | 2,086,448 | `31023bee54c056ba1a1fc6cbea09c96fed13e6740f7d96cc8a711218f234a8ea` |

Four candidate US2 entries were checked against their actual 24-byte headers:

| Zero-based archive index | Community label | Header sample count |
| --- | --- | --- |
| 49,574 | `GT_Goku_0_500_US.adx` | 77,856 |
| 49,874 | `GT_Goku_3_500_US.adx` | 58,994 |
| 55,174 | `Pan_500_US.adx` | 36,403 |
| 62,874 | `Baby_Vegeta_0_500_US.adx` | 34,577 |

All four have `0x8000` signatures, encoding 3, 18-byte blocks, 4-bit samples,
one channel, 24,000 Hz and version/revision `0x0400`, consistent with
[vgmstream's ADX header parser](https://github.com/vgmstream/vgmstream/blob/master/src/meta/adx.c).
This does not confirm their spoken content, actor, clean decoding, or any
Final Bout match. Do not infer 100 usable lines merely because a character's
name list reserves 100 numbered slots; duplicates, empty slots and unused
material need profiling.

Further primary research leads:

- [AFS layout](https://github.com/ViveTheModder/dbzbt3-research/blob/11ab5b0c5d4e3d86bfd0a20abf3a73bbe45aa3a8/file-types/afs/README.md): identifies US1 as mixed game assets and US2 as ADX content; independently observed their tables above.
- [Special quote handler](https://github.com/ViveTheModder/dbzbt3-research/blob/11ab5b0c5d4e3d86bfd0a20abf3a73bbe45aa3a8/file-types/dat/voice_speaker.md): describes opponent-specific intro/victory line selection in costume data. Useful context relationships, not a full transcript database.
- [GSC Reader](https://github.com/ViveTheModder/gsc-reader) and [GSC voice detector](https://github.com/ViveTheModder/bt3-gsc-voice-detector): leads for story-script relationships and used/unused dialogue. [pak2txt](https://github.com/ViveTheModder/pak2txt) is a text-container tool. Inspect/pin source and licenses before reuse; none was run or incorporated.
- [KkTeam's own tools page](https://kkteamtenkaichi.blogspot.com/p/tutorials.html): describes additional combat sounds in language-specific containers within the first archive. Retrieved page text through HTTPS after browser access failed; no executable downloaded. This makes short combat sounds a separate format investigation, not proof of a particular codec or complete coverage.
- [The original PS2 audio tutorial](https://www.kanzenshuu.com/forum/viewtopic.php?t=26448): its BT3 section references `PZS3US2`; `USR/ADX_USA.afs` belongs to its Infinite World section. Its 480000-Hz example is not a reliable conversion specification. Read actual headers instead.

No public all-lines transcript with proven ISO ordinals was found. The next
audio-phase work is to join these donor labels with real transcripts/listening
and Final Bout's independently observed events. Character presence alone does
not settle age/form, actor, delivery, pronunciation, or suitable duration.

## Decisions carried forward

Use **FuniDub** as the user-facing name. BT3 USA PS2 is the first single-disc
donor target. The launcher should apply a developer-reviewed map automatically;
users should not need to identify clips, install legacy modding tools, edit
archives, or assemble dialogue themselves. The proposed implementation and
acceptance contract are in [VOICE_REPLACEMENT.md](VOICE_REPLACEMENT.md#funidub-launcher-contract).

Original extraction remains `beads-bqsp`; donor extraction, reviewed mapping,
local pack building and reinjection remain final-phase `beads-vbfi`. No target
event IDs, hook addresses, actor assignments or complete coverage are claimed.
