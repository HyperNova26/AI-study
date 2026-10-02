#!/usr/bin/env bash
# Export a training checkpoint to the runnable TorchScript policy and copy it to a destination.
#
#   bash scripts/export_policy.sh <run_dir>/model_<iter>.pt <destination>/policy.pt [extra play options]
#
# `isaaclab.sh play` loads the checkpoint, writes <run_dir>/exported/policy.pt and policy.onnx, and then
# keeps simulating until stopped. This script waits for the files, stops play (SIGTERM, then SIGKILL after
# 30 s), copies policy.pt and checks it with tools/inspect_policy.py. Repeat any env./agent. override that
# changed the network or the observations during training: play rebuilds the configuration from the task,
# not from params/.
set -eo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ $# -lt 2 ]]; then
    printf '사용법: bash scripts/export_policy.sh <model_<iter>.pt> <저장할 policy.pt> [play 옵션...]\n' >&2
    exit 2
fi
checkpoint="$(realpath "$1")"
destination="$(realpath -m "$2")"
shift 2
[[ -f "$checkpoint" ]] || { printf '체크포인트가 없습니다: %s\n' "$checkpoint" >&2; exit 1; }
source "$script_dir/isaaclab_env.sh"

exported="$(dirname "$checkpoint")/exported/policy.pt"
start="$(date +%s)"
cd "$GO2_RUNS_DIR"
# A separate process group lets us stop play and its child processes together.
setsid "$ISAACLAB_ROOT/isaaclab.sh" play --rl_library rsl_rl --task Isaac-Velocity-Flat-Unitree-Go2-Play-v0 \
    --num_envs 1 --checkpoint "$checkpoint" "$@" &
play_pid=$!
# A script's background jobs start with SIGINT ignored, so Ctrl+C-style stopping cannot work here.
# Isaac Lab's AppLauncher handles SIGTERM; SIGKILL is the fallback if Kit does not shut down.
stop_play() {
    kill -TERM -- "-$play_pid" 2>/dev/null || return 0
    for _ in $(seq 30); do
        kill -0 -- "-$play_pid" 2>/dev/null || return 0
        sleep 1
    done
    kill -KILL -- "-$play_pid" 2>/dev/null || true
}
# Also runs if this script is interrupted, so Isaac Sim is never left running in the background.
trap stop_play EXIT

fresh() { [[ -f "$1" && "$(stat -c %Y "$1")" -ge "$start" ]]; }
while kill -0 "$play_pid" 2>/dev/null; do
    if fresh "$exported" && fresh "$(dirname "$exported")/policy.onnx"; then
        sleep 2
        break
    fi
    sleep 2
done
stop_play
wait "$play_pid" 2>/dev/null || true
trap - EXIT

if ! fresh "$exported"; then
    printf '내보내기 실패: %s 이 생성되지 않았습니다. play 출력을 확인하세요.\n' "$exported" >&2
    exit 1
fi
mkdir -p "$(dirname "$destination")"
cp "$exported" "$destination"
printf '\n복사 완료: %s -> %s\n' "$exported" "$destination"
"$ISAACLAB_ROOT/isaaclab.sh" -p "$script_dir/../tools/inspect_policy.py" "$destination"
