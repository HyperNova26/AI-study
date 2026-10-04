#!/usr/bin/env bash
# Usage: ROS_DOMAIN_ID=44 bash scripts/run_replay.sh BAG CONFIG OUTPUT_DIR
set -eo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$here/../preparation/scripts/env.sh"
exec python3 "$here/tools/replay_experiment.py" "$@"
