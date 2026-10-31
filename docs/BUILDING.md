# Building from source

The downloadable Windows release includes OpenBIOS and portable local overlay
setup tools. Source developers use the pinned shared release builder and the
title recipe in `packaging/release.toml`.

Initialize the committed dependencies from the repository root:

```powershell
& "$env:ProgramFiles\Git\cmd\git.exe" submodule update --init --recursive
```

Provide your own USA Final Bout CUE + BIN image, serial **SLUS-00493**.
The configured single-track image has MD5 `2f869f926514278b72ffbd671e69b9f7`
and SHA-1 `8a2373f133788256cba64a1a0ba9fbb4b4667f71`. These identify the
tested source, not an independent dump-database certification.

## Windows release

With native Python 3.12+, CMake, Ninja and the supported native MinGW toolchain
installed, keep the original CUE and BIN together under `disc/` with the names
declared in `game.toml`. Extract the original boot executable using the shared
disc probe, then invoke the shared builder from this title's repository root:

```powershell
python psxrecomp/tools/new_project_layout/probe_disc.py `
  'disc/Dragon Ball GT - Final Bout (USA).cue' --write-boot-exe disc
& psxrecomp/tools/package_title_release.ps1 --channel public --platform windows --jobs 2
```

The builder regenerates the game from the disc, builds both emitters, uses
fresh per-title selective runtime PGO on supported GNU/Ninja builds, and
verifies the clean public package. It requires real muted boot training and
normal close before the strict use build. Training does not establish gameplay
coverage or a per-title performance gain. Compiler/profile data is not shipped.
Other toolchains must truthfully record their portable unprofiled path.

`scripts/package_release.sh` delegates to the same builder; it accepts the
shared command's options rather than the retired prebuilt-build-directory
arguments. See the pinned engine's `docs/RELEASING_A_TITLE.md` for toolchain,
output-directory and package-verification options. No title-specific packager
or blanket developer-build archive is used.

The public ZIP includes the compiled game, bundled OpenBIOS, reviewed mod
catalog, notices and portable overlay toolchain. It excludes disc images,
prepared voice recordings, settings, native saves and disposable snapshots.
CD Speed and Fast Loading packages are excluded. The player config preserves
digital-pad enforcement, local overlay caching, netplay and title widescreen
hooks. Fresh resolution selection comes from the shared 4x mod, with bounded
1x through 32x choices.

## Dependency and feature preservation

The engine pin is the reviewed shared master. The recomp-ui pin
`1f55b10858ac0118bf89fbc5274f39d816ec78c5` merges current shared UI `3f1d6f1`
with Final Bout's original `1fa1f24` owned preparation progress and cooperative
cancellation. This retains the current native memory-card exclusive-create
safety fix, shared settings behavior and full Internal Resolution mod selector.
Do not replace that UI with a revision lacking
`RECOMP_LAUNCHER_HAS_MOD_PREPARATION_PROGRESS`. The engine keeps that optional
bridge. FuniDub's native builder, verified
recipe/output identities, cache and original-audio fallback are unchanged.

Keep game dumps, generated game C, retail BIOS, extracted audio and packs out
of commits. Read [AGENTS.md](../AGENTS.md) for central tracking and scoped QA.
