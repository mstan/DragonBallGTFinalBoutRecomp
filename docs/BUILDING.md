# Building from source

The downloadable Windows release includes its runtime setup tools. These
instructions are for developers building the repository itself.

Use the pinned framework's [setup guide](https://github.com/RetroPortingToolKit/psxrecomp/blob/c91331ff67c8797a5c0a74332e019f143bdb0270/docs/GAME_PROJECT_SETUP.md)
and [local codegen contract](https://github.com/RetroPortingToolKit/psxrecomp/blob/c91331ff67c8797a5c0a74332e019f143bdb0270/docs/LOCAL_CODEGEN_SDK.md). Initialize
the committed dependencies from the repository root:

```powershell
& "$env:ProgramFiles\Git\cmd\git.exe" submodule update --init --recursive
```

Provide your own USA Final Bout CUE + BIN image, serial **SLUS-00493**.
The configured single-track image has MD5 `2f869f926514278b72ffbd671e69b9f7`
and SHA-1 `8a2373f133788256cba64a1a0ba9fbb4b4667f71`. These identify the
tested source, not an independent dump-database certification.

## Windows generation and build

Install the native RetComM `cmake-clang-v1` toolchain, version `1.0.14`, and
native Python 3.12. Adjust the paths below to your installations. Run from
the repository root:

```powershell
$env:RETCOMM_TOOLCHAIN_DIR = "$env:LOCALAPPDATA\RetComM\toolchains\cmake-clang-v1\1.0.14"
$env:PSXRECOMP_TOOLCHAIN_DIR = $env:RETCOMM_TOOLCHAIN_DIR
$env:CMAKE_BUILD_PARALLEL_LEVEL = '2'
$nativePython = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
& $nativePython psxrecomp/psxrecomp_cli.py generate --config game.toml --project-root . --disc 'disc/Dragon Ball GT - Final Bout (USA).cue'
& $nativePython psxrecomp/psxrecomp_cli.py rebuild --config game.toml --project-root . --build-dir build-release --no-pgo --cmake-extra=-DPSX_DEBUG_TOOLS=OFF --cmake-extra=-DPSX_GAME_VERSION=1.0.0
```

Use explicit native executables when PATH contains MSYS/Cygwin shims.
`RETCOMM_TOOLCHAIN_DIR` takes precedence over `PSXRECOMP_TOOLCHAIN_DIR`, so set
both. The CLI rebuild stages the overlay toolchain beside the executable;
a manual CMake build alone does not prepare that runtime path. Enable
`PSX_DEBUG_TOOLS` only for diagnostic builds.

## Release packaging

After building the matching version, run the native packaging helper:

```powershell
& $nativePython tools/package_release.py --build-dir build-release --output-dir dist
```

It stages a clean Windows x64 payload, strips the staged executable, binds its
execution manifest, verifies the bundled mod catalog and writes a ZIP plus
SHA-256 checksums. It uses committed runtime configuration, not personal
settings from the build directory. The package includes OpenBIOS, notices,
and the portable overlay toolchain; overlays compile locally from the
player's disc. It excludes disc images, prepared audio, saves and generated
game code. Check the extracted package with a fresh cache and without the
developer SDK before publishing.

## Repository layout

- `game.toml`, `catalog_identity.json`, `disc_probe.json`: title and disc identity.
- `seeds/`, `symbols.toml`, `psx_symbols.h`: discovery and symbol map.
- `psxrecomp/`, `recomp-ui/`: pinned submodules; recomp-net is nested.
- `src/mods/`, `src/audio/`, `mods/preloaded/`: title plugins and FuniDub recipes.
- `docs/`, `validation/`: design, provenance and validation evidence.
- `disc/`, `generated/`, `build*/`, `analysis/`, `local-media/`: ignored local data.

Keep game dumps, generated game C, retail BIOS, Ghidra databases, extracted
assets and audio out of commits. The selected gameplay screenshots in
`docs/screenshots/` are documentation images. See [AGENTS.md](../AGENTS.md)
for engineering and central issue-tracking instructions.
