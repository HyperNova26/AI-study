# Week 3 - Go2 Policy Training!!

Isaac Lab에서 PPO 기반 Go2 속도 추종 보행 정책을 학습하고, 이를 가상 미로 환경에 적용·검증

## 1. 환경

- OS: Ubuntu 24.04.5.1
- GPU: NVIDIA RTX 5070 Ti
- Isaac Sim: 6.0.1
- Isaac Lab: v3.0.0-beta2
- RL Framework: RSL-RL
- RL Algorithm: PPO
- ROS2: Jazzy

---

## 2. 정책 입출력

### 관측

정책이 보는 관측은 총 48개로 (평지 작업은 높이 스캔이 빠짐)

- 항목 / 위치
- Body linear velocity / 0–2
- Body angular velocity / 3–5
- Gravity direction / 6–8
- Velocity command `[vx, vy, wz]` / 9–11
- Joint positions / 12–23
- Joint velocities / 24–35
- Previous action / 36–47

 로 구성 됨

Teleop으로 입력한 속도 명령은 Velocity command 부분에 반영됨

### 행동

정책이 내는 행동은 총 12개로 (4개의 다리 * 3개의 관절 = 12개)

- 각 관절의 목표 각도가 기본 자세에서 얼마나 벗어날지를 나타냄
- 관절 목표 = `기본 자세 각도 + 0.25 × 정책 출력` 처럼 실제 목표 각도로 바꿈
- 기본 자세 : 엉덩이 ±0.1, 앞 허벅지 0.8, 뒤 허벅지 1.0, 종아리 −1.5 rad

---

## 3. 학습

### 학습 명령

```bash
bash scripts/train_go2_flat.sh --run_name JaeDae
```

별도의 reward 또는 command range override는 사용하지 않고 기본 설정 명령을 사용하여 학습시킴.

만약 학습 iteration 등의 설정을 변경해야 하는 경우 다음과 같이 override함. (이번 과제에서 하진 않았음)

```bash
bash scripts/train_go2_flat.sh --run_name myname --max_iterations 500 \
    env.commands.base_velocity.rel_standing_envs=0.1
```

### 내보내기

```bash
bash scripts/export_policy.sh \
  logs/rsl_rl/unitree_go2_flat/2026-10-05_19-47-07_JaeDae/model_299.pt \
  ../JaeDae/policy/policy.pt
```

### 미로 실행 명령

```bash
bash scripts/run_teleop_policy.sh \
  --policy ../JaeDae/policy/policy.pt \
  --maze-usd ../../week2-gait/JaeDae/assets/jaedae_maze.usda \
  --spawn -4.25 -3.25 0.42 \
  --spawn-yaw 0
```

키보드 telop 실행
```bash
bash scripts/teleop.sh
```

## 4. 수정한 코드
정책 실행 과정에서 다음과 같은 NVRTC 라이브러리 오류가 발생함.

RuntimeError: nvrtc: error: failed to open libnvrtc-builtins.so.13.0

내PC CUDA 13 환경에서 NVRTC 라이브러리 경로가 실행 환경의 LD_LIBRARY_PATH와 달라 발생한 문제로 확인

따라서 scripts/run_teleop_policy.sh에서 LD_LIBRARY_PATH에 CUDA 13 라이브러리 경로를 추가함

수정 전
``` 
export LD_LIBRARY_PATH="${ROS_CORE}/lib"
```
수정 1
```
export LD_LIBRARY_PATH="${ROS_CORE}/lib:$HOME/IsaacLab/env_isaaclab/lib/python3.12/site-packages/nvidia/cu13/lib"
```
경로를 추가한 이후 관련 오류가 해결 됨 하지만 내pc의 경로를 하드코딩 한 것으로 깃에 올리기엔 부적합하다 생각하여 
Python의 nvidia 패키지 위치를 동적으로 탐색하도록 다음과 같이 수정함

수정2 
```
NVIDIA_LIB="$(python -c 'import nvidia; print(nvidia.__path__[0])')"
export LD_LIBRARY_PATH="${ROS_CORE}/lib:${NVIDIA_LIB}/cu13/lib"
```
이에 대한 검토가 필요해 보임
## Notion
[학습 설정·변경 항목, 보상 그래프, 문제와 해결 시도, 제공 정책과의 차이](https://puzzled-trouser-7e5.notion.site/HYPER-NOVA-3week-Go2-Gait-Policy-3f09a781827b80128e89eff3eddfad96)