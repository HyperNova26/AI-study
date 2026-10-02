#!/usr/bin/env bash
# Train the Isaac Lab Go2 flat velocity-tracking task with RSL-RL PPO.
# The flat task has the same 48-D observation and 12-D action as the week-2 maze runner.
#
#   bash scripts/train_go2_flat.sh --run_name myname                      # default settings
#   bash scripts/train_go2_flat.sh --run_name myname --max_iterations 500 \
#        env.commands.base_velocity.rel_standing_envs=0.1                  # with overrides
#
# Output: $GO2_RUNS_DIR/logs/rsl_rl/unitree_go2_flat/<date>_<time>_<run_name>/model_<iter>.pt
set -eo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/isaaclab_env.sh"
cd "$GO2_RUNS_DIR"
printf '학습 로그 위치: %s/logs/rsl_rl/unitree_go2_flat\n' "$GO2_RUNS_DIR"
exec "$ISAACLAB_ROOT/isaaclab.sh" train --rl_library rsl_rl --task Isaac-Velocity-Flat-Unitree-Go2-v0 "$@"
