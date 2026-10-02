# 3주차 보행팀 제공 자료 — Go2 보행 정책 학습·내보내기·미로 적용

[과제 안내](../go2-rl-gait-task.md)의 "제공되는 것"에 해당하는 실행 예제와 교보재입니다. Isaac Lab의 Go2 평지 속도 추종 예제로 정책을 학습하고, 실행용 `.pt`로 내보낸 뒤, 2주차 미로에서 ROS 2 teleop으로 주행합니다. 전체 흐름과 개념은 [3주차 보행팀 안내](../guide.md)를 먼저 읽으세요.

| 과제의 제공 항목 | 이 폴더의 위치 |
| --- | --- |
| 2주차 실행 환경과 호환되는 Go2 학습 예제 및 기본 설정 | [scripts/train_go2_flat.sh](scripts/train_go2_flat.sh), [docs/isaaclab_rslrl.md](docs/isaaclab_rslrl.md) |
| 강화학습 기초, Isaac Lab, RSL-RL 교보재 | [docs/rl_basics.md](docs/rl_basics.md), [docs/isaaclab_rslrl.md](docs/isaaclab_rslrl.md) |
| 정책 학습·저장·내보내기·불러오기 예제 | `train_go2_flat.sh` → [scripts/export_policy.sh](scripts/export_policy.sh) → [tools/inspect_policy.py](tools/inspect_policy.py) → `go2_policy_teleop.py --policy` |
| 학습 정책을 기존 teleop에 연결하는 실행 예제 | [go2_policy_teleop.py](go2_policy_teleop.py), [maze_env_cfg.py](maze_env_cfg.py), [scripts/run_teleop_policy.sh](scripts/run_teleop_policy.sh), [scripts/teleop.sh](scripts/teleop.sh) |
| GPU 사용 환경과 학습 시간 안내 | [docs/gpu_and_time.md](docs/gpu_and_time.md) |
| 제출해야 할 실행용 `.pt` 형식 안내 | [docs/policy_format.md](docs/policy_format.md) |
| teleop 명령이 정책에 전달되는 흐름 | [docs/teleop_flow.md](docs/teleop_flow.md) |

예시 답안은 [Solution-HJ1](../Solution-HJ1/README.md)에 있습니다.

## 기준 환경

2주차 보행팀 제출([week2-gait/ChanwonJung](../../week2-gait/ChanwonJung/README.md))에서 미로 teleop이 동작한 구성을 그대로 사용합니다.

| 항목 | 기준 |
| --- | --- |
| OS / GPU | Ubuntu 24.04, NVIDIA GPU (2주차: RTX 5070 12 GB) |
| Isaac Sim / Isaac Lab | Isaac Sim 6.0.1, Isaac Lab **v3.0.0-beta2** (`ISAACLAB_ROOT`, 기본 `~/IsaacLab`) |
| 강화학습 라이브러리 | RSL-RL **5.0.1** (`isaaclab_rl`이 `rsl-rl-lib==5.0.1`로 고정) |
| Python / PyTorch | Isaac Sim 내장 Python 3.12, Isaac Lab 기준 torch 2.10 |
| 학습 작업 | `Isaac-Velocity-Flat-Unitree-Go2-v0` (내보내기는 `...-Play-v0`) |
| teleop | ROS 2 Jazzy `teleop_twist_keyboard` → `/cmd_vel`, 시뮬레이터 쪽은 Isaac Sim 내장 rclpy |

Isaac Lab 3.0은 학습·실행이 기본적으로 **화면 없이(headless)** 진행됩니다. 창을 보려면 `--viz kit`을 붙이고, 미로 실행기는 기본으로 창을 엽니다(`--viz none`으로 끄기). `--headless`는 3.0에서 더 이상 권장하지 않는 옵션입니다.

## 폴더 구성

```text
week3-gait/preparation/
├── go2_policy_teleop.py      # 미로 + Go2 정책 + /cmd_vel 구독 (2주차 실행기에 --policy 추가)
├── maze_env_cfg.py           # 미로 USD·시작 위치를 받는 Go2 평지 PLAY 환경
├── assets/sample_maze.usda   # 연습용 S자 미로 (tools/make_sample_maze.py로 생성)
├── scripts/
│   ├── isaaclab_env.sh       # ISAACLAB_ROOT, 학습 출력 폴더(GO2_RUNS_DIR) 설정
│   ├── train_go2_flat.sh     # 학습
│   ├── tensorboard.sh        # 학습 곡선
│   ├── export_policy.sh      # 체크포인트 → exported/policy.pt → 복사·검사
│   ├── run_teleop_policy.sh  # 미로 실행기 (Isaac Sim 내장 ROS 2 사용)
│   └── teleop.sh             # 키보드 teleop
├── tools/
│   ├── inspect_policy.py     # .pt 형식·입출력 차원 검사 (torch만 필요)
│   └── make_sample_maze.py
└── docs/                     # 교보재
```

학습 로그와 체크포인트는 저장소 밖 `~/aistudy_go2_runs/logs/rsl_rl/unitree_go2_flat/`에 생깁니다(`GO2_RUNS_DIR`로 변경). `isaaclab.sh train`·`play`가 **현재 폴더 기준** `logs/`에 기록하므로 저장소 안에서 실행하면 큰 파일이 커밋 대상이 되기 쉽습니다. 제출할 `policy.pt`만 본인 폴더로 복사합니다.

## 실행 순서

모든 명령은 이 폴더(`week3-gait/preparation`)에서 실행합니다. Isaac Lab 위치가 다르면 앞에 `ISAACLAB_ROOT=/경로/IsaacLab`을 붙입니다.

### 1. 학습

```bash
bash scripts/train_go2_flat.sh --run_name 본인ID
```

기본 설정은 4096개 병렬 환경, 300 iteration입니다. 매 iteration마다 평균 보상, 에피소드 길이, 소요 시간과 남은 시간(ETA)이 출력됩니다. 체크포인트는 50 iteration마다 `model_0.pt`, `model_50.pt`, …, 마지막에 `model_299.pt`로 저장됩니다. `Ctrl+C`로 중단하면 마지막 저장은 생략됩니다. 설정을 바꾸는 방법은 [docs/isaaclab_rslrl.md](docs/isaaclab_rslrl.md), GPU 메모리와 시간은 [docs/gpu_and_time.md](docs/gpu_and_time.md)를 참고하세요.

### 2. 학습 곡선

```bash
bash scripts/tensorboard.sh   # 브라우저에서 http://localhost:6006
```

`Train/mean_reward`, `Train/mean_episode_length`, `Episode_Reward/track_lin_vel_xy_exp` 등을 Notion 학습 기록에 사용합니다.

### 3. 실행용 정책 내보내기

```bash
bash scripts/export_policy.sh \
    ~/aistudy_go2_runs/logs/rsl_rl/unitree_go2_flat/<날짜_시각_본인ID>/model_299.pt \
    ../본인폴더/policy/policy.pt
```

`isaaclab.sh play`가 체크포인트를 불러와 같은 폴더의 `exported/policy.pt`(TorchScript)와 `policy.onnx`를 만든 직후, 스크립트가 play를 멈추고 `policy.pt`를 복사한 뒤 [tools/inspect_policy.py](tools/inspect_policy.py)로 검사합니다. 직접 할 때는 아래 명령 실행 후 `exported/`가 생기면 `Ctrl+C`로 종료합니다.

```bash
cd ~/aistudy_go2_runs
${ISAACLAB_ROOT:-$HOME/IsaacLab}/isaaclab.sh play --rl_library rsl_rl --task Isaac-Velocity-Flat-Unitree-Go2-Play-v0 \
    --num_envs 1 --checkpoint logs/rsl_rl/unitree_go2_flat/<run>/model_299.pt --viz kit
```

학습 때 네트워크 크기나 관측·행동 설정을 바꿨다면 **같은 override를 play에도** 붙여야 합니다. play는 `params/*.yaml`이 아니라 작업 등록 정보와 명령행으로 설정을 다시 만듭니다.

### 4. 미로에서 teleop

터미널 1 — 미로와 정책 실행:

```bash
# 제공 정책(공개된 사전학습 체크포인트)으로 먼저 확인
bash scripts/run_teleop_policy.sh
# 본인 정책
bash scripts/run_teleop_policy.sh --policy ../본인폴더/policy/policy.pt
# 2주차 본인 미로와 시작 위치 사용
bash scripts/run_teleop_policy.sh --policy ../본인폴더/policy/policy.pt \
    --maze-usd /경로/week2-gait/본인/assets/go2_maze.usda --spawn -4.15 -3.2 0.42 --spawn-yaw 0
```

`[INFO] Go2 maze is ready`가 나오면 터미널 2에서 teleop을 실행합니다.

```bash
bash scripts/teleop.sh   # i 전진, j/l 회전, k 정지, , 후진
```

실행기는 2초마다 `[STATUS] cmd vx=… | measured vx=…`를 출력합니다. 명령 속도와 실제 몸체 속도를 비교하는 근거로 사용하세요. 새 명령이 0.5초 동안 없으면 정지 명령(0)이 적용되고, 몸통이 벽에 닿으면 에피소드가 끝나 시작 위치에서 다시 시작합니다([docs/teleop_flow.md](docs/teleop_flow.md)).

## 검증 상태

- 실행기는 2주차에 Isaac Sim 6.0.1 / Isaac Lab v3.0.0-beta2 / RSL-RL 5.0.1에서 동작한 `go2_maze_ros2.py`를 기반으로, 정책 불러오기·미로 선택·시작 위치·상태 출력만 추가했습니다.
- 내보낸 `policy.pt`의 형식은 RSL-RL 5.0.1의 내보내기 코드(`MLPModel.as_jit` → `torch.jit.script`)로 Go2 평지 설정과 같은 모델을 만들어 확인했습니다: 입력 `[N, 48]` → 출력 `[N, 12]`, 파라미터 40,844개, 약 172 KiB, 메모리 속 정책과 출력 차이 0. 같은 확인으로 `inspect_policy.py`가 실행용 정책과 학습 체크포인트를 구분하는 것을 확인했습니다.
- Isaac Sim이 필요한 학습·play 내보내기·미로 주행은 GPU 실습 PC에서 확인해야 합니다. 결과는 [Solution-HJ1](../Solution-HJ1/README.md)의 확인 목록에 기록합니다.

## 출처

- `go2_policy_teleop.py`, `maze_env_cfg.py`, `scripts/run_teleop_policy.sh`, `scripts/teleop.sh`는 [week2-gait/ChanwonJung](../../week2-gait/ChanwonJung/)의 2주차 제출 코드를 바탕으로 수정했습니다.
- Go2 작업·보상·PPO 설정과 학습·내보내기 스크립트는 [Isaac Lab](https://github.com/isaac-sim/IsaacLab) v3.0.0-beta2(BSD-3-Clause), 학습 알고리즘은 [RSL-RL](https://github.com/leggedrobotics/rsl_rl) v5.0.1(BSD-3-Clause)을 설치해 사용하며 이 폴더에 복사하지 않습니다.
