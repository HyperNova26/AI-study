# 공식 자산 출처

이 폴더는 공통 준비용으로 공식 예제 자산을 재사용합니다.

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
| `config/nav2_params.yaml` | `params/nav2_params.yaml` | 출처 주석과 AMCL `set_initial_pose: true`, `initial_pose: {x: -2.0, y: -0.5, z: 0.0, yaw: 0.0}` 추가. 나머지 파라미터 동일 |
| `rviz/practice.rviz` | `rviz/nav2_default_view.rviz` | RobotModel 활성화 및 description QoS를 Transient Local로 설정, TF 기본 비활성화, 센서·도킹 등 불필요한 패널과 디스플레이 제거, 창 위치 제거, YAML 재직렬화 |

## 설치 패키지로 제공하는 자산

Waffle URDF/SDF, 메시, sandbox 월드, Gazebo/ROS 브리지는 [nav2_minimal_turtlebot_simulation](https://github.com/ros-navigation/nav2_minimal_turtlebot_simulation)의 `nav2_minimal_tb3_sim` 패키지에서 읽습니다. 이 폴더에 모델·메시를 복사하지 않습니다. 준비용 launch는 설치된 1.0.1 URDF의 존재하지 않는 메시 URI를 실제 `models/turtlebot3_model/meshes/` 파일 경로로 보정해 메모리에서 사용합니다. 이미 유효한 URI는 유지합니다. 모델의 원래 출처는 [ROBOTIS TurtleBot3](https://github.com/ROBOTIS-GIT/turtlebot3) 및 [TurtleBot3 simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations)이며, 배포 패키지의 라이선스·저작권 고지를 따릅니다.

설치 스크립트는 Jazzy 배포 채널의 패키지를 설치합니다. 설치 시점의 패치 버전까지 잠그는 apt snapshot은 아니며, 공통 기준 버전과 실제 설치 버전은 README와 검사 스크립트에서 구분합니다.
