# FuniDub

FuniDub prepares recorded English BT3 voices locally from the user's USA
Budokai Tenkaichi 3 ISO. No audio is downloaded or distributed with this project,
and no voices are generated or cloned. Both supplied images remain unchanged.

## Use and current status

The optional **Audio / FuniDub** feature is in the launcher's Mods page. Enable
it, choose the supported BT3 USA ISO, then prepare/launch. Preparation reports
progress and supports cancellation between work units. A verified cache is
reused; missing or corrupt content is rebuilt. Disable the feature to restore
original recordings. FuniDub uses separate save slots because the samples are
loaded into guest SPU memory. Disabling it returns to the ordinary slots;
memory cards are shared. There is no automatic import between these slots.

The native builder, paired launcher and generated-game build pass local checks.
The launcher displays the selected source and preparation progress/Cancel, and
closing during preparation joins safely. A representative Goku/Boo combat run
contains replacement bytes from both banks in SPU memory; save/load succeeds.
That diagnostic run used a 30-second watchdog allowance after both mod-on and
mod-off default-watchdog runs stalled. This does not establish default-runtime
performance acceptance or a fix for the separately tracked stall. A brief
two-peer gate admits matching packs and rejects FuniDub-on/off at frame zero.
The final build also passes a fresh save/load in its isolated slots and returns
to ordinary paths with FuniDub disabled. Listening review and broader cue
coverage remain open.

## Coverage and substitutions

Recipe 0.1.0 replaces **290 of 323 selected SPU candidates**: 159 combat sounds,
89 menu introductions and 42 victory cues. Another 21 menu and 12 victory slots
keep original audio because the current intact donor candidates do not fit their
original playback capacity. This denominator excludes other unclassified sounds.

The 54 XA attack-channel groups remain original pending a short content review.
Their long container durations mostly comprise trailing silence. Character 0's
additional instrument 13, Piccolo's differently pitched instrument 7, looping
and shared effects, movie/tournament audio and unclassified sounds remain
original. This is partial coverage, not a complete English redub.

Thirteen additions use intact shorter recordings: earlier-era Super Saiyan
Vegeta, sword-variant Super Saiyan Trunks, full-power Frieza and five complete
Kid Boo exertions used in menu/victory scenes. Those form/context substitutions
are explicit candidates for listening review. The first 277 cue edits are
unchanged.

The owner permits suitable generic introductions, victory lines and grunts.
Mappings therefore describe generic context substitutions, not literal dialogue
matches. Adult GT Goku uses BT3 Goku (End). Super Little Goku's ordinary short
donor bank is silent and reuses GT base Goku recordings. Every such form/era
substitution is recorded in the recipe. Character 4's native wave 2 serves both
an attack and ki-charge event; its one replacement remains a shared nonverbal
exertion and both uses need the same listening review.

Individual phrase transcripts, performer identities and all in-game edits have
not been independently accepted. The owner's earlier sample-reel approval
establishes donor sound quality for those examples, not every mapped event.

## Reproducible content

Only the manifest, source hashes and sample-based edit recipe ship in
`mods/preloaded/packages/finalbout.audio.funidub/0.1.0/`. The portable native
builder validates the target resources, donor PVD/AFS tables and every used
payload, decodes ADX/SPU with integer arithmetic, resamples at the exact original
SPU pitch, applies recorded gain/trims/fades and preserves each original ADPCM
flag byte and encoded extent. It pads unused playback capacity with silence.
Intact spoken phrases never get cut to force a fit.

The current output is 14,563,328 bytes, SHA-256
`20af0a00107eec23d870da7848f7553826c61f364ca85a3f163aa2075942b428`.
Local verification found 290 nonzero changed cues, unchanged unmapped bytes,
unchanged ADPCM flags and no PCM rail samples after conversion. Four real ADX
decodes match FFmpeg 7.1 at their declared sample counts. The end-user builder
does not require Python or FFmpeg.

Cached preparation verifies the pack's fixed SHA-256 and all selected source
payloads before reusing encoded bytes when no qualified file stamp is available.
Windows timestamp-only identities are deliberately unqualified after rapid
rewrite collisions were reproduced; no cheap receipt probe claims readiness
there. Source-verified pack reuse measured 662 ms in the native provider check,
versus 15,007 ms for that run's cold preparation. This measures preparation,
not game CD loading. HLE/precaching remains parked.

The framework verifies the exact target-disc identity and stock ranges before
installing three immutable resource-backed logical-disc overlays. Prepared
bytes participate in the normal content fingerprint. No runtime voice hook,
host-only resimulation playback or donor path enters gameplay. Online use must
follow verified content-plan negotiation; it is not cosmetic-only.

Developer tools under `tools/audio/` reproduce inventory, curation and native
pack preparation. See the two table reports for source coordinates, primary
BT3 call-site evidence and remaining interpretation limits. Local media,
inventory JSONs, PCM, built packs and audition reels stay under ignored
`analysis/` or build directories.
