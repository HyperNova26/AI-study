#!/usr/bin/env bash
set -eo pipefail
student_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$student_dir/scripts/env.sh"
exec python3 "$student_dir/navigate_to_goal.py" "$@"
