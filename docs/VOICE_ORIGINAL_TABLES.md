# Final Bout original audio tables

Offline discovery against the supplied USA disc, SHA-1
`8a2373f133788256cba64a1a0ba9fbb4b4667f71`. The extracted boot EXE SHA-256 is
`507f132cdcbb635bbbf7a75e15c62a9d0d51e22ce4432828da784ec03b67cbcc`.
Addresses below come from the disc's own MIPS instructions and tables, independently
of other recomp projects. No game launch, audio playback or Ghidra database change
was performed for this discovery. Character names and individual sound semantics
are still separate qualification work.

Local metadata and reproducibility scripts are under ignored
`analysis/funidub-original-discovery/`. `inventory_tables.py` produces
`original-tables.json`: file identities, complete per-sample offsets/hashes, terminal
frames, allocations, instrument aliases, original pitches, mixed-resource spans,
and exact opcode/table guards. Inventory reproduction reads the original disc
directly; it requires no gameplay RAM capture, prior generated inventory or
Capstone installation. Importing the inventory module does not regenerate output.
This is metadata, not a distributable media pack.

## Verified bank format and playback

The resident bank registry is `0x80035030`, eight slots of 16 bytes:
header pointer, SPU body address, sample-offset-table pointer, transfer remainder.
Registration at `0x8001350C` computes the offset-table pointer from the header's
instrument count. The header format is:

| Offset | Meaning |
| --- | --- |
| `+0` | Four bytes `SNTp` |
| `+4` | Little-endian u32 ADPCM body byte length |
| `+8` | u16 instrument count |
| `+A` | u8 sample count |
| `+B` | u8 bank volume |
| `+10` | Instrument records, 16 bytes each |
| after records | u16 sample start offsets in units of eight bytes |

An instrument's byte `+1` selects its sample; u16 `+4` is its base note/fine
pitch; u16 `+8` and `+A` supply ADSR. Append the header's body length to the
sample starts to obtain the last sample's end. Do not assume an additional
nonzero table sentinel: several banks have zero padding there.

`0x80013B20` triggers an instrument: `a0` is voice, `a1` bank handle, `a2`
instrument, `a3` note; caller stack `+10` is fine pitch and `+14/+18` are
left/right volume. Its lookup uses the instrument's sample index and the u16
offset multiplied by eight. `0x8001A274` sets voice attributes and keys on.
The pitch calculation is `0x8001AE94`, using the 192-entry u16 lookup table at
`0x8002C66C`. At note `0x3C00`:

| Instrument base note | SPU pitch | Exact effective source rate |
| --- | --- | --- |
| `0x4E39` | `0x05CD` | `44100 * 1485 / 4096 = 15988.4033203125 Hz` |
| `0x5400` | `0x0400` | 11,025 Hz |
| `0x4800` | `0x0800` | 22,050 Hz |

These are driver-derived pitches, replacing the earlier unqualified 44.1 kHz
WAV assumption. Preserve the integer pitch and original frame/end behavior.

## Character combat banks

`MENU/STEP01.BIN` loads at `0x8003DFA0`. Its sector table at `0x80053BEC`
has 15 entries per numeric character ID; body resource is slot 5, metadata
resource is slot 10. Each metadata resource contains one `SNTp` header at
resource `+0x200`. Offsets below are in the logical 2048-byte view of
`TITLE/BTCHARA.DAT`, LBA 18,415.

| ID | Body offset | Body bytes | Header offset | Samples |
| --- | --- | --- | --- | --- |
| 0 | `066000` | `12460` | `07C200` | 13 |
| 1 | `0DF000` | `11B50` | `0F6200` | 13 |
| 2 | `159800` | `0E510` | `16C200` | 12 |
| 3 | `1CF000` | `115A0` | `1E4200` | 13 |
| 4 | `246000` | `11560` | `25D200` | 12 |
| 5 | `2C2800` | `0D9D0` | `2D4A00` | 12 |
| 6 | `33C000` | `129F0` | `353200` | 13 |
| 7 | `3B8000` | `112E0` | `3CE200` | 13 |
| 8 | `43D000` | `12810` | `455200` | 12 |
| 9 | `4BC800` | `11770` | `4D3200` | 13 |
| 10 | `53A000` | `12CC0` | `551200` | 13 |
| 11 | `5B5800` | `0D9D0` | `5C7200` | 12 |
| 12 | `62F000` | `13620` | `646A00` | 13 |
| 13 | `6AA800` | `11880` | `6C1200` | 13 |
| 14 | `729000` | `0FF80` | `73CA00` | 12 |
| 15 | `7A2000` | `0EB50` | `7B5200` | 12 |
| 16 | `81B000` | `13620` | `832200` | 13 |
| 17 | `896800` | `128C0` | `8AD200` | 13 |

All table numbers are hexadecimal. The 227 sample records contain 160 unique
hashes. IDs 5/11 have identical combat banks, as do IDs 12/16.

In `STEP40`, combat dispatch `0x8004FEB8` routes event IDs below `0x10` to the
selected player's character bank, at note 60 and fine pitch zero. IDs
`0x10..0x2E` select the common effects bank. Character instruments 0..8 usually
use base note `0x4E39`; exception ID 10/instrument 7 uses `0x5400`. ID 0 has
an additional instrument 13 with `0x4E39`. This is a candidate voice group,
not semantic proof that every member is speech. Instruments 9..12 have other
base notes and extensive shared samples: preserve these pending classification.
Instrument 10 in every character bank reaches terminal flag 3 (end plus repeat),
so it loops until native cancellation. For IDs 4 and 8 it selects wave 9;
the other IDs select wave 10. The JSON marks repeat behavior and loop markers.
Its sample count through that terminal describes the first pass, never a finite
playback duration. The CHARSEL and victory regions have nonrepeating flag-1
terminals. Do not remove or replace looping effects as bounded voice clips.

Instrument and sample indices are not interchangeable. For example ID 4/i8
aliases wave 2; ID 8/i7 aliases wave 6; ID 9/i6/i7 swap waves 7/6; ID 13/i11/i12
select waves 12/11. The JSON retains all aliases and their differing pitches.
The common effects body at BTCHARA `[0,0xDE40)` is excluded from replacement.
Its header is in STEP40 at file `+0x30B80`, runtime `0x8006EB20`.

Selected menu character IDs are u16 at `0x8003BCA4` and `0x8003BCA6`.
Combat character ID is byte `0x800727FC + 0x7C*player`, masked with `0x7F`.

The uncompressed `DB` animation-script tables now provide verified event
contexts. ID 0's table is at BTCHARA file `+0x5E800`: u16 magic `0x4244`,
u16 slot count 173, then 173 u32 word offsets (`0xFFFFFFFF` means absent),
followed by script words. Each character has one independently located table.
Interpreter `0x8004E530` dispatches the word's bits 16..23 through the table at
`0x8003E78C`; opcode `0x60` reaches `0x8004EAA4`, then the audio dispatcher.
Its low byte is the event ID and the next byte volume. Payload words must be
skipped correctly: vectors can contain false `0xFC600000` sound matches.
The local `combat-event-raw.json` retains source offsets, full scripts and
payload-aware event records for all 18 characters; all 2,929 populated scripts
terminate and use the interpreter's supported opcode set.

| Character instrument/event | Verified caller context |
| --- | --- |
| 0, 1, 2 | Physical attacks and combos; for ID 0, states 98..119, 140, 150, 155/156, 160..165 |
| 3 | Additional character-specific attack/finisher state; ID 0 state 151 |
| 4 | Hit reactions, including states 36..38, 42/45/48/51/54, 83 and 90 |
| 5 | Stronger hit reactions, states 39..41 |
| 6, 7 | Two projectile/energy-attack groups, normally states 120..122 and 126..128 |
| 8 | Ki-charge start, state 71 |
| ID 0 instrument 13 | Special energy-gathering/release sequence, state 157; exact attack wording remains unqualified |

Hit-reaction routine `0x80068314`, called by the hit resolver at `0x80066778`,
selects states 38/41 at `0x8006843C..54` based on incoming strength <=100/>100.
Those scripts contain events 4/5 respectively. The charge context has a second
independent check: `0x8006D1E4..0x8006D258` tests state `0x47` (71) and
replenishes the energy counter every two ticks, versus fifteen ticks outside
that state. Event 8 appears in that state's script for every character.
ID 6 reverses its event 6/7 assignment between the two projectile groups; ID 9
uses event 7 in both groups. ID 10/event 7 retains the previously noted effects
pitch and requires separate listening classification. These are caller
categories, not transcripts or proof that each attack sound is nonverbal.

## Menu and victory resources

The STEP01 table at `0x80053888` supplies CHARSEL sector boundaries. The
pre-fight loader indexes `12*character_id + 4 + variant`, with populated
variants 0..7 and empty aliases. This yields **110 nonempty bounded ADPCM
regions** in `TITLE/CHARSEL.BIN`, LBA 14,980. Every reported region has valid
frames, a terminal flag-1 frame followed by a flag-7 sentinel, and zero padding
to its sector allocation. Mixed `Psdp` and other resources are excluded.

STEP01 calls at `0x800521FC` and `0x80052504` use voices 22/23 and SPU body
addresses `0x50900/0x64900`, note `0x3C00`, base `0x4E39`: pitch `0x05CD`.
The side-effect-free pair-selection block `0x80051150..0x80051794` chooses
left variant in `s0`, right variant in `s7`, then stores `(s7 << 4) | s0` at
`0x8005663C`. It branches on both selected numeric character IDs when the
global at `0x80056874` is 1 or 2; other modes use variant 0 for both sides
(checked with mode 3). This comparison requires the **raw P1 u16 to be below
17**; P1 is not masked first, while P2 is masked with `0x7F`. A high-bit-flagged
P1 selection uses 0/0 even in modes 1/2, so the pair matrix is not a claim that
every route uses opponent-specific speech. A bounded offline evaluation recovered
all 324 unflagged pair
choices and their instruction traces in `menu-pair-variants.json`, and every
chosen variant resolves to a populated region. For example pair 4/5 uses
variants 5/6, pair 5/5 uses 5/7, and pair 14/5 uses 6/5. The initial six-variant
inventory omitted 14 regions; the eight-variant inventory supersedes it.

The STEP40 table at `0x80071798` has 55 sector boundaries ending at 953,
covering all of `BATTLE/BTWINV.DAT`, LBA 22,880. Its **54 victory slots** are
indexed `3*(character_id & 0x7F) + condition`. Function `0x8006CB40` chooses
condition 0 at health percentage >=80, 1 at 30..79, and 2 below 30.
The trigger at `0x8004FF78..0x8005001C` uses voice 23, SPU body `0x50900`,
note `0x3C00`, base `0x4800`: pitch `0x0800`, exactly 22,050 Hz.
Completion polling, cancellation and scene timing remain native game behavior.

## Tournament result resource

`TITLE/TENKAWIN.BIN`, LBA 17,583, is 872,448 bytes, SHA-256
`e11e441995854123da52353a3c6ff57b4fa4334a59d601a106f91c28aa9edcfa`.
Its 19 raw SPU regions have two independently matching 20-entry sector tables:
STEP02 at `0x8004D16C` and STEP999 at `0x800411F8`. Both tables hash to
`2e72f028a6397ff75598c79f0d6c1a6dd12e2182bb5dbcc8578132fa4722ffe2`.
They cover the complete file, with sector boundaries
`0,16,30,45,5C,6C,89,97,B9,C0,D5,EE,10B,12A,13D,159,165,184,197,1AA`
(hexadecimal). Regions 0..16 are finite clips with flag-1 terminal, flag-7
sentinel and zero allocation padding; regions 17/18 have flag-3 loop terminals.
Preserve those last two looping sounds independently of any new voice mapping.

The tracked [inventory tool](../tools/audio/inventory_original.py) now emits
`tournament`: 19 records named `tenkawin/slot00..slot18`, using the same
offset/size/hash/allocation/first-pass fields as menu and victory records.
Records include exact rates, flags, finite-playback status and preservation
markers. File identity and 29 exact producer instructions, both table hashes,
and complete STEP02/STEP999 identities are checked from the disc; no capture,
Capstone, playback or transcription is needed. Reproduce into ignored metadata:

```powershell
python tools/audio/inventory_original.py --target-bin 'disc/Dragon Ball GT - Final Bout (USA).bin' --out analysis/funidub-original-discovery/remaining-original-inventory.json
```

STEP02 `0x80043570..0x800435A4` obtains the selected player's numeric ID from
the u16 selection array at `0x8003BCA4`, masks it with `0x7F`, and carries it in
`s3`. At `0x80043BBC..0x80043C2C`, that ID indexes the TENKAWIN table, then the
unaltered raw resource uploads to SPU `0x50900` through `0x80016AD4`.
The result sequence's trigger at `0x800442C4..0x80044368` keys on voice **21**
(mask `0x00200000`), note `0x3C00`, base `0x4800`: pitch `0x0800`, exactly
22,050 Hz. This establishes slots 0..16 as numeric character result contexts;
their words, performer and voice/effect composition remain unqualified.
STEP02 separately loads the final two looping regions to SPU `0x64900` and
`0x6E100`, keying voices 22/23 at `0x80044100/0x8004418C`. Their counts describe
only the first pass, not finite playback durations.

STEP999's sound-test selector at `0x8003FD64..0x8003FE84` accepts decimal cue
IDs **164..180**, indexes `id - 164`, and reads these same finite slots. Its
trigger at `0x8003FF04..0x8003FF74` uses voice **23**, SPU `0x50900`, and the
same 22,050 Hz rate. IDs 181/182 do not access the two looping regions through
this selector. Representative guards are `0x80043BC4=0x2610D16C`,
`0x800442FC=0x24023C00`, `0x80044308=0x24024800`,
`0x8003FE18=0x2631FF5C`, and `0x8003FE20=0x261011F8`.

| Slots | Finite first-pass duration | Observation |
| --- | --- | --- |
| 0..16 | 1.0019..5.4286 seconds | 17 clips; 5/11 identical, 12/16 identical |
| 17/18 | 2.9968 / 2.9956 seconds per first pass | Repeating sounds; preserve |

These are concrete additional replacement **candidates**, not an assertion that
all 17 are speech or that a generic victory line is the appropriate substitute.

## XA selection and limits

STEP40 dispatch `0x800500A4..0x80050114` selects these original resources:

| Event IDs | Resource | Original audio channels | Coding |
| --- | --- | --- | --- |
| `0x32..0x41` | DEMOXA01, LBA 23,833 | 0..15 | mono 37,800 Hz, 4-bit |
| `0x42..0x51` | DEMOXA02, LBA 30,249 | 0..15 | mono 37,800 Hz, 4-bit |
| `0x52..0x55` | DEMOXA03, LBA 36,665 | 0..3 | mono 37,800 Hz, 4-bit |
| `0x30`, character channel | FINISH, LBA 42,873 | 0..17 | mono 18,900 Hz, 4-bit |

The dispatch also accepts `0x56..0x59`, but those DEMOXA03 channels have no
audio groups on this disc. File pointers are resident BCD MSF values at
`0x8002BE04/08/0C/10`; all four XA files use file number 1.
The dispatcher seeks the file start through `0x80016DC8` and supplies the
file/channel filter through `0x800172EC`. This path supplies no intra-channel
start/end range. Fresh offline discovery on 2026-10-15 ties these channels to
character attack scripts. Opcode `0x60` at `0x8004EAA4..0x8004EAF0` forwards
the event, volume and player to the dispatcher without character-specific event
remapping. The following table records the actual event bytes in the on-disc
animation scripts. Columns A/B are states 123..125 / 129..131 respectively;
they accompany the two projectile groups whose normal states are 120..122 /
126..128. Event IDs in this table are hexadecimal; character/channel IDs are
decimal. Convert DEMOXA event `E` to file `1 + floor((E-0x32)/16)` and channel
`(E-0x32) % 16`.

| Character ID | DEMOXA A event | DEMOXA B event | FINISH event/channel |
| --- | --- | --- | --- |
| 0 | `32` | `33` | `30` / 0 |
| 1 | `34` | `35` | `30` / 1 |
| 2 | `36` | `37` | `30` / 2 |
| 3 | `38` | `39` | `30` / 3 |
| 4 | `3A` | `3B` | `30` / 4 |
| 5 | `32` | `33` | `30` / 5 |
| 6 | `3F` | `3E` | `30` / 6 |
| 7 | `40` | none | `30` / 7 |
| 8 | `41` | `42` | `30` / 8 |
| 9 | `43` | `54` | `30` / 9 |
| 10 | `44` | `45` | `30` / 10 |
| 11 | `32` | `33` | `30` / 11 |
| 12 | `4F` | `50` | `30` / 12 |
| 13 | `55` | `4A` | `30` / 13 |
| 14 | `4B` | `4C` | `30` / 14 |
| 15 | `36` | `37` | `30` / 15 |
| 16 | `48` | `49` | `30` / 16 |
| 17 | `52` | `53` | `30` / 17 |

All 18 state-171 scripts start FINISH event `0x30`; its dispatcher path at
`0x8005002C..0x80050060` reads the acting player's raw character byte for the XA
channel. Character 17/state 171 additionally starts DEMOXA event `0x53` after
FINISH, so it switches streams within that sequence. Every script containing
an XA start also contains a later event `0x31`. At `0x8005006C..0x80050098`,
that event sets CD volume, calls `0x80017550(1)`, and queues command 10 through
`0x800169D0`. The corresponding explicit cancellation path also reaches
`0x80017550`. These are synchronized animation cues with native stop/cancel
behavior, not independent long-running scene tracks. This table establishes
on-disc script associations; loader mutation and every runtime route have not
been exhaustively ruled out. In particular, do not invent missing form-specific
event IDs from the apparent character order.

Only 29 of the 36 DEMOXA channels are referenced by these on-disc script events.
Events `3C/3D`, `46/47`, `4D/4E` and `51` have media but no such reference.
Their speaker/usage remains unqualified. Character 7's second group uses an SPU
event rather than XA. No script references the nonexistent channels `56..59`.

The tracked `tools/audio/inventory_xa.py` derives the bounded animation tables
and command boundaries directly from BTCHARA, checks eight exact
dispatcher/caller instructions and inventories all 54 XA groups. Optional
`--codec-check` decodes channels through the portable native developer driver.
The earlier ignored `xa_discovery.py --decode` independently cross-checked the
same script events and decoded all channels with FFmpeg 7.1. Its ignored
`xa-discovery.json` records raw
sector hashes, PCM hashes, sample counts, exact zero tails and 100 ms amplitude
windows. The long container durations are mostly padding: all DEMOXA channels
have **35.0144..35.1059 seconds of exact PCM zero tail**, with last nonzero sample
at 1.2312..7.7129 seconds; FINISH has **30.0176..30.2130 seconds of exact zero
tail**, with last nonzero sample at 0.2757..3.8652 seconds. FINISH channels 5/11
are PCM-identical, as are 12/16. DEMOXA02 channels 6/13 and 7/14 are PCM-identical.
The padding must not be mistaken for long musical content, or removed from disc
allocations. Amplitude and caller evidence do not establish transcript, speech
versus effect content, or whether a short cue contains music. Local offline
transcription later supplied speech/technique-name hypotheses; these are
research aids, not accepted transcripts or voice-only proof. FuniDub now
curates 46 script-associated channels with explicit generic-context mappings.
FINISH17 retains its original for the timing reason below; the seven
unreferenced channels remain original. Describing every retained XA as music,
or claiming all original audio has been replaced, is unsupported.

### Character 17 FINISH timing qualification

Character 17/state 171 switches FINISH channel 17 to DEMOXA03 channel 1
(event `0x53`) after **11 normal interpreter advances**. BTCHARA at
`0x88FB24` begins `01200001 00607830 0B2000A9 58607853`:
animation 1, FINISH start, animation `0xA9` with delay 11, then DEMOXA start.
The high byte is a relative countdown for the current command, not an absolute
timestamp or a delay before its side effect. STEP40 `0x8004E65C..0x8004E670`
loads it into `s4`; `0x8004EE18` immediately chains zero-delay commands;
`0x8004EE60..0x8004EE94` clears the pending-command flag at countdown 1 and
decrements it. Thus FINISH and the delay-11 animation execute in one invocation;
DEMOXA starts 11 subsequent advances later. The `0x58` high byte on the DEMOXA
command delays the following command, rather than postponing that XA start.

The interpreter call at `0x80054B84` occurs once per player in the normal combat
loop. Initialization stores 2 at `0x800A9CF4` (`0x800540BC/0x800540DC`);
the loop ends through `0x80055654 -> 0x8003FB40`, which passes that byte to
VSync `0x8001BBEC` at `0x8003FB68..0x8003FB70`. This gives a nominal interval
of **22 VBlanks, about 0.367 seconds** at 60 VBlanks/second (6,930 samples at
18,900 Hz). Pause/skipped updates or slow execution can extend the interval.
This is **not a guaranteed usable PCM budget**: `0x80016DC8` queues seek/start
operations and `0x800172EC` queues the file/channel filter; the script does not
wait for audible start or confirm completion. Their queue-full failure returns
are also ignored here. Static script timing therefore supplies no safe exact
audio sample upper bound. Preserve FINISH channel 17 until usable playback
timing is qualified; its 1.0835-second nonzero source window is not that budget.

The shortest complete same-form donor attack grunt currently inventoried is
BT3 US1 bank 3337, wave 18: 4,760 first-end samples at 16,000 Hz (0.2975 seconds),
terminal flag 1, no loop. Even this does not prove a safe fit after native CD
latency. The ignored receipt `analysis/funidub-original-discovery/xa-finish17-timing.json`
records source hashes, exact words, instruction guards and the selected-gap
reason.

Separate BGM control is visible in the same script: opcode `0x62` after the
DEMOXA command sets volume 30 on resident sequence handles `0x80034F98/9A`
through `0x80013800` (`0x8004EB10..0x8004EB78`). Those handles originate from
sequenced-music calls to `0x8001400C`, including `0x800542E4/0x8006A3EC`.
This supports an inference that attack XA accompanies separately sequenced BGM;
it does **not** prove that any XA PCM is voice-only or lacks embedded effects.

## Guards and remaining qualification

A final bounded shared-bank audit regenerated the common BTCHARA and both
VABDATA tables. The resident 19-sample bank has nine looping waveforms, varied
base notes and sequenced-music callers; replacing these as dialogue is
unsupported. Twenty-two finite common-combat/menu candidates were decoded for
local research. No confirmed omitted spoken announcer/menu cue emerged.
Common waves 13/14 (events `1F/20`) remain possible nonverbal vocals versus
effects; their shared, repetitive use across characters supports preserving
them, not a claim they contain no voice. Menu instrument 3 lacks a recovered
direct caller, so its note-60 decode is a reference pitch only. Ignored receipts
live in `build-audio-review/local-asr/shared-audit/`; blank model output is not
proof of speech absence. No shared-bank replacement was added from this audit.

The local inventory guards exact resident lookup/KEYON instructions, pitch
table, overlay call sites and all three sector tables by SHA-256 and raw words.
Useful opcode checks include `0x80013B20=0x27BDFF88`,
`0x80013B94=0x92220001`, `0x80052190=0x24023C00`,
`0x8005219C=0x24024E39`, `0x8004FFB0=0x24023C00`,
`0x8004FFBC=0x24024800`; all three cited attribute calls use `0x0C00689D`.
Require matching disc/overlay identity and complete table/content bounds, not
one opcode alone. The sample offsets were additionally checked by an independent
body search requiring every ADPCM frame and sample terminal to be valid.
Negative controls reject the mixed CHARSEL and STEP40 prefixes as audio.

Stable local IDs are `btchara/cNN/waveNN`, `charsel/cNN/variantN`, and
`btwinv/cNN/conditionN`, always accompanied by file offset/hash. Character names,
voice/effect listening classification, donor mapping, and runtime acceptance
remain explicit qualification steps. In particular, compilation and static
table discovery do not prove playback or netplay compatibility.
