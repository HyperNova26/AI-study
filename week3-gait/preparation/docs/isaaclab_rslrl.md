# Isaac Lab·RSL-RL로 학습·저장·내보내기·불러오기

Isaac Lab v3.0.0-beta2와 RSL-RL 5.0.1 기준입니다. 이전 버전 블로그·예제와 명령·파일 형식이 다르므로 이 문서의 명령을 기준으로 합니다.

## 1. 학습 작업이 정의되는 방식

Isaac Lab의 학습 작업은 Gymnasium ID로 등록된 **환경 설정 클래스 + 학습기 설정 클래스**의 조합입니다.

| Gym ID | 환경 설정 | 학습기 설정 | 용도 |
| --- | --- | --- | --- |
| `Isaac-Velocity-Flat-Unitree-Go2-v0` | `UnitreeGo2FlatEnvCfg` | `UnitreeGo2FlatPPORunnerCfg` | 학습 |
| `Isaac-Velocity-Flat-Unitree-Go2-Play-v0` | `UnitreeGo2FlatEnvCfg_PLAY` | 같음 | 실행·내보내기 |

환경 설정은 상속과 `__post_init__`으로 값을 덮어씁니다.

```text
LocomotionVelocityRoughEnvCfg   velocity/velocity_env_cfg.py   관측·행동·보상·이벤트 기본 정의, 4096 env, 50 Hz
 └ UnitreeGo2RoughEnvCfg        velocity/config/go2/rough_env_cfg.py   Go2 모델, 행동 스케일 0.25, 보상 가중치
    └ UnitreeGo2FlatEnvCfg      velocity/config/go2/flat_env_cfg.py    평지, 높이 스캔 제거, flat_orientation −2.5
       └ UnitreeGo2FlatEnvCfg_PLAY                                     50 env, 관측 노이즈·밀기 끔
          └ Go2MazeEnvCfg       week3-gait/preparation/maze_env_cfg.py 1 env, 미로, teleop 명령
```

미로 실행기의 환경은 학습 환경과 **관측(48)과 행동(12)의 정의가 같습니다**. 그래서 Flat 작업으로 학습한 정책을 그대로 미로에 넣을 수 있습니다. Rough 작업은 높이 스캔 187개가 추가된 235차원 관측이라 미로 실행기와 맞지 않습니다.

## 2. 학습 명령

Isaac Lab 3.0의 통합 명령은 `isaaclab.sh train`입니다(`scripts/reinforcement_learning/rsl_rl/train.py`는 3.0에서 deprecated). `scripts/train_go2_flat.sh`는 아래를 `GO2_RUNS_DIR`에서 실행합니다.

```bash
cd ~/aistudy_go2_runs
${ISAACLAB_ROOT:-$HOME/IsaacLab}/isaaclab.sh train --rl_library rsl_rl --task Isaac-Velocity-Flat-Unitree-Go2-v0 \
    --run_name 본인ID [--num_envs 4096] [--max_iterations 300] [--seed 42] [--viz kit]
```

| 옵션 | 기본값 | 설명 |
| --- | --- | --- |
| `--num_envs` | 4096 | 병렬 로봇 수. GPU 메모리가 부족하면 2048, 1024로 줄임 |
| `--max_iterations` | 300 | 이번 실행에서 반복할 iteration 수 |
| `--seed` | 42 | 난수 시드 (`-1`이면 무작위) |
| `--run_name` | 없음 | 로그 폴더 이름 뒤에 붙는 이름 |
| `--viz kit` | 없음 | 학습 화면 표시. 느려지므로 확인할 때만 |
| `--export_io_descriptors` | 끔 | 관측·행동 정의를 `io_descriptors/IO_descriptors.yaml`로 저장 (README 작성에 유용) |

### 설정 바꾸기 (override)

Isaac Lab 소스를 고치지 않고 명령 끝에 `env.<경로>=<값>`, `agent.<경로>=<값>`을 붙입니다. 값은 Python 리터럴로 해석되며 공백이 있으면 따옴표로 감쌉니다.

```bash
bash scripts/train_go2_flat.sh --run_name 본인ID \
    env.commands.base_velocity.rel_standing_envs=0.1 \
    env.rewards.feet_air_time.weight=0.5 \
    env.commands.base_velocity.ranges.lin_vel_x="(-1.0, 1.0)" \
    agent.algorithm.entropy_coef=0.005
```

- 마지막 이름을 잘못 쓰면 오류 없이 **새 속성이 만들어지고 무시**됩니다. 실행 후 run 폴더의 `params/env.yaml`, `params/agent.yaml`에서 값이 바뀌었는지 반드시 확인하세요.
- `--num_envs`, `--max_iterations`, `--seed` 같은 옵션은 override보다 나중에 적용되어 우선합니다.
- `env.sim.dt`, `env.decimation`처럼 다른 값을 계산하는 데 쓰이는 설정은 바꿔도 파생값이 다시 계산되지 않습니다. 이 과제에서는 바꾸지 않는 것을 권장합니다.
- `--resume`은 명령행 옵션으로만 동작합니다(`agent.resume=true`는 무시됨).

### 미로 실행기와의 호환성

| 바꾸는 것 | 미로 실행기와 호환 | 주의 |
| --- | --- | --- |
| 보상 가중치, 명령 범위·비율, 학습 iteration, PPO 하이퍼파라미터 | 그대로 호환 | |
| 신경망 크기 (`agent.actor.hidden_dims`) | `--policy policy.pt`로는 호환 | play에도 같은 override 필요, `--checkpoint` 방식은 기본 크기만 가능 |
| 관측 항목, 행동 스케일·관절 (`env.observations.*`, `env.actions.*`) | **비호환** | `maze_env_cfg.py`도 똑같이 바꿔야 함 |
| 시뮬레이션 주기 (`env.sim.dt`, `env.decimation`) | **비호환** | 정책의 시간 간격이 달라짐 |

## 3. 학습 출력

```text
~/aistudy_go2_runs/logs/rsl_rl/unitree_go2_flat/2026-10-02_14-03-11_본인ID/
├── params/env.yaml, params/agent.yaml   # 실제 적용된 전체 설정 (override 포함)
├── events.out.tfevents.*                # TensorBoard 기록
├── model_0.pt, model_50.pt, …, model_250.pt, model_299.pt   # 학습 체크포인트
└── git/*.diff                            # 학습 당시 코드 상태
```

- 체크포인트는 `save_interval=50`마다, 그리고 마지막 iteration에 저장됩니다. 300 iteration이면 마지막 파일은 `model_299.pt`입니다. `Ctrl+C`로 멈추면 마지막 저장은 없습니다.
- 콘솔에는 iteration마다 `Mean reward`, `Mean episode length`, `Steps per second`, `Iteration time`, `ETA`가 출력됩니다.

### TensorBoard 항목 (Notion 기록용)

| 태그 | 의미 |
| --- | --- |
| `Train/mean_reward` | 최근 100개 에피소드의 보상 합 평균 — 학습 진행의 대표 그래프 |
| `Train/mean_episode_length` | 평균 에피소드 길이 (1000스텝 = 20초 동안 넘어지지 않음) |
| `Episode_Reward/<보상 항목>` | 항목별 기여 (`track_lin_vel_xy_exp` 등) |
| `Episode_Termination/base_contact`, `.../time_out` | 넘어져서 끝난 비율, 시간이 다 되어 끝난 비율 |
| `Metrics/base_velocity/error_vel_xy`, `error_vel_yaw` | 명령 속도 추종 오차 |
| `Loss/value`, `Loss/surrogate`, `Loss/entropy`, `Loss/learning_rate` | PPO 손실과 자동 조절된 학습률 |
| `Policy/mean_std` | 행동 분포의 표준편차 — 줄어들면 탐색이 줄고 정책이 확신함 |
| `Perf/total_fps` | 초당 시뮬레이션 스텝 수 (GPU 성능 비교용) |

## 4. 이어서 학습하기

```bash
bash scripts/train_go2_flat.sh --resume --load_run 2026-10-02_14-03-11_본인ID --checkpoint model_299.pt \
    --run_name 본인ID --max_iterations 200
```

- `--load_run`은 run 폴더 이름의 앞에서부터 맞추는 정규식입니다. 이어서 학습할 폴더 이름을 그대로 쓰는 것이 가장 안전합니다. 학습의 `--checkpoint`는 그 폴더 안 파일 이름의 정규식입니다.
- iteration 번호는 이어지고, 결과는 **새 시각 폴더**에 저장됩니다(`--max_iterations`는 추가로 반복할 수). 이전 학습에서 바꾼 `env.`·`agent.` override도 다시 붙입니다.
- `--export_io_descriptors`와 함께 쓰지 않습니다. 이 옵션은 체크포인트를 찾기 전에 새 run 폴더를 만들기 때문에, `.*_본인ID` 같은 정규식이 방금 만든 빈 폴더를 골라 `No checkpoints in the directory`로 끝납니다.

## 5. 내보내기 (play)

```bash
cd ~/aistudy_go2_runs
${ISAACLAB_ROOT:-$HOME/IsaacLab}/isaaclab.sh play --rl_library rsl_rl --task Isaac-Velocity-Flat-Unitree-Go2-Play-v0 \
    --num_envs 1 --checkpoint logs/rsl_rl/unitree_go2_flat/<run>/model_299.pt [--viz kit]
```

1. play는 체크포인트를 불러온 직후 `<run>/exported/policy.pt`(TorchScript)와 `policy.onnx`를 만듭니다.
2. 이후 정책을 계속 실행하므로 확인 후 `Ctrl+C`로 끝냅니다. `scripts/export_policy.sh`가 이 과정을 자동으로 처리합니다.
3. play의 `--checkpoint`는 **파일 경로**입니다(학습의 `--checkpoint`는 파일 이름 정규식).
4. `exported/policy.pt`는 play를 실행할 때마다 덮어써지고 파일 이름에 iteration이 없습니다. 제출 폴더로 복사해 두세요.
5. 공개된 사전학습 정책을 내보내려면 `--use_pretrained_checkpoint`를 사용합니다(제공 정책과 비교할 때).

## 6. 불러오기

| 파일 | 형식 | 불러오는 방법 |
| --- | --- | --- |
| `model_<iter>.pt`, 공개 `checkpoint.pt` | `torch.save`로 저장한 학습 상태 dict | `OnPolicyRunner.load()` 후 `get_inference_policy()` — 학습기 설정이 같아야 함 |
| `exported/policy.pt` | TorchScript | `torch.jit.load(path, map_location=device)` 후 `policy(obs["policy"])` |

미로 실행기는 두 방법을 모두 지원합니다(`--checkpoint`, `--policy`). 제출물은 `exported/policy.pt`입니다. 자세한 형식은 [policy_format.md](policy_format.md)를 참고하세요.

```python
policy = torch.jit.load("policy.pt", map_location=env.unwrapped.device)  # play는 CPU로 저장
policy.eval()
with torch.inference_mode():
    obs = env.get_observations()          # TensorDict {"policy": [num_envs, 48]}
    actions = policy(obs["policy"])       # [num_envs, 12]
    env.step(actions)
```

## 7. 실행기가 부르는 Isaac Lab 함수

`go2_policy_teleop.py`는 학습 스크립트 대신 환경을 직접 만듭니다. 그래서 학습 스크립트가 자동으로 하는 처리를 직접 호출합니다.

| 호출 | 이유 |
| --- | --- |
| `AppLauncher(args)` | Isaac Sim(Kit)을 먼저 시작해야 `isaaclab.envs` 등을 import할 수 있음 |
| `parser.set_defaults(visualizer=["kit"])` | 3.0은 기본이 headless라 미로를 보려면 Kit 화면을 명시적으로 선택 |
| `resolve_presets(cfg)` | 물리 엔진별 선택값(`preset`)을 기본값으로 확정. Go2 관절 armature처럼 dict 안의 preset은 이 함수만 처리 |
| `handle_deprecated_rsl_rl_cfg(cfg, version)` | RSL-RL 5의 모델이 받지 않는 예전 설정 필드를 정리 (`--checkpoint` 방식에서만 필요) |
| `RslRlVecEnvWrapper(env)` | RSL-RL이 쓰는 형식으로 변환, `get_observations()`가 TensorDict 반환 |
| `command_manager.get_command("base_velocity")` | 정책이 보는 속도 명령 텐서 자체(복사본 아님). 여기에 teleop 값을 씀 |

3.0에서 바뀐 점: 로봇 데이터(`asset.data.*`)는 torch 텐서가 아닌 `ProxyArray`라 직접 보상·관측 함수를 만들 때 `.torch`를 붙입니다. 쿼터니언 순서는 `(x, y, z, w)`입니다.

## 참고 자료

- [Isaac Lab 3.0 마이그레이션 안내 (train/play 명령, 시각화 옵션)](https://isaac-sim.github.io/IsaacLab/main/source/migration/migrating_to_isaaclab_3-0.html)
- [Isaac Lab — Hydra 설정 override](https://isaac-sim.github.io/IsaacLab/main/source/features/hydra.html)
- [Isaac Lab — 학습한 정책을 USD 장면에서 실행](https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/policy_inference_in_usd.html): `exported/policy.pt` 사용 예
- [RSL-RL 저장소](https://github.com/leggedrobotics/rsl_rl) (v5.0.1)
