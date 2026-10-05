# 3주차 보행팀 — 직접 학습한 Go2 정책으로 미로 teleop (ChanwonJung)

RTX 5070에서 Go2 평지 보행 정책을 500 iteration 학습하고, 실행용 TorchScript 정책으로 내보내 2주차 미로에 적용했습니다. 학습을 완료하고 정책 검사에서 `OK`를 확인한 뒤, 학습한 정책으로 전진·회전·정지 teleop 주행 영상을 촬영했습니다.

키보드로 속도와 방향을 명령하고, 정책은 해당 명령을 수행하도록 12개 관절을 제어합니다.

[과제](../go2-rl-gait-task.md)의 요구 사항에 맞춘 실행 결과입니다. 실행 환경과 제공 코드는 [preparation](../preparation/README.md), 전체 흐름은 [보행팀 안내](../guide.md)를 따릅니다. 주행 영상과 Notion 링크는 PR에 첨부하였습니다.

## 과제 목표와 구현 내용

Isaac Lab의 `Isaac-Velocity-Flat-Unitree-Go2-v0` 작업으로 속도 명령을 따라 걷는 정책을 학습하고, `exported/policy.pt`로 내보내, 미로에서 `/cmd_vel` 키보드 teleop으로 주행합니다.

## 제공 코드와 직접 작성·변경한 부분

[Solution-HJ1](../Solution-HJ1/README.md)의 스크립트 구조와 학습 설정 변경안을 기반으로 제출 폴더를 구성했습니다. 스크립트를 처음부터 새로 작성한 것은 아니며, run 이름과 결과 관리에 맞춰 재사용·수정했습니다.

| 구분 | 파일 | 내용 |
| --- | --- | --- |
| 제공 (수정 없이 사용) | `../preparation/go2_policy_teleop.py`, `maze_env_cfg.py`, `scripts/*` | 학습·내보내기·미로 실행기 |
| 예시 수정 | [train.sh](train.sh) | run 이름을 `cwj`로 변경. 아래 학습 설정으로 실행 |
| 예시 수정 | [export.sh](export.sh) | 검색할 run 이름을 `_cwj`로 변경. 정책 복사·검사 및 출처·설정 기록 |
| 예시 재사용 | [run_maze.sh](run_maze.sh) | 2주차에 사용한 미로와 시작 위치가 이미 지정되어 있어 실행 로직 변경 없이 사용 |
| 학습 결과 | [policy.pt](policy/policy.pt) | 직접 학습한 최종 체크포인트에서 내보낸 실행용 정책 |
| 실행 기록 | [policy_info.md](policy/policy_info.md), [IO_descriptors.yaml](policy/IO_descriptors.yaml), [train_env.yaml](policy/train_env.yaml), [train_agent.yaml](policy/train_agent.yaml) | 정책 출처, 입출력 정의, 실제 적용된 학습 설정 |

## 실제 실행 환경

| 항목 | 사용 값 |
| --- | --- |
| OS / 커널 | Ubuntu 24.04 / `6.8.0-142-generic` |
| GPU / 드라이버 | RTX 5070 12 GB / NVIDIA `580.178.04` |
| Isaac Sim / Isaac Lab | 6.0.1 / `v3.0.0-beta2` (`~/IsaacLab`) |
| 강화학습 / teleop | RSL-RL 5.0.1 PPO / ROS 2 Jazzy |
| 병렬 환경 / 환경당 수집 스텝 | 4096 / 24 |
| iteration / seed | 500 / 42 |

## 학습 설정과 변경 이유

기본 Go2 평지 설정에서 아래만 바꿨습니다. 관측(48)·행동(12) 정의는 그대로라 미로 실행기와 호환됩니다.

| 항목 | 기본값 | 변경값 | 이유 |
| --- | --- | --- | --- |
| `commands.base_velocity.heading_command` | `True` | `False` | teleop은 목표 방향이 아니라 회전 속도(`angular.z`)를 직접 줍니다. 학습도 회전 속도 명령을 직접 뽑아(−1에서 1 rad/s 사이) 회전 키를 누르고 있는 상황과 같게 함 |
| `commands.base_velocity.rel_standing_envs` | 0.02 | 0.1 | `k`나 watchdog으로 정지 명령이 자주 들어옴. 정지 연습 비율을 늘림 |
| `max_iterations` | 300 | 500 | 명령 분포가 넓어진 만큼 학습을 길게 |

실제 저장된 `policy/train_env.yaml`에서 `heading_command: false`, `rel_standing_envs: 0.1`, `policy/train_agent.yaml`에서 `max_iterations: 500`을 확인했습니다. 기본 설정으로 별도의 학습 run을 수행하지는 않았으며, 보상 가중치는 변경하지 않았습니다.

## 실행 방법

ROS 2 Jazzy, Isaac Sim 6.0.1, Isaac Lab v3.0.0-beta2(`~/IsaacLab` 또는 `ISAACLAB_ROOT`)가 설치된 Ubuntu 24.04 기준입니다.

각 터미널은 저장소 루트에서 시작합니다. 먼저 학습합니다.

```bash
cd week3-gait/ChanwonJung
bash train.sh
```

별도 터미널에서 TensorBoard를 실행하고 `http://localhost:6006`을 엽니다.

```bash
cd week3-gait/ChanwonJung
bash ../preparation/scripts/tensorboard.sh
```

학습 종료 후 `week3-gait/ChanwonJung` 폴더에서 최종 체크포인트를 내보냅니다.

```bash
bash export.sh \
  ~/aistudy_go2_runs/logs/rsl_rl/unitree_go2_flat/2026-10-06_01-17-45_cwj/model_499.pt
```

미로 실행 터미널에서 학습한 정책을 불러옵니다.

```bash
bash run_maze.sh
```

다른 터미널에서 teleop을 시작합니다.

```bash
cd week3-gait/ChanwonJung
bash ../preparation/scripts/teleop.sh
```

제공 정책을 확인하려면 학습한 정책 실행을 `Ctrl+C`로 종료한 뒤, 미로 실행 터미널에서 다음 명령을 실행합니다.

```bash
bash run_maze.sh --provided
```

학습은 `bash train.sh`로 실행했고 환경 수 감소나 resume 없이 4096 환경으로 완료했습니다. 학습 로그는 저장소 밖 `~/aistudy_go2_runs/logs/rsl_rl/unitree_go2_flat/<날짜_시각>_cwj/`에 생성됩니다. `GO2_RUNS_DIR`로 로그 루트를 변경할 수 있으며, Isaac Lab 위치가 다르면 `ISAACLAB_ROOT`를 지정합니다.

`run_maze.sh`는 2주차 미로(`week2-gait/ChanwonJung/assets/go2_maze.usda`), 시작 위치 `(-4.15, -3.2, 0.42)`, 방향 `0°`를 사용합니다. 학습한 정책과 제공 정책은 하나를 종료한 뒤 다른 정책을 실행합니다. teleop 터미널에 포커스를 두고 `i` 전진, `j/l` 회전, `k` 정지, `,` 후진으로 조종했습니다.

학습한 정책 적용 시 다음 로그를 확인했습니다.

```text
[INFO] Go2 policy: exported TorchScript .../ChanwonJung/policy/policy.pt (sha256 37100f54ba61)
[INFO] Maze: .../week2-gait/ChanwonJung/assets/go2_maze.usda
[INFO] Go2 maze is ready. Publish geometry_msgs/Twist on /cmd_vel
```

제공 정책 실행 시에는 `exported TorchScript` 대신 `RSL-RL checkpoint`가 출력됩니다. 정책 검사만 다시 수행하려면 `week3-gait/ChanwonJung` 폴더에서 다음 명령을 실행합니다.

```bash
~/IsaacLab/isaaclab.sh -p ../preparation/tools/inspect_policy.py policy/policy.pt
```

제출 파일은 실행용 `policy.pt`이며, 학습 체크포인트 `model_499.pt`와 전체 로그는 제출 폴더에 포함하지 않습니다.

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
- **보상**은 무엇을 잘해야 하는지(명령 속도 추종 가중치 1.5, 회전 추종 0.75)와 어떻게 해야 하는지(기울기 −2.5, 상하 움직임 −2.0, 급한 동작·토크 벌점)를 정합니다. 학습은 이 합이 커지는 방향으로 신경망을 고칩니다.

## 실제 학습 및 정책 검사 결과

| 확인 항목 | 결과 |
| --- | --- |
| 학습 run | `2026-10-06_01-17-45_cwj` |
| 최종 체크포인트 | `model_499.pt`, 2026-10-06 01:28:39 KST 생성 |
| 학습 완료 | 500 iteration 로그 및 학습 프로세스 종료 확인 |
| 학습 시간 | 첫 iteration 로그부터 마지막까지 약 10분 22초. run 이름 시각부터 최종 저장까지 초기 로딩 포함 약 10분 55초 |
| 처리속도 | 최종 `Perf/total_fps` 81,955 steps/s, 마지막 20회 평균 약 79,138 steps/s |
| 학습 중 GPU 상태 | 관찰 시 VRAM 약 9.2 GB, 사용률 약 78–82%, 온도 약 47–49°C |
| `Train/mean_reward` | 처음 −0.5277 → 최종 35.5816 |
| `Train/mean_episode_length` | 처음 13.0795 → 최종 1000스텝. 마지막 20회 평균 997.699스텝 |
| 정책 형식 / 크기 | TorchScript `_TorchMLPModel` / 171.5 KiB / 파라미터 40,844개 |
| 정책 입력·출력 검사 | `[1, 48] → [1, 12]`, `[8, 48] → [8, 12]`, 모두 `finite=True`, 검사 `OK` |

정책 SHA-256:

```text
37100f54ba61dbb02ce5d247947f6ceebc41f4c26415e37fcca48a7a040a6f42
```

최종 에피소드 길이 1000은 평지 학습 환경의 20초 제한에 해당합니다. 미로 완주나 제공 정책 대비 성능 우위를 의미하지는 않습니다.

TensorBoard에서 학습 run `2026-10-06_01-17-45_cwj`의 `Train/mean_reward`, `Train/mean_episode_length`, `Episode_Reward/track_lin_vel_xy_exp`, `Episode_Reward/track_ang_vel_z_exp`를 캡처해 Notion에 업로드했습니다.

## 미로 주행 및 제공 정책과의 관찰

학습한 정책으로 2주차 미로에서 전진·회전·정지를 시험하고 영상을 촬영했습니다. 영상에서 통로를 따라 이동하고 방향을 바꾸는 동작을 확인했습니다.

- 영상 후반 일부 로그에서 전진 명령 `vx=0.80`에 실제 `vx=0.82~0.85`, 회전 명령 `wz=1.00`에 실제 `wz=0.96~0.97`이 관찰됐습니다. 일부 시점의 값이며 구간 평균이나 반복 측정 결과는 아닙니다.
- 다리를 굽혀 몸통을 비교적 낮게 유지하는 자세가 관찰됐습니다. 카메라 각도와 벽 가림 때문에 정확한 높이는 측정하지 않았고, 실제 무게중심이 낮다고 단정하지 않았습니다.
- 학습 보상에는 특정 몸통 높이를 유지하는 항목이 없습니다. 이 설정이 낮은 자세에 영향을 주었을 가능성은 있지만 원인을 확정하지 않았습니다.
- 벽 충돌·재시작 횟수, 정지까지 걸린 시간은 별도로 집계하지 않았습니다.

초기 제공 정책 테스트에서는 전진 명령 `vx=0.50`에 실제 `vx=0.44~0.49`, 정지 명령 후 속도가 0에 가까워지는 기록을 확인했습니다. 학습한 정책의 위 기록과는 명령 및 상황이 달라 직접 비교하기 어렵습니다. 같은 조건에서 반복 측정하지 않았기 때문에 제공 정책보다 성능이 좋은지는 판단하지 않았습니다.

## 영상과 Notion 제출

주행 영상은 **PR에 첨부**하고, 학습 그래프를 올린 **Notion 페이지 링크도 PR에 기재**합니다. 영상과 Notion은 이 저장소 폴더에 포함하지 않습니다.

주행 영상에는 학습한 정책으로 2주차 미로에서 전진·회전·정지하는 모습을 담았습니다. 학습 기록은 Notion에서 확인할 수 있습니다.

## 출처

- [preparation](../preparation/README.md): 제공 학습·정책 검사·미로 teleop 실행기. 미로 실행기는 2주차에 제출한 `week2-gait/ChanwonJung` 코드를 바탕으로 확장된 자료입니다.
- [Solution-HJ1](../Solution-HJ1/README.md): 스크립트 구조 및 teleop용 학습 설정 변경안.
- Isaac Lab v3.0.0-beta2, RSL-RL 5.0.1: 제공 Go2 작업과 PPO 구현을 설치해 사용했습니다.
