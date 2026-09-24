# Unitree Go2 커스텀 미로 ROS 2 teleop

Isaac Sim 6.0.1에서 Isaac Lab의 사전학습 Unitree Go2 flat locomotion 정책을 실행하고, ROS 2 `/cmd_vel`로 미로 안의 Go2를 조종하는 과제입니다.

## 실행

터미널 1에서 미로, Go2 정책, ROS 2 subscriber와 Isaac Sim GUI를 실행합니다.

```bash
cd /home/chanwonjung/hypernova/AI-study/week2-gait/ChanwonJung
./isaaclab.sh
```

`[INFO] Go2 maze is ready`가 출력되면 터미널 2에서 키보드 teleop을 실행합니다.

```bash
cd /home/chanwonjung/hypernova/AI-study/week2-gait/ChanwonJung
./teleop.sh
```

| 키 | 동작 |
|---|---|
| `i` | 전진 |
| `j` | 좌회전 |
| `l` | 우회전 |
| `k` | 정지 |
| `,` | 후진 |

두 스크립트가 ROS 2 Jazzy 설정과 긴 Isaac Lab 옵션을 처리하므로 Isaac Sim을 따로 켤 필요가 없습니다. 종료는 각 터미널에서 `Ctrl+C`를 누릅니다.

## ROS 2 CLI 직접 명령

전진:

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.5}, angular: {z: 0.0}}"
```

제자리 좌회전:

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

우회전은 `angular.z: -0.5`를 사용합니다. publisher를 `Ctrl+C`로 종료하거나 zero Twist를 보내면 정지합니다. 새 명령이 0.5초 동안 없을 때도 watchdog이 목표 속도를 0으로 만듭니다.

## 파일 구성

| 파일 | 역할 |
|---|---|
| `isaaclab.sh` | ROS 2 Jazzy와 Isaac Lab GUI를 한 번에 실행 |
| `teleop.sh` | 키보드 teleop을 `/cmd_vel`에 연결 |
| `assets/go2_maze.usda` | 실제 실행에서 불러오는 텍스트 기반 미로 USD 장면 |
| `generate_maze_usda.py` | 벽 치수 데이터로 USDA 장면을 재생성하는 스크립트 |
| `maze_env_cfg.py` | USD 미로 로드, 시작 위치와 카메라 구성 |
| `go2_maze_ros2.py` | Go2 정책 로드, Twist 구독, 정책 추론과 simulation step |

## 미로와 충돌 설정

- 전체 크기: 약 `10 m x 8 m`
- 벽 높이/두께: `0.65 m / 0.16 m`
- 통로 간격: 약 `2.25 m`
- 구조: 끝이 번갈아 열린 세 개의 내부 벽으로 만든 S자 통로
- 시작 위치: `(-4.15, -3.2, 0.42)`, `+x` 방향

미로 형상은 GitHub에서도 내용을 확인할 수 있는 텍스트 기반 `assets/go2_maze.usda`에 저장합니다. 각 벽은 USD `Cube`이고 `PhysicsCollisionAPI`가 적용된 정적 collider이므로 로봇이 접촉해도 밀리거나 쓰러지지 않습니다. `maze_env_cfg.py`는 이 장면을 reference하고 정적 마찰 `0.8`, 동적 마찰 `0.7`, 반발계수 `0.0`을 적용합니다.

벽의 크기나 배치를 수정한 후 USD를 다시 만들려면 다음을 실행합니다.

```bash
cd /home/chanwonjung/hypernova/AI-study/week2-gait/ChanwonJung
./generate_maze_usda.py
```

생성된 USDA가 실제 제출 장면이며, 생성 스크립트는 장면의 재현과 수정을 위해 함께 제공합니다.

## 사용자 입력에서 로봇 동작까지

```text
teleop_twist_keyboard 또는 ros2 topic pub
                    |
                    v
          /cmd_vel (Twist)
                    |
                    v
  [linear.x, linear.y, angular.z]
                    |
                    v
 Isaac Lab base_velocity command
                    |
                    v
 사전학습 Go2 RSL-RL policy
                    |
                    v
       12개 관절 position action
                    |
                    v
 Isaac Sim PhysX: 관절 운동, 마찰, 벽 충돌
```

입력은 정책 범위를 크게 벗어나지 않도록 전후 `0.8 m/s`, 좌우 `0.4 m/s`, 회전 `1.0 rad/s`로 제한합니다. 환경은 RTX 5070 12GB에 맞춰 한 개만 생성합니다.

## 사용 환경

- Ubuntu 24.04
- NVIDIA GeForce RTX 5070 12GB
- Isaac Sim 6.0.1 (`/home/chanwonjung/isaacsim`)
- Isaac Lab v3.0.0-beta2 계열 (`/home/chanwonjung/IsaacLab`)
- RSL-RL 5.0.1
- ROS 2 Jazzy

Isaac Lab 경로가 다르면 `ISAACLAB_ROOT=/다른/경로/IsaacLab ./isaaclab.sh`로 실행합니다.

## 영상 체크리스트

1. 커스텀 미로 전체와 Go2 시작 위치
2. `/cmd_vel`에 의한 전진
3. 코너에서 좌회전 또는 우회전
4. 다시 전진
5. `k` 입력 또는 watchdog에 의한 정지

