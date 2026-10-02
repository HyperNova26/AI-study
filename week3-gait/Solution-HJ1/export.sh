#!/usr/bin/env bash
# Export the final checkpoint of the newest "hj1" run to policy/policy.pt and record where it came from.
# Usage: bash export.sh [path/to/model_<iter>.pt]
set -eo pipefail
shopt -s nullglob
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
runs="${GO2_RUNS_DIR:-$HOME/aistudy_go2_runs}/logs/rsl_rl/unitree_go2_flat"
checkpoint="${1:-}"
if [[ -z "$checkpoint" ]]; then
    # Run folders are named <date>_<time>_hj1, so the glob is in time order. Skip folders without
    # checkpoints (an interrupted or failed start leaves an empty run folder).
    candidates=("$runs"/*_hj1)
    for (( i = ${#candidates[@]} - 1; i >= 0; i-- )); do
        models=("${candidates[i]}"/model_*.pt)
        if (( ${#models[@]} > 0 )); then
            checkpoint="$(printf '%s\n' "${models[@]}" | sort -V | tail -1)"
            break
        fi
    done
    if [[ -z "$checkpoint" ]]; then
        printf '체크포인트가 있는 학습 결과가 없습니다: %s/*_hj1\n' "$runs" >&2
        exit 1
    fi
fi
bash "$here/../preparation/scripts/export_policy.sh" "$checkpoint" "$here/policy/policy.pt"

run_dir="$(dirname "$(realpath "$checkpoint")")"
{
    printf '# policy.pt 출처\n\n'
    printf -- '- run: `%s`\n' "$(basename "$run_dir")"
    printf -- '- checkpoint: `%s`\n' "$(basename "$checkpoint")"
    printf -- '- sha256: `%s`\n' "$(sha256sum "$here/policy/policy.pt" | cut -d' ' -f1)"
    printf -- '- exported: %s\n' "$(date '+%Y-%m-%d %H:%M')"
} > "$here/policy/policy_info.md"
# The I/O description written by --export_io_descriptors documents the observation and action layout.
if [[ -f "$run_dir/io_descriptors/IO_descriptors.yaml" ]]; then
    cp "$run_dir/io_descriptors/IO_descriptors.yaml" "$here/policy/IO_descriptors.yaml"
fi
cp "$run_dir/params/env.yaml" "$here/policy/train_env.yaml"
cp "$run_dir/params/agent.yaml" "$here/policy/train_agent.yaml"
printf '기록: %s/policy/\n' "$here"
