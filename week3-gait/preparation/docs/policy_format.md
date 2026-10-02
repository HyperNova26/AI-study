# 제출할 실행용 `.pt` 정책 형식

과제의 "본인이 학습하여 내보낸 실행용 `.pt` 정책 파일"은 `isaaclab.sh play`가 만드는 **`<run>/exported/policy.pt` 파일**입니다. 학습 중 저장되는 `model_<iter>.pt`는 이어서 학습하기 위한 파일이라 제출 대상이 아닙니다.

## 두 `.pt`의 차이

| | 학습 체크포인트 `model_<iter>.pt` | 실행용 정책 `exported/policy.pt` |
| --- | --- | --- |
| 만드는 곳 | 학습 중 50 iteration마다 | play가 체크포인트를 불러온 직후 |
| 저장 방식 | `torch.save(dict)` | TorchScript (`torch.jit.script(...).save`) |
| 내용 | `actor_state_dict`, `critic_state_dict`, `optimizer_state_dict`, `iter`, `infos` | actor 신경망 + 관측 정규화 + 결정적 출력(평균)만 |
| 불러오기 | `OnPolicyRunner`와 같은 학습기 설정이 필요 | `torch.jit.load`만 있으면 됨 |
| 용도 | 이어서 학습, 다시 내보내기 | 실행·배포 |

## 실행용 정책의 입출력

| 항목 | 값 (Go2 평지 기본 설정) |
| --- | --- |
| 모듈 | `_TorchMLPModel` (RSL-RL 5.0.1) |
| 입력 | `float32` 텐서 하나, 크기 `[N, 48]` — 관측 그룹 `"policy"` 그대로 ([rl_basics.md](rl_basics.md)의 순서) |
| 출력 | `float32` 텐서, 크기 `[N, 12]` — 관절 위치 행동 (환경이 `기본 각도 + 0.25 × 출력`으로 변환) |
| 동작 | 같은 입력에 항상 같은 출력 (확률적 샘플링 없음), 내부 상태 없음 (`reset()`은 인자 없이 아무것도 안 함) |
| 신경망 | `mlp.0.weight [128, 48]` → `mlp.2 [128, 128]` → `mlp.4 [128, 128]` → `mlp.6 [12, 128]`, ELU |
| 크기 | 파라미터 40,844개, 파일 약 170 KiB — 저장소에 커밋해도 되는 크기 |
| 장치 | CPU로 저장됨 → `map_location=env.unwrapped.device`로 불러오기 |

정책은 **관측을 만들거나 행동을 관절 각도로 바꾸지 않습니다**. 그 일은 Isaac Lab 환경(`Go2MazeEnvCfg`)이 하므로, 학습과 같은 관측·행동 설정의 환경에서 실행해야 같은 동작이 나옵니다. `policy(obs)`처럼 TensorDict를 그대로 넣으면 TorchScript 형식 오류가 나므로 `policy(obs["policy"])`로 호출합니다.

## 확인 방법

```bash
${ISAACLAB_ROOT:-$HOME/IsaacLab}/isaaclab.sh -p tools/inspect_policy.py ../본인폴더/policy/policy.pt
```

정상 출력 예 (RSL-RL 5.0.1 내보내기 코드로 만든 같은 구조의 정책):

```text
file: ../본인폴더/policy/policy.pt (171.5 KiB, sha256 <앞 16자리>)
TorchScript module: _TorchMLPModel, parameters: 40,844
  mlp.0.weight: [128, 48]
  mlp.2.weight: [128, 128]
  mlp.4.weight: [128, 128]
  mlp.6.weight: [12, 128]
observation normalizer: none (Identity)
forward([1, 48]) -> [1, 12], finite=True
forward([8, 48]) -> [8, 12], finite=True
OK: 실행용 정책 형식입니다 (TorchScript, 입력 1개, 결정적 출력).
```

`model_<iter>.pt`를 넣으면 "학습 체크포인트입니다"라고 알려 줍니다. 신경망 크기를 바꿨다면 층 크기가 달라지는 것은 정상입니다. 입력이 48이 아니면 Flat 작업으로 학습했는지 확인합니다.

## 제출 방법

```text
week3-gait/본인이름/
├── policy/
│   ├── policy.pt          # exported/policy.pt를 복사
│   └── policy_info.md     # 원본 run 폴더, 체크포인트 iteration, sha256, 학습 명령 (선택)
└── README.md              # 정책 불러오는 명령: run_teleop_policy.sh --policy policy/policy.pt
```

- `exported/policy.pt`는 play를 다시 실행하면 덮어써집니다. 제출할 파일을 정한 뒤 복사하고, 어떤 체크포인트에서 만들었는지 기록하세요.
- 약 170 KiB이므로 일반 커밋으로 올립니다. `logs/` 폴더 전체나 `model_*.pt` 여러 개는 올리지 않습니다.
- `policy.onnx`는 다른 실행 환경(ONNX Runtime 등)용이며 이번 제출물은 아닙니다.
