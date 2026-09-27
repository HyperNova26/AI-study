#!/usr/bin/env bash
set -eo pipefail
student_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$student_dir/scripts/env.sh"
exec ros2 launch "$student_dir/launch/submission.launch.py" "$@"
