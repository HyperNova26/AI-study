#!/usr/bin/env bash
# Show the Go2 training curves (reward, episode length, losses) at http://localhost:6006
set -eo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/isaaclab_env.sh"
cd "$GO2_RUNS_DIR"
exec "$ISAACLAB_ROOT/isaaclab.sh" -p -m tensorboard.main --logdir=logs/rsl_rl/unitree_go2_flat "$@"
