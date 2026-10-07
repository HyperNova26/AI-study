#!/usr/bin/env bash
set -eo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/env.sh"
exec ros2 launch "$script_dir/../launch/simulation.launch.py" "$@"
