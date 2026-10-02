# 3주차 보행팀 예시 답안 — 학습한 Go2 정책으로 미로 teleop (HJ1)

> **이 예시의 상태 — Isaac Sim 실행 전 (미검증)**: 명령과 설명은 작성했지만 `train.sh`, `export.sh`, `run_maze.sh`는 아직 Isaac Sim에서 실행하지 않았습니다. 확인된 것은 내보낸 `policy.pt`의 형식(RSL-RL 5.0.1 내보내기 코드로 같은 구조를 만들어 입력 `[N, 48]` → 출력 `[N, 12]`, 파라미터 40,844개, `inspect_policy.py` 출력 확인)뿐입니다. `policy/policy.pt`, 학습 그래프, 주행 영상과 아래 `(실행 후 기입)` 칸은 GPU 실습 PC에서 실행한 실제 값으로만 채우고, 예상값을 적지 않습니다.
>
> 실행 확인 목록: [ ] `train.sh` 학습 완료 · [ ] `export.sh` 내보내기·검사 `OK` · [ ] `run_maze.sh` 2주차 미로 teleop 주행

[과제](../go2-rl-gait-task.md)의 요구 사항에 맞춘 제출 예시입니다. 실행 환경과 제공 코드는 [preparation](../preparation/README.md), 전체 흐름은 [보행팀 안내](../guide.md)를 따릅니다.

## 과제 목표와 구현 내용

Isaac Lab의 `Isaac-Velocity-Flat-Unitree-Go2-v0` 작업으로 속도 명령을 따라 걷는 정책을 학습하고, `exported/policy.pt`로 내보내, 미로에서 `/cmd_vel` 키보드 teleop으로 주행합니다.

## 제공 코드와 직접 작성·변경한 부분

| 구분 | 파일 | 내용 |
| --- | --- | --- |
| 제공 (수정 없이 사용) | `../preparation/go2_policy_teleop.py`, `maze_env_cfg.py`, `scripts/*` | 학습·내보내기·미로 실행기 |
| 작성 | [train.sh](train.sh) | 학습 설정 변경 3가지 (아래) |
| 작성 | [export.sh](export.sh) | 마지막 체크포인트 내보내기 + 출처·설정 기록 |
| 작성 | [run_maze.sh](run_maze.sh) | 2주차 미로에서 본인 정책 / 제공 정책 실행 |
| 결과 | `policy/policy.pt` (실행 후 생성) | 제출할 실행용 정책 |
| 결과 | `policy/policy_info.md`, `IO_descriptors.yaml`, `train_env.yaml`, `train_agent.yaml` | 정책 출처, 입출력 정의, 실제 적용된 학습 설정 |

## 학습 설정과 변경 이유

기본 Go2 평지 설정에서 아래만 바꿨습니다. 관측(48)·행동(12) 정의는 그대로라 미로 실행기와 호환됩니다.

| 항목 | 기본값 | 변경값 | 이유 |
| --- | --- | --- | --- |
| `commands.base_velocity.heading_command` | `True` | `False` | teleop은 목표 방향이 아니라 회전 속도(`angular.z`)를 직접 줍니다. 학습도 회전 속도 명령을 직접 뽑아(−1에서 1 rad/s 사이) 회전 키를 누르고 있는 상황과 같게 함 |
| `commands.base_velocity.rel_standing_envs` | 0.02 | 0.1 | `k`나 watchdog으로 정지 명령이 자주 들어옴. 정지 연습 비율을 늘림 |
| `max_iterations` | 300 | 500 | 명령 분포가 넓어진 만큼 학습을 길게 |

적용 여부는 `policy/train_env.yaml`에서 `heading_command: false`, `rel_standing_envs: 0.1`로 확인합니다(override 이름을 틀리면 오류 없이 무시되기 때문).

## 실행 방법

ROS 2 Jazzy, Isaac Sim 6.0.1, Isaac Lab v3.0.0-beta2(`~/IsaacLab` 또는 `ISAACLAB_ROOT`)가 설치된 Ubuntu 24.04 기준입니다.

```bash
cd week3-gait/Solution-HJ1

# 1) 학습 (로그: ~/aistudy_go2_runs/logs/rsl_rl/unitree_go2_flat/<날짜_시각>_hj1/)
bash train.sh
bash ../preparation/scripts/tensorboard.sh        # 학습 곡선, http://localhost:6006

# 2) 내보내기: 최신 hj1 run의 마지막 체크포인트 → policy/policy.pt, 검사까지
bash export.sh

# 3) 2주차 미로 주행 — 터미널 1
bash run_maze.sh                    # 본인 정책
bash run_maze.sh --provided         # 비교용 제공 정책
#    터미널 2
bash ../preparation/scripts/teleop.sh
```

`run_maze.sh`는 이 저장소의 2주차 보행팀 미로(`week2-gait/ChanwonJung/assets/go2_maze.usda`, 시작 위치 `(-4.15, -3.2, 0.42)`)를 사용합니다. 학생은 본인 2주차 미로를 `--maze-usd <미로.usda> --spawn <x> <y> 0.42 --spawn-yaw <도>`로 넘기며, 뒤에 쓴 옵션이 적용됩니다. 제출 영상은 반드시 2주차 미로에서 촬영합니다.

## 정책 입출력과 적용 방법

| 항목 | 값 |
| --- | --- |
| 정책 파일 | `policy/policy.pt` — TorchScript `_TorchMLPModel`, 은닉층 128-128-128 ELU |
| 입력 | `[1, 48]`: 몸체 선속도 3, 각속도 3, 중력 방향 3, **속도 명령 3**, 관절 각도 12, 관절 속도 12, 직전 행동 12 |
| 출력 | `[1, 12]`: 관절 위치 행동, 환경이 `기본 각도 + 0.25 × 출력`으로 변환 |
| 주기 | 50 Hz — 물리 200 Hz(0.005초)를 4번(decimation 4) 진행할 때마다 정책 1회(0.02초) |
| 불러오기 | `torch.jit.load(policy.pt, map_location=cuda)` → `policy(obs["policy"])` (`go2_policy_teleop.py --policy`) |

teleop 명령 흐름: `teleop_twist_keyboard` → `/cmd_vel` → 범위 제한(±0.8, ±0.4, ±1.0)·0.5초 watchdog → `command_manager`의 `base_velocity` 명령 텐서 → 관측 9–11번 → 정책 → 12개 관절 목표 → PhysX. 자세한 단계는 [teleop_flow.md](../preparation/docs/teleop_flow.md)에 정리되어 있습니다.

## 관측·행동·보상의 역할 (설명 정리)

- **관측**은 정책이 판단에 쓰는 현재 상태입니다. 명령 속도가 관측에 들어 있기 때문에 하나의 정책이 여러 속도 명령을 수행할 수 있고, teleop은 이 칸을 바꾸는 일입니다.
- **행동**은 각 관절 목표가 기본 자세에서 얼마나 벗어날지(오프셋)입니다. 직전 목표에 더하는 증분이 아니며, 정책 출력에 0.25를 곱해 기본 자세에 더하므로 학습 초기의 무작위 출력에도 자세가 크게 무너지지 않습니다.
- **보상**은 무엇을 잘해야 하는지(명령 속도 추종 +1.5, 회전 추종 +0.75)와 어떻게 해야 하는지(기울기 −2.5, 상하 튐 −2.0, 급한 동작·토크 벌점)를 정합니다. 학습은 이 합이 커지는 방향으로 신경망을 고칩니다.

## 결과 (실행 후 기입)

| 확인 항목 | 결과 |
| --- | --- |
| 학습 환경 (GPU, `--num_envs`, 총 학습 시간, `Steps per second`) | (실행 후 기입) |
| 최종 `Train/mean_reward` / `Train/mean_episode_length` | (실행 후 기입) |
| `inspect_policy.py policy/policy.pt` 결과 | (실행 후 기입 — `OK`와 sha256) |
| 미로 주행: 전진·좌우 회전·정지·코너 통과 | (실행 후 기입) |
| 벽 충돌로 인한 재시작 횟수 | (실행 후 기입) |

- 학습 곡선: `media/train_reward.png`, `media/episode_length.png` (TensorBoard 캡처)
- 주행 영상: `media/maze_teleop.mp4` — **2주차 미로**에서 전진·회전·정지·코너 통과. 시작 시 `[INFO] Go2 policy: exported TorchScript …/policy.pt` 줄과 미로 전체가 보이도록 촬영

### 제공 정책과의 비교 관찰 (실행 후 기입)

같은 미로·같은 키 입력으로 두 정책을 실행하고 `[STATUS] cmd … | measured …` 출력을 비교합니다.

| 상황 | 제공 정책 | 본인 정책 |
| --- | --- | --- |
| 전진 `vx=0.5` 추종 (measured vx) | | |
| 제자리 회전 `wz=0.8` 추종 (measured wz) | | |
| 정지 명령 시 자세 (발 구름 여부) | | |
| 코너에서 회전하며 전진 | | |

예상과 다르면 그대로 적고 원인을 추정합니다. 예: 정지 비율을 늘렸는데도 발을 구른다면 `feet_air_time`·`action_rate_l2` 가중치와의 관계를 Notion에 기록합니다.

## 개인 Notion 학습 페이지

(링크) — 학습 설정과 변경 이유, 학습 그래프, 문제와 해결 시도, 제공 정책과의 차이를 정리합니다.

## 미완료 항목 또는 질문

- 결과 표와 영상은 GPU 실습 PC에서 실행 후 채웁니다.
