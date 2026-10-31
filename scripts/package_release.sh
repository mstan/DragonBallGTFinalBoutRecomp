#!/usr/bin/env bash
# Official releases use the pinned shared builder and packaging/release.toml.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"
exec "${PYTHON:-python3}" "${ROOT}/psxrecomp/tools/package_title_release.py" "$@"
