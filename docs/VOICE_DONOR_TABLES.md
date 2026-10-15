# BT3 donor ordering and coverage

2026-10-14 discovery for `beads-bqsp` / `beads-vbfi`. This is a source-category
inventory, not a reviewed Final Bout replacement map. No actor or transcript is
established by an AFL filename. The owner accepted the earlier GT Goku/Pan reel;
this pass performed no playback, game launch, media upload or generated speech.

## Evidence and reproducibility

The supplied 3,020,816,384-byte BT3 USA ISO passed the PVD and both AFS-table
fingerprints recorded in [FUNIDUB_RESEARCH.md](FUNIDUB_RESEARCH.md). Every entry
inspected below has a complete encoded SHA-256, offset and extent in ignored
`analysis/funidub-donor-discovery/inventory.json`. The full ISO is not hashed.
The tracked [inventory tool](../tools/audio/inventory_donor.py) reproduces this
metadata using the adjacent `probe_sources.py` parser. The tracked
[curation tool](../tools/audio/curate_donor.py) then produces `curation.json`, adding `candidate_category`,
`verified_silent_placeholder`, sound-to-wave relationships, source-code pin,
and bounded-versus-driver-stop sample counts. It checks 13 unique short payloads
with offline FFmpeg 7.1 decoding and retains PCM hashes and peaks.

From the repository root, use Python 3 and an explicit FFmpeg executable.
Replace the quoted input placeholders with local paths. The first command can
download only the two pinned AFL metadata lists into the ignored source cache;
their byte counts and SHA-256 values are checked before use. Omit
`--fetch-labels` for an existing cache and fully offline operation. Media stays
in the supplied ISO; these tools write JSON metadata and cached AFL lists only.
Neither captured RAM nor downloaded decompilation source files are required.

```powershell
python tools/audio/inventory_donor.py `
  --donor-iso '<BT3 USA ISO path>' `
  --source-cache analysis/funidub-donor-discovery/source-cache `
  --fetch-labels `
  --out analysis/funidub-donor-discovery/inventory.json

python tools/audio/curate_donor.py `
  --inventory analysis/funidub-donor-discovery/inventory.json `
  --donor-iso '<BT3 USA ISO path>' `
  --source-cache analysis/funidub-donor-discovery/source-cache `
  --ffmpeg '<FFmpeg executable path>' `
  --out analysis/funidub-donor-discovery/curation.json
```

The curation records the actual FFmpeg version alongside the PCM receipts.
Event categories remain the documented interpretation of the pinned primary
sources below; running this metadata workflow does not qualify transcripts or
Final Bout substitutions.

The inventory reads all 161 English-labelled US1 voice PAKs, 59 relevant
100-entry English US2 character blocks, and 210 menu/referee candidate entries.
All 161 banks contain 57 bounded Sony waves. Actual sequence and timbre tables
independently verify **sound i -> timbre i -> wave i** for all 9,177 entries.
Observed bank rates are 8,000, 11,000, 11,025, 16,000 and 18,000 Hz.

Event ordering is corroborated against the primary matching-decompilation
source pinned at `z3xox/BT3-Decompiled` commit
`95b950367364137130758ef82a218e607a54b703`. This pass did not rebuild that
decompilation or independently prove every instruction against the executable.
The metadata checks and the source-derived event interpretation are distinct
evidence. The source receipts remain in the ignored discovery directory.

## Stable source addressing

Use zero-based archive ordinals and wave indices, never community filenames as
identity. For character ID `c`, US1 English bank ordinal is `3194 + c`; English
US2 character line `l` is ordinal `48874 + c*100 + l`. The AFL suffix is
`500 + l`. These are archive ordinals; BT3's global file IDs additionally add
3,400 for US2. This translation comes from
[`file.c`](https://github.com/z3xox/BT3-Decompiled/blob/95b950367364137130758ef82a218e607a54b703/src/sys/file.c)
and [`adx.c`](https://github.com/z3xox/BT3-Decompiled/blob/95b950367364137130758ef82a218e607a54b703/src/sys/adx.c).

The following form descriptions are discovery metadata, cross-referenced with
the community author's [character-ID list at a pinned revision](https://github.com/ViveTheModder/gsc-reader/blob/9801aec91cbd93f626e6a674e098927ac0e83d43/csv/bt3/chara.csv).
They do not prove performer identity or the appropriate Final Bout target form.
US2 start means line 0; add the verified event line index below.

| Candidate donor form | AFL family | Character ID | US1 bank | US2 start |
| --- | --- | ---: | ---: | ---: |
| Adult Goku, End | Goku_3 | 3 | 3197 | 49174 |
| Adult Goku, End SS | Goku_4 | 4 | 3198 | 49274 |
| GT Goku base | GT_Goku_0 | 7 | 3201 | 49574 |
| GT Goku SS | GT_Goku_1 | 8 | 3202 | 49674 |
| GT Goku SS3 | GT_Goku_2 | 9 | 3203 | 49774 |
| GT Goku SS4 | GT_Goku_3 | 10 | 3204 | 49874 |
| Kid Goku, Dragon Ball | Goku_7 | 11 | 3205 | 49974 |
| Adult Gohan | Gohan_4 | 17 | 3211 | 50574 |
| Adult Gohan SS | Gohan_5 | 18 | 3212 | 50674 |
| Piccolo, End | Piccolo_1 | 23 | 3217 | 51174 |
| Vegeta, End base | Vegeta_6 | 34 | 3228 | 52274 |
| Vegeta, End SS | Vegeta_7 | 35 | 3229 | 52374 |
| Vegeta, End SS2 | Vegeta_3 | 36 | 3230 | 52474 |
| Trunks with sword | Trunks_0 | 39 | 3233 | 52774 |
| Trunks with sword SS | Trunks_1 | 40 | 3234 | 52874 |
| Trunks without sword | Trunks_5 | 41 | 3235 | 52974 |
| Trunks without sword SS | Trunks_6 | 42 | 3236 | 53074 |
| Pan | Pan | 63 | 3257 | 55174 |
| Frieza final form | Frieza_4 | 94 | 3288 | 58274 |
| Cell perfect form | Cell_2 | 107 | 3301 | 59574 |
| Cell perfect | Cell_3 | 108 | 3302 | 59674 |
| Majin Buu | Buu_0 | 112 | 3306 | 60074 |
| Kid Buu | Buu_3 | 117 | 3311 | 60574 |
| Baby Vegeta | Baby_Vegeta_0 | 140 | 3334 | 62874 |
| Super Baby 1 | Baby_Vegeta_1 | 141 | 3335 | 62974 |
| Super Baby 2 | Baby_Vegeta_2 | 142 | 3336 | 63074 |
| Great Ape Baby | Baby_Vegeta_3 | 143 | 3337 | 63174 |

BT3's GT base Goku is the child form; adult GT Goku needs an explicitly recorded
substitution such as adult Z Goku. GT Trunks and base/SS GT Vegeta likewise need
form substitutions from the available Z banks. Do not silently interpret AFL
`Vegeta_3` as SS: this ID list identifies it as End SS2. Select the actual Final
Bout Buu/Cell/Baby form from target evidence before choosing one of those rows.

## Event categories recovered from code and donor tables

[`btl_seq.c`](https://github.com/z3xox/BT3-Decompiled/blob/95b950367364137130758ef82a218e607a54b703/src/battle/btl_seq.c)
selects generic intros from lines 0/1 and generic wins from 3/4. Opponent-specific
intros add 6 to the costume talk-table entry; opponent-specific wins add 30.
The table and target context must be checked before borrowing a specific quote.

| Donor event category | US2 line index | AFL suffix |
| --- | ---: | ---: |
| Generic intro alternatives | 0, 1 | 500, 501 |
| Generic victory alternatives | 3, 4 | 503, 504 |
| Non-winning result line | 42 | 542 |
| Technique class 0 | 83, 84 | 583, 584 |
| Technique class 1 | 85, 86 | 585, 586 |
| Technique class 2 | 87, 88 | 587, 588 |
| Technique class 3 | 89, 90 | 589, 590 |
| Technique class 4 | 91, 92 | 591, 592 |

Technique class ordering and the two animation event bits come from
[`btl_char_sound.c`](https://github.com/z3xox/BT3-Decompiled/blob/95b950367364137130758ef82a218e607a54b703/src/battle/btl_char_sound.c).
That function selects short-wave groups 45..48, 49..52 and 53..56 for classes
2..4; its short-sound selector is disabled for classes 0/1. A separate primary
path, [`BtlCharApi_PlayTechniqueSound`](https://github.com/z3xox/BT3-Decompiled/blob/95b950367364137130758ef82a218e607a54b703/src/battle/btl_char_api_2.c),
maps classes 0/1 to `37+n` / `41+n` for `n<4`. Its observed caller
[`EftShot_PlayFireSound`](https://github.com/z3xox/BT3-Decompiled/blob/95b950367364137130758ef82a218e607a54b703/src/battle/eft_shot.c)
supplies only n=0/1/2. Thus 37..39 and 41..43 have demonstrated caller categories;
40/44 are API-supported slots with caller usage unproven and have no candidate
category in the machine curation. A technique class is not a transcript or
attack-name match.

The shared voice-kind table is actual US1 ordinal 1, member 5 (zero-based),
512 bytes, SHA-256
`3c03c34074cb409fe6aec7354476ceace0a6608f9f43c2cdcbebf5a4a1efcd20`.
The first 57 records contain signed 16-bit first/count and a float cooldown.
`btl_char_mgr.c` binds header word 6 at roster +0x28; `btl_char_util.c` uses
kinds below 15 for short bank sounds, and the rest for streamed character lines.

| Verified donor usage | Voice kind | US1 wave indices |
| --- | ---: | --- |
| Hit reaction category 0 | 0 | 0..5 |
| Hit reaction category 1 | 1 | 6..9 |
| Hit reaction category 3 | 3 | 12..13 |
| Attack-record voice 1 | 5 | 16..18 |
| Attack-record voice 2 | 6 | 19..21 |
| Attack-record voice 3 / rapid rush | 7 | 22..25 |
| Guarded-hit reaction | 11 | 30..31 |
| Ki-blast emission | 12 | 33..34 |
| Ki-charge start | 13 | 35 |
| Form-change / animation trigger | 14 | 36 |

Usage comes from `btl_hit_reaction.c`, `btl_param.c`, `btl_act_1.c`,
`btl_act_2.c` and `btl_act_change.c` at the same pinned revision. These are
useful audition sets; a combat category does not prove a sample is nonverbal.
The full machine inventory retains every other kind without guessed meanings.

## Menu, referee and missing-content limits

Actual English-labelled referee blocks start at 65060 (Ox), 65067 (Videl),
65074 (Kaioshin), 65081 (Shenron), 65088/65095/65102 (Announcer A/B/C), and
65109 (Training). Each has seven entries. In
[`hud_notice_2.c`](https://github.com/z3xox/BT3-Decompiled/blob/95b950367364137130758ef82a218e607a54b703/src/battle/hud_notice_2.c),
the first six slots are ready, fight, two K.O. variants, finish-reason bit 2,
and time-up. Slot 6 is not classified here. These are event identities, not
auditioned English transcripts. Announcer A's fight candidate is US2/65089.

The auxiliary inventory also hashes AFL-labelled Versus 32219..32230,
World Tour 32231..32264, Main Menu 32525..32589, and Options 32590..32632.
Their names are category leads. No Final Bout title announcement, menu phrase,
character-name call or tournament-completion speech has a reviewed match yet.

Do not count reserved slots as coverage. Across the 59 inspected character
blocks, distinct encoded payload counts range from 21 to 90 per 100 slots.
GT_Goku_1 has 33 and GT_Goku_2 has 21. A frequent 240-sample / 10-ms entry has
SHA-256 `597d97724aa574ce5497a8eb724bf13ee3977ec4d9e1e252a16f27c10c0b4057`;
another GT placeholder has only 36 samples. Duplicate payloads, near-silence,
form sharing, semantic fitness, actor and contamination require explicit review.
The two short ADX payloads decode to all-zero PCM, covering 1,550 slots in the
59 inspected blocks. Both are positively marked as silent in `curation.json`.

GT_Goku_1 / US1/3202 and GT_Goku_2 / US1/3203 have verified silent waves 0..35,
including every ordinary hit/attack/ki sound group above. Those forms need an
explicitly reviewed reuse such as GT base bank 3201 for short combat sounds;
their bank record counts do not establish usable grunt coverage.

Short-wave bounds include alignment/end padding. For example GT_Goku_0 wave 0
contains at most 5,236 decoded samples, but its first ADPCM end flag is after
5,208. The prior probe's FFmpeg WAV included the extra 28 samples. The new
inventory preserves both counts and the end flag; use actual playback bounds
when trimming, and keep source sample rate separate from any review conversion.
Pan wave 36 is only 56 samples to its first end flag, so a valid wave record
does not guarantee a usable transformation shout.
The repeated 48-byte wave payload with SHA-256
`3b304fa12faf3d1494977c1ef0c4c9642ce2d4ce78ae6a8d59ca9094c3bd08b8`
is all-zero through that first end flag (56 samples), but decoding the whole
bounded record adds a padding artifact with peak 224. This verified silent
payload occurs in 1,814 short-bank slots. Other very short waves include real
nonzero PCM; duration alone is not a silence classifier.

These findings establish source locations and event-category candidates. Final
recipes still need target cue identity, source/target semantic review, performer
verification where claimed, recorded edits, and playback/timing validation.
