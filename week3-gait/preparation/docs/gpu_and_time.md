# GPU 사용 환경과 학습 시간

## 권장 환경

| 항목 | Isaac Lab 3.0 문서 기준 | 이 스터디에서 확인된 구성 |
| --- | --- | --- |
| GPU | NVIDIA RTX, VRAM 16 GB 이상 권장 | RTX 5070 12 GB에서 2주차 미로 실행(env 1개) 확인 |
| 드라이버 | Linux 580.95.05 이상 | — |
| RAM | 32 GB 이상 | — |
| OS | Ubuntu 24.04 권장 (22.04, Windows 11도 지원하지만 Windows는 일부 기능 미완성) | Ubuntu 24.04 |

12 GB GPU로 4096개 환경 학습이 가능한지는 아직 확인하지 못했습니다. 처음 학습할 때 아래처럼 GPU 메모리를 보면서 시작하고, `CUDA out of memory`나 PhysX GPU 버퍼 오류가 나면 `--num_envs`를 2048 → 1024로 줄입니다. 환경 수를 줄이면 iteration당 데이터가 줄어 같은 iteration 수에서 성능이 낮을 수 있으므로 `--max_iterations`를 늘려 보완합니다.

```bash
watch -n 1 nvidia-smi   # 다른 터미널에서 메모리 사용량 확인
```

## 학습 시간 계산

```text
1 iteration = 환경 수 × num_steps_per_env = 4096 × 24 = 98,304 스텝
300 iteration = 약 2,950만 스텝
학습 시간 ≈ iteration 수 × Iteration time (콘솔 출력)
```

학습을 시작하면 콘솔에 매 iteration의 `Steps per second`, `Iteration time`, `ETA`(남은 시간)가 나옵니다. 처음 몇 iteration은 셰이더 컴파일·자산 다운로드 때문에 느리므로 10 iteration 이후 값을 기준으로 합니다.

Isaac Lab 문서의 참고 수치: RTX 4090에서 PhysX 4096 env의 G1 거친 지형 작업은 초당 약 82,000 스텝(학습 포함), RSL-RL로 6,550만 스텝 Humanoid 학습에 198초. Go2 평지 300 iteration은 같은 속도라면 **수 분~수십 분** 범위이지만 GPU·환경 수에 따라 크게 달라집니다. 본인 PC에서 측정한 `Steps per second`와 총 시간을 Notion에 기록해 다음 학습 계획에 사용하세요.

## 학습을 빠르고 안정적으로

- **화면을 띄우지 않습니다.** 3.0은 기본이 headless입니다. `--viz kit`은 학습 확인용으로만 짧게 사용합니다.
- 학습 중에는 Isaac Sim GUI, 브라우저 영상, 다른 GPU 프로그램을 닫습니다.
- 학습은 `~/aistudy_go2_runs`에서 진행되어 저장소가 커지지 않습니다.
- 오래 걸리는 학습은 `tmux`나 `screen` 안에서 실행하면 터미널을 닫아도 계속됩니다.
- 50 iteration마다 체크포인트가 저장되므로 중간에 멈춰도 `model_<k×50>.pt`부터 이어서 학습할 수 있습니다 ([isaaclab_rslrl.md](isaaclab_rslrl.md#4-이어서-학습하기)).
- 학습이 잘 되는지는 `Train/mean_episode_length`가 1000(20초)에 가까워지고 `Train/mean_reward`가 증가하다 평평해지는지로 봅니다.

## 미로 실행 (추론)

미로 teleop은 로봇 1대만 시뮬레이션하므로 학습보다 훨씬 가볍습니다. 2주차에서 RTX 5070 12 GB로 실시간(정책 50 Hz) 실행을 확인했습니다. 실행기는 시뮬레이션 1스텝(0.02초)마다 실제 시간에 맞춰 기다립니다(`--no-real-time`으로 해제).
