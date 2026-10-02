#!/usr/bin/env python3
"""Check that a .pt file is the runnable Go2 policy expected for the week-3 submission.

Only PyTorch is needed, so it runs with Isaac Lab's Python or any Python that has torch:

    ${ISAACLAB_ROOT}/isaaclab.sh -p tools/inspect_policy.py path/to/policy.pt

A runnable policy is the TorchScript file that `isaaclab.sh play` writes to
<run>/exported/policy.pt: one float tensor [batch, 48] in, joint actions [batch, 12] out.
A training checkpoint (model_<iter>.pt) is a different format; this script says so.
"""

import argparse
import hashlib
import sys
from pathlib import Path

import torch

EXPECTED_OBS = 48  # Isaac-Velocity-Flat-Unitree-Go2: 3+3+3+3+12+12+12
EXPECTED_ACT = 12  # 4 legs x (hip, thigh, calf) joint position actions


def linear_shapes(state_dict):
    """Weights of the Linear layers in order, e.g. mlp.0.weight [128, 48] ... mlp.6.weight [12, 128]."""
    weights = [(name, tensor.shape) for name, tensor in state_dict.items()
               if name.endswith(".weight") and tensor.dim() == 2]
    return sorted(weights, key=lambda item: [int(p) if p.isdigit() else p for p in item[0].split(".")])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("policy", type=Path)
    parser.add_argument("--obs-dim", type=int, default=EXPECTED_OBS)
    parser.add_argument("--act-dim", type=int, default=EXPECTED_ACT)
    args = parser.parse_args()

    if not args.policy.is_file():
        sys.exit(f"파일이 없습니다: {args.policy}")
    digest = hashlib.sha256(args.policy.read_bytes()).hexdigest()
    print(f"file: {args.policy} ({args.policy.stat().st_size / 1024:.1f} KiB, sha256 {digest[:16]})")

    try:
        policy = torch.jit.load(str(args.policy), map_location="cpu")
    except RuntimeError:
        checkpoint = torch.load(str(args.policy), map_location="cpu", weights_only=False)
        if isinstance(checkpoint, dict) and "actor_state_dict" in checkpoint:
            sys.exit("이 파일은 학습 체크포인트(model_<iter>.pt, keys: "
                     f"{', '.join(checkpoint)})입니다.\n"
                     "isaaclab.sh play로 내보낸 <run>/exported/policy.pt를 제출하세요. docs/policy_format.md 참고.")
        sys.exit("TorchScript 정책도, RSL-RL 학습 체크포인트도 아닙니다.")

    policy.eval()
    state = policy.state_dict()
    layers = linear_shapes(state)
    print(f"TorchScript module: {policy.original_name}, parameters: {sum(t.numel() for t in state.values()):,}")
    for name, shape in layers:
        print(f"  {name}: {list(shape)}")
    normalizer = [name for name in state if name.startswith("obs_normalizer.")]
    print("observation normalizer:", ", ".join(normalizer) if normalizer else "none (Identity)")

    obs_dim = layers[0][1][1] if layers else args.obs_dim
    if obs_dim != args.obs_dim:
        print(f"경고: 입력 차원 {obs_dim} != 기대값 {args.obs_dim}. Flat Go2 작업으로 학습했는지 확인하세요 "
              "(Rough 작업은 height scan 187개가 추가되어 235차원).")
    with torch.inference_mode():
        for batch in (1, 8):
            actions = policy(torch.zeros(batch, obs_dim) if batch == 1 else torch.randn(batch, obs_dim))
            print(f"forward([{batch}, {obs_dim}]) -> {list(actions.shape)}, finite={bool(torch.isfinite(actions).all())}")
        if actions.shape[-1] != args.act_dim:
            sys.exit(f"출력 차원 {actions.shape[-1]} != 기대값 {args.act_dim}")
        policy.reset()  # exported MLP policies are stateless; this must exist and take no arguments
    print("OK: 실행용 정책 형식입니다 (TorchScript, 입력 1개, 결정적 출력).")


if __name__ == "__main__":
    main()
