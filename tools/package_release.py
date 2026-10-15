#!/usr/bin/env python3
"""Stage the compiled Windows game using the framework's shared release helpers.

Never archive an entire developer build: it contains media caches and settings.
This wrapper supplies a title-specific allowlist without invoking an MSYS shell.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
EXE = "DragonBallGTFinalBout_Recompiled.exe"


def shared_module(name: str):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "psxrecomp/tools" / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument("--strip", type=Path, help="native llvm-strip.exe")
    args = parser.parse_args()
    build, output = args.build_dir.resolve(), args.output_dir.resolve()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("VERSION must be a stable semantic version")
    if (build / "psx_game_version.txt").read_text().strip() != version:
        raise ValueError("Rebuild with PSX_GAME_VERSION matching VERSION first")
    if "PSX_HAS_GAME_DISPATCH" not in (build / "build.ninja").read_text():
        raise ValueError("A compiled game build is required, not a setup host")
    if "PSX_DEBUG_TOOLS:BOOL=OFF" not in (build / "CMakeCache.txt").read_text():
        raise ValueError("Rebuild with PSX_DEBUG_TOOLS=OFF for release")

    sdk = os.environ.get("RETCOMM_TOOLCHAIN_DIR") or os.environ.get("PSXRECOMP_TOOLCHAIN_DIR")
    strip = args.strip or (Path(sdk) / "bin/llvm-strip.exe" if sdk else None)
    if strip is None or not strip.is_file():
        raise ValueError("Set RETCOMM_TOOLCHAIN_DIR or pass --strip")
    git = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git/cmd/git.exe"

    def git_bytes(*command: str) -> bytes:
        return subprocess.check_output([str(git), *command], cwd=ROOT)

    name = f"DragonBallGTFinalBoutRecompiled-{version}-windows-x64"
    work = output / f"stage-{version}-{datetime.now():%Y%m%d-%H%M%S-%f}"
    stage = work / "payload"
    stage.mkdir(parents=True, exist_ok=False)
    copy(build / EXE, stage / EXE)
    subprocess.run([str(strip), "--strip-debug", str(stage / EXE)], check=True)
    copy(build / "psx_game_version.txt", stage / "psx_game_version.txt")
    for config in ("game.toml", "game_options.toml"):
        (stage / config).write_bytes(git_bytes("show", f"HEAD:{config}"))
    config = tomllib.loads((stage / "game.toml").read_text(encoding="utf-8"))
    if not config.get("runtime", {}).get("overlay_cache"):
        raise ValueError("Release must enable local overlay caching")
    shutil.copytree(build / "assets", stage / "assets")
    for filename in ("openbios.bin", "OpenBIOS.LICENSE"):
        copy(build / "bios" / filename, stage / "bios" / filename)

    # Give the shared validator a clean catalog input, excluding installed mods,
    # extracted texture packs and personal mod state by construction.
    catalog = work / "catalog-input"
    shutil.copytree(build / "mods/bundled", catalog / "mods/bundled")
    release_stage = shared_module("release_stage")
    release_stage.stage_mods(
        str(catalog), str(stage),
        catalog_manifest=str(build / "psx_mod_catalog_psx-runtime.txt"),
    )
    copy(build / "mods/README.md", stage / "mods/README.md")
    shutil.copytree(
        build / "overlay_toolchain", stage / "overlay_toolchain",
        ignore=shutil.ignore_patterns("compiler.txt", "__pycache__", "*.pyc"),
    )
    for relative in ("python/python.exe", "tcc/tcc.exe", "psxrecomp-game.exe",
                     "psxrecomp-bios.exe", "compile_overlays.py", "bios_module_build.py"):
        if not (stage / "overlay_toolchain" / relative).is_file():
            raise ValueError(f"Portable toolchain is missing {relative}")
    for emitter in ("psxrecomp-game.exe", "psxrecomp-bios.exe"):
        subprocess.run(
            [str(strip), "--strip-debug", str(stage / "overlay_toolchain" / emitter)],
            check=True,
        )
    trace_header = stage / "overlay_toolchain/include/audio_trace.h"
    trace_header.write_bytes(trace_header.read_bytes().replace(
        b"F:/Projects/_audio_round2/ROUND2_PLAN.md", b"the cross-system audio measurement plan"
    ))

    shutil.copytree(ROOT / "psxrecomp/runtime/licenses", stage / "licenses")
    notices = {
        "psxrecomp/LICENSE": "licenses/psxrecomp-LICENSE",
        "psxrecomp/THIRD_PARTY_ATTRIBUTION.md": "licenses/THIRD_PARTY_ATTRIBUTION.md",
        "recomp-ui/LICENSE": "licenses/recomp-ui-LICENSE",
        "recomp-ui/src/third_party/imgui/LICENSE.txt": "licenses/ImGui-LICENSE.txt",
        "psxrecomp/recompiler/lib/rabbitizer/LICENSE": "licenses/rabbitizer-LICENSE",
        "psxrecomp/recompiler/lib/ELFIO/LICENSE.txt": "licenses/ELFIO-LICENSE.txt",
        "psxrecomp/recompiler/lib/fmt/LICENSE.rst": "licenses/fmt-LICENSE.rst",
        "recomp-ui/assets/common/fonts/NOTICE.md": "assets/fonts/NOTICE.md",
        "recomp-ui/assets/common/img/NOTICE.md": "assets/img/NOTICE.md",
    }
    for source, destination in notices.items():
        copy(ROOT / source, stage / destination)
    for directory in ("saves",):
        (stage / directory).mkdir()
    (stage / "README.txt").write_bytes(f"""Dragon Ball GT: Final Bout Recompiled {version}
Windows x64

Extract the entire ZIP, then run {EXE}.
Select your own USA Final Bout CUE + BIN image (SLUS-00493) when prompted.
OpenBIOS and portable setup tools are included. No compiler installation is needed.
First use compiles and caches overlays locally from your disc.

Mods > Display > Widescreen: enable Adaptive framing through 21:9.
Mods > Audio > FuniDub: enable and select your own USA PS2 Budokai Tenkaichi 3
ISO (SLUS-21678). Import once, then reuse the locally cached voices.
NETPLAY: online lobbies or LAN / Direct IP. Both players use the same release
and compatible disc/mod content; each prepares FuniDub locally if enabled.

No game media, prepared voice recordings or saves are included.
Third-party notices are in licenses/ and bios/OpenBIOS.LICENSE.
Help, screenshots and known limitations:
https://github.com/mstan/DragonBallGTFinalBoutRecomp
""".encode("utf-8"))
    copy(ROOT / f"docs/RELEASE_NOTES_{version}.md", stage / "RELEASE_NOTES.md")
    release_stage.stage_execution(
        str(stage / EXE), manifest=str(build / EXE.replace(".exe", ".execution.json"))
    )
    files = sorted(p for p in stage.rglob("*") if p.is_file())
    for path in files:
        rel = path.relative_to(stage).as_posix()
        if path.is_symlink() or path.suffix.lower() in {
            ".cue", ".iso", ".img", ".chd", ".mcd", ".mcr", ".pst", ".pack",
            ".wav", ".mp3", ".ogg", ".flac", ".log",
        }:
            raise ValueError(f"Forbidden release payload: {rel}")
        if path.suffix.lower() == ".bin" and rel != "bios/openbios.bin":
            raise ValueError(f"Unexpected binary media: {rel}")
        if path.name in {"compiler.txt", "settings.toml", "state.toml", "disc.cfg", "bios.cfg"}:
            raise ValueError(f"Personal configuration leaked into package: {rel}")
        if path.suffix.lower() == ".c" and not rel.startswith("overlay_toolchain/"):
            raise ValueError(f"Generated game code in package: {rel}")
    manifest = {
        "version": version,
        "source_revision": git_bytes("rev-parse", "HEAD").decode().strip(),
        "files": {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in files},
    }
    (stage / "release-manifest.json").write_bytes(
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    archive = output / f"{name}.zip"
    if archive.exists():
        raise FileExistsError(f"Refusing to overwrite release artifact: {archive}")
    shared_module("create_release_zip").create_release_zip(stage, archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS.txt").write_bytes(f"{digest}  {archive.name}\n".encode("ascii"))
    print(json.dumps({"stage": str(stage), "archive": str(archive), "sha256": digest}, indent=2))


if __name__ == "__main__":
    main()
