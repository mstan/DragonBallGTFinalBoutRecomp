# Dragon Ball GT: Final Bout Recompiled

Initial native recompilation project for **Dragon Ball GT - Final Bout (USA)**,
serial **SLUS-00493**, using pinned PSXRecomp and recomp-ui dependencies.

This repository is at initial bring-up. A project scaffold, renderer setting,
or compiled netplay integration does not establish playable-game compatibility.
The Windows build and opening movie passed. A later check reached the menus,
character selection and Goku-versus-Piccolo screen, then guest execution ended
unexpectedly before a fight was validated. Combat, saves, audible audio and
multiplayer remain unvalidated; this is not yet a qualified playable port.
See [validation/README.md](validation/README.md) for the actual validation result.
No public repository or release has been created.

The requested scope is higher internal resolution, faster loading through HLE
and precaching, adaptive widescreen, and two-player recomp-net. Original dialogue
extraction is the penultimate phase; an optional Funimation-cast voice pack
assembled from existing recordings is the final phase. No generated or cloned
voices are part of the plan.

## Configuration and tracked work

The initial renderer target is OpenGL at the shared `1080p` internal-resolution
preset. Initial framing remains 4:3 until Final Bout's adaptive view is implemented
and validated. Two-player netplay and the setup UI are enabled for bring-up.
These settings do not certify graphics, multiplayer, or performance results.

Requirements and acceptance checks are in
[docs/PROJECT_REQUIREMENTS.md](docs/PROJECT_REQUIREMENTS.md).
[docs/VOICE_REPLACEMENT.md](docs/VOICE_REPLACEMENT.md) records the deferred audio
workflow and provenance rules. The central Beads epic is **beads-6058**; the
initial setup issue is **beads-jsz8**. No per-repository Beads database is used.
The owner's Brazilian redub and NovaPowers Ghidra/profile references are recorded
with review findings in [docs/REFERENCE_NOTES.md](docs/REFERENCE_NOTES.md).

## Local source

The owner-supplied source is:

```text
\\SERVER\Games\PSX\Dragon Ball GT - Final Bout (USA)\Dragon Ball GT - Final Bout (USA).cue
```

The disc is a single MODE2/2352 data track, 158,811,744 bytes. Independent source
verification found MD5 `2f869f926514278b72ffbd671e69b9f7` and SHA-1
`8a2373f133788256cba64a1a0ba9fbb4b4667f71`. The boot executable is
`SLUS_004.93`, load address `0x80010000`, entry `0x80010B98`, and text size
`0x0002E000`. The probe records this supplied image's identity; it is not an
external dump-database certification.

Disc data and the extracted boot executable remain local under ignored `disc/`.
No dialogue or other game audio has been extracted. The owner supplied a BT3
USA PS2 ISO and research ZIP for the eventual **FuniDub** feature. Its intended
launcher flow is to choose the donor ISO and prepare a local mapped voice pack
automatically. The [research audit](docs/FUNIDUB_RESEARCH.md) records verified
metadata and mapping leads; audio implementation still follows core validation.

## Development

Use the pinned framework's [setup guide](psxrecomp/docs/GAME_PROJECT_SETUP.md)
and [local codegen contract](psxrecomp/docs/LOCAL_CODEGEN_SDK.md). Initialize
committed dependencies with:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' submodule update --init --recursive
```

Generate and build from the repository root using native Python and the installed
RetComM toolchain:

```powershell
$env:RETCOMM_TOOLCHAIN_DIR = 'C:\Users\Matthew\AppData\Local\RetComM\toolchains\cmake-clang-v1\1.0.14'
$env:PSXRECOMP_TOOLCHAIN_DIR = $env:RETCOMM_TOOLCHAIN_DIR
$env:CMAKE_BUILD_PARALLEL_LEVEL = '2'
& 'C:\Users\Matthew\AppData\Local\Programs\Python\Python312\python.exe' psxrecomp/psxrecomp_cli.py generate --config game.toml --project-root . --disc "disc/Dragon Ball GT - Final Bout (USA).cue"
& 'C:\Users\Matthew\AppData\Local\Programs\Python\Python312\python.exe' psxrecomp/psxrecomp_cli.py rebuild --config game.toml --project-root . --build-dir build-release --no-pgo --cmake-extra=-DPSX_DEBUG_TOOLS=ON
```

On this machine, PATH contains MSYS shims. Prefer the native Python executable
at `C:\Users\Matthew\AppData\Local\Programs\Python\Python312\python.exe`
and native Git at `C:\Program Files\Git\cmd\git.exe`. `RETCOMM_TOOLCHAIN_DIR`
takes precedence over `PSXRECOMP_TOOLCHAIN_DIR`, so set both as shown to avoid
an inherited toolchain override. Adjust these machine-local paths on other PCs.
A build failure or unvalidated runtime is
recorded explicitly in the validation notes.

## Repository layout

- `game.toml`, `catalog_identity.json`, `disc_probe.json`: title and disc identity.
- `seeds/`, `symbols.toml`, `psx_symbols.h`: initial discovery and symbol map.
- `psxrecomp/`, `recomp-ui/`: pinned root submodules; recomp-net is nested.
- `mods/preloaded/`: future title enhancement packages.
- `docs/`, `validation/`: requirements, deferred audio design, and evidence.
- `disc/`, `generated/`, `build*/`, `analysis/`, `local-media/`: local ignored data.

No game dumps, generated game code, retail BIOS, Ghidra databases, or original
and third-party recordings belong in source commits. Version recipes and
annotation exports instead. Dependency gitlinks are authoritative; pin changes
must be deliberate and validated.
