#!/usr/bin/env bash
set -eo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash "$here/../preparation/scripts/run_simulation.sh" headless:=True use_rviz:=False "$@"
