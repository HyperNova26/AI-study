
# JaeDae — Go2 커스텀 미로 ROS 2 Teleop
컴퓨터도 왔고 너무 어려워서 이제 제출합니다. 죄송합니다!
## 포함 파일

| 파일 | 용도 |
|---|---|
| `generate_jaedae_maze.py` | 간단히 구성한 미로를 .usda파일로 생성|
| `assets/jaedae_three_turn_maze.usda` | 생성된 커스텀 미로 에셋 |
| `maze_env_cfg.py` | isaac Lab의 환경 구성, 충돌 재질, 카메라, 시작 위치, GO2 등  |
| `go2_maze_ros2.py` | `policy.pt`를 불러오고 노드에서 전달받은 명령에 대한 정책 추론 및 출력 |
| `run_maze.sh` / `teleop.sh` | Isaac Sim의 실행 환경과 키보드 텔레옵 실행 |
| `videos/` | 동작을 촬영한 영상 |

## 실행 방법
터미널을 두개 켜서 하나는 환경을 실행하고 하나는 키보드텔레옵을 실행
1. 환경 실행
 ````
cd ~AI-study/week2-gait/JaeDae
bash run_maze.sh
````

2. 키보드텔레옵 실행

```
cd /home/woeo9945/Desktop/hyper/AI-study/week2-gait/JaeDae
bash teleop.sh
```
| 키 | 동작 |
|---|---|
| `i` | 전진 |
| `j` | 좌회전 |
| `l` | 우회전 |
| `k` | 정지 |
| `,` | 후진 |
종료는 각 터미널에서 ctrl + c 로 종료
## 미로 구성과 충돌 설정
### 미로구성
-   전체 크기: **11 m × 9 m**
-   외곽 벽: 4개
-   내부 분리벽: 1개
### 충돌설정

    prepend apiSchemas = ["PhysicsCollisionAPI"]

통해 Physics Collision API를 벽에 설정, `maze_env_cfg.py`에서도 미로에 대한 정적 충돌과 물리 재질을 설정
-   Static friction 0.8 → 벽이나 바닥과 접촉한 상태에서 미끄러지기 어려운 정도
-   Dynamic friction 0.7 → 접촉하면서 움직일 때의 마찰 정도
-   Restitution 0.0 → 충돌했을 때 튕겨 나가는 정도
Go2가 벽에 부딪혔을 때 공처럼 튕겨 나가는 것이 아니라 벽에 막히는 형태로 구성.

## 사용자 입력이 로봇동작으로 이어지는 흐름
키보드 입력
   ↓
teleop.sh 입력에 따른 이동 명령을 geometry_msgs/Twist 형태로 /cmd_vel 토픽에 전달함
   ↓
go2_maze_ros2.py가 /cmd_vel 토픽을 받아 속도 명령을 처리함
   ↓
48차원 Observation 구성
   ↓
policy.pt, 정책에 따라 많은 요소를 분석하여 관절 동작을 추론함  
   ↓
12차원 Action 출력
   ↓
Go2 관절 제어
   ↓
Go2 이동
##  느낀점
2주차 스터디인데 벌써 힘듭니다. 몇 시간을 한 지 모르겠습니다.

