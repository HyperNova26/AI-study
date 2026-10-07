# 3주차 인지팀 — FAST-LIO2 odometry·지도 추정과 RViz 표시

3D LiDAR와 IMU를 단 TurtleBot3 Burger 시뮬레이션에서 FAST-LIO2를 실행했다. 로봇을 키보드로 이동시키며 추정 궤적과 3D 점군 지도가 RViz에서 갱신되는 것을 확인했다.

## 제출 결과

- [RViz 스크린샷](media/rviz_fastlio_map.png): `/path`와 `/Laser_map`이 표시된 화면
- [실행 영상](media/HYPER_slam_week3_demo.mp4): Gazebo에서 로봇이 이동하고 RViz의 지도·궤적이 갱신되는 과정

## 실행에 사용한 파일

`../preparation/`은 실행에 사용한 제공 환경이다.

- `launch/simulation.launch.py`: Gazebo, TurtleBot3, ROS-Gazebo 브리지, 점군 변환 실행
- `config/fast_lio_burger.yaml`: FAST-LIO2 기본 설정
- `tools/points_to_fastlio.py`: `/points`를 `/points_fastlio`로 변환
- `scripts/run_simulation.sh`, `scripts/run_fast_lio.sh`, `scripts/run_teleop.sh`: 실행 스크립트
- `rviz/fast_lio.rviz`: FAST-LIO2 결과 RViz 설정

## 실행 방법

처음 한 번만 의존성을 설치하고 FAST-LIO2를 빌드한다.

```bash
cd week3-slam/preparation
bash scripts/install_dependencies.sh
bash scripts/build_fast_lio.sh
source scripts/env.sh
bash scripts/check_environment.sh
```

이후 Ubuntu 터미널 세 개에서 아래 순서로 실행한다.

```bash
# 터미널 1: Gazebo와 센서 데이터 생성
cd week3-slam/preparation
bash scripts/run_simulation.sh use_rviz:=False

# 터미널 2: FAST-LIO2와 결과 RViz
cd week3-slam/preparation
bash scripts/run_fast_lio.sh

# 터미널 3: 키보드 조종
cd week3-slam/preparation
bash scripts/run_teleop.sh
```

FAST-LIO2를 실행한 뒤 `IMU Initial Done`이 나올 때까지 로봇을 정지한다. 초기화가 끝난 뒤 teleop 터미널에 포커스를 두고 `i`(전진), `j`·`l`(회전), `k`(정지)를 입력한다.

## 센서 토픽과 좌표계

| 구분 | 토픽 | 프레임 | 역할 |
| --- | --- | --- | --- |
| 입력 | `/points_fastlio` | `lidar_3d_link` | 3D LiDAR 점군 |
| 입력 | `/imu` | `imu_link` | 각속도·선형가속도 |
| 출력 | `/Odometry` | `camera_init` → `body` | FAST-LIO2가 추정한 위치·자세 |
| 출력 | `/path` | `camera_init` | 추정 궤적 |
| 출력 | `/cloud_registered` | `camera_init` | 추정 위치를 적용한 현재 점군 |
| 출력 | `/Laser_map` | `camera_init` | 누적 3D 점군 지도 |

좌표계는 Gazebo 바퀴 odometry의 `odom → base_footprint` 트리와 FAST-LIO2의 `camera_init → body` 트리로 구성된다. `camera_init`은 FAST-LIO2 시작 순간의 IMU 위치·자세를 기준으로 한다.

## FAST-LIO2 입력·출력과 바퀴 odometry의 차이

FAST-LIO2는 `/points_fastlio`와 `/imu`, LiDAR-IMU 외부 파라미터를 입력으로 받는다. IMU로 다음 스캔 시점의 움직임을 예측하고, 현재 점군을 기존 지도에 맞춰 위치를 보정한다. 그 결과로 `/Odometry`, TF, `/path`, `/cloud_registered`, `/Laser_map`을 발행한다.

| 항목 | 바퀴 `/odom` | FAST-LIO2 `/Odometry` |
| --- | --- | --- |
| 사용 센서 | 바퀴 회전량 | 3D LiDAR + IMU |
| 추정 범위 | 2D 위치와 방향 | 3D 위치와 자세 |
| 기준점 | `base_footprint` | `body`(IMU) |
| 기준 프레임 | `odom` | `camera_init` |
| 발행 주기 | 약 30 Hz | LiDAR 스캔마다 약 10 Hz |
| 지도 작성 | 하지 않음 | `/Laser_map`을 함께 작성 |

## 실행 확인

FAST-LIO2 로그에서 `IMU Initial Done`과 지도 초기화 메시지를 확인했다. 주행 뒤 RViz에서 `/path`가 늘어나고 `/Laser_map`에 벽과 기둥 점군이 누적되는 것을 확인했다.

## Notion 학습 기록

개인 Notion 학습 페이지에는 환경 구축부터 실행 확인까지의 과정을 기록했다. 제공 기본 설정에서 `lidar_type: 5`, `/points_fastlio`, `/imu`, LiDAR-IMU 외부 파라미터를 사용했고, `colcon: command not found`와 `pcl_ros` 누락은 `scripts/install_dependencies.sh`로 해결했다. 실행 중에는 정지 상태에서 IMU 초기화를 마친 뒤 `/path`와 `/Laser_map`이 주행에 따라 갱신되는 과정을 확인했다. 또한 Gazebo, ROS 2 토픽, teleop, FAST-LIO2, 두 RViz 화면이 연결되는 흐름을 정리했다.

[개인 Notion 학습 기록](https://app.notion.com/p/HYPER-3-slam-3f2467cbd233805fb9c5ffb86cf0cfae?source=copy_link)에 위 과정을 정리했다. PR 본문에도 이 링크를 첨부한다.
