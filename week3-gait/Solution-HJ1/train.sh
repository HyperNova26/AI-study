#!/usr/bin/env bash
# Example training run for week 3 (operator example, HJ1).
#
# Changes from the default Go2 flat task, chosen for keyboard teleop in the maze:
#   heading_command=False   teleop sends a yaw rate (angular.z), not a target heading, so train on
#                           directly sampled yaw-rate commands instead of heading-derived ones.
#   rel_standing_envs=0.1   teleop often commands zero ("k" or the 0.5 s watchdog); 10% instead of
#                           2% of robots practise standing still.
#   --max_iterations 500    longer than the default 300, to compensate for the harder command mix.
# Observation (48) and action (12) definitions are unchanged, so the policy still fits the maze runner.
#
# Resume: bash train.sh --resume --load_run <date>_<time>_hj1 --checkpoint model_499.pt
set -eo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# --export_io_descriptors writes into the new run folder before a resume checkpoint is looked up,
# which would make the new, empty folder the newest match. Only use it for fresh runs.
io_descriptors=(--export_io_descriptors)
for arg in "$@"; do
    [[ "$arg" == --resume ]] && io_descriptors=()
done
exec bash "$here/../preparation/scripts/train_go2_flat.sh" \
    --run_name hj1 \
    --max_iterations 500 \
    "${io_descriptors[@]}" \
    env.commands.base_velocity.heading_command=False \
    env.commands.base_velocity.rel_standing_envs=0.1 \
    "$@"
