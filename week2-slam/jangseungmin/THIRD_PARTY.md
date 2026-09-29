# 공식 자산 출처

이 개인 제출 폴더는 공식 예제 자산을 재사용합니다. 원본 자산과 변경 사항은 아래와 같습니다.

## 저장소에 포함한 자산

- 프로젝트: [ros-navigation/navigation2](https://github.com/ros-navigation/navigation2)
- 원본 버전: [1.3.13](https://github.com/ros-navigation/navigation2/tree/1.3.13), commit `f4108e5b1c2bce804a1aa0c7be6673a8eb4a1501`
- 복사 기준: Ubuntu 패키지 `ros-jazzy-nav2-bringup` 버전 `1.3.13-1noble.20260907.023821`
- 라이선스: [Apache License 2.0](licenses/Apache-2.0.txt), [원본 LICENSE](https://github.com/ros-navigation/navigation2/blob/1.3.13/LICENSE)
- 원본 프로젝트의 라이선스 고지: [원문 사본](licenses/NOTICE.navigation2.txt). 저작권 고지는 각 원본 파일과 위 저장소를 따릅니다.

| 로컬 파일 | 원본 위치 (`nav2_bringup/` 아래) | 변경 사항 |
| --- | --- | --- |
| `maps/tb3_sandbox.pgm` | `maps/tb3_sandbox.pgm` | 없음 |
| `maps/tb3_sandbox.yaml` | `maps/tb3_sandbox.yaml` | 없음 |
| `config/nav2_params.yaml` | `params/nav2_params.yaml` | 기본 AMCL 초기 위치, Burger 반지름·inflation, MPPI 속도·가속도, velocity smoother, progress checker 변경. 아래 변경 목록 참고 |
| `rviz/practice.rviz` | `rviz/nav2_default_view.rviz` | RobotModel 활성화 및 description QoS를 Transient Local로 설정, Burger TF 목록, /points 3D 디스플레이와 Orbit 뷰 추가, 불필요한 패널·디스플레이·창 위치 제거, YAML 재직렬화 |

`config/recording.rviz`는 위 `rviz/practice.rviz`를 바탕으로 경로 색상·점군 투명도·Orbit 촬영 시점을 조정한 보기 설정입니다. 개인 주행 변경값은 `config/nav2_overrides.yaml`에 분리했습니다.

## 설치 패키지로 제공하는 자산

- **Burger 본체·바퀴·기존 센서 장착 좌표·메시:** [ROBOTIS turtlebot3_description](https://github.com/ROBOTIS-GIT/turtlebot3/tree/jazzy/turtlebot3_description), Apache 2.0. 검증에 사용한 배포 버전은 `2.3.6`입니다. `models/burger_sensors.urdf.xacro`에서 설치된 `turtlebot3_burger.urdf`를 include하며 공식 자산을 저장소에 복사하지 않습니다.
- **sandbox 월드·장애물 모델:** [nav2_minimal_turtlebot_simulation](https://github.com/ros-navigation/nav2_minimal_turtlebot_simulation), `nav2_minimal_tb3_sim`의 `1.0.1`로 검증했습니다. launch에서 물리 시간 간격만 1 ms로 바꾸고 지형과 지도는 유지합니다.
- **추가한 모델 정의:** Burger의 2D LDS·IMU용 Gazebo 센서 설정, 범용 16채널 3D LiDAR·지지대, Harmonic 구동 플러그인, 브리지 설정은 시뮬레이션 구성 파일입니다. IMU 노이즈 값과 2D LDS 범위는 [공식 Burger Gazebo 모델](https://github.com/ROBOTIS-GIT/turtlebot3_simulations/blob/jazzy/turtlebot3_gazebo/models/turtlebot3_burger/model.sdf)을 참고했습니다.

## Nav2 기본 설정에서 바꾼 Burger 기본값

- AMCL: `set_initial_pose=true`, `initial_pose={x: -2.0, y: -0.5, z: 0.0, yaw: 0.0}`.
- 두 costmap: `robot_radius=0.13`, `inflation_radius=0.35`.
- MPPI: `vx_max=0.22`, `vx_min=-0.22`, `vy_max=0.0`, `ax_max=0.5`, `ax_min=-0.5`, `ay_max=0.0`, `ay_min=0.0`, `az_max=2.0`.
- Velocity smoother: `max_velocity=[0.22,0,2.0]`, `min_velocity=[-0.22,0,-2.0]`, `max_accel=[0.5,0,2.0]`, `max_decel=[-0.5,0,-2.0]`.
- Progress checker: `required_movement_radius=0.1`, `movement_time_allowance=20.0`.

설치 스크립트는 Jazzy 배포 채널의 패키지를 설치합니다. 설치 시점의 패치 버전까지 잠그는 apt snapshot은 아니며, 기준 버전과 실제 설치 버전은 ROBOT_SPEC.md와 검사 스크립트에서 구분합니다.
