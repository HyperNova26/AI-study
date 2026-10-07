# 문제 해결

모든 명령은 `week3-slam/preparation`에서 `source scripts/env.sh`를 실행한 터미널 기준입니다. 2주차와 같은 설치·통신 문제는 [2주차 문제 해결](../../../week2-slam/wanjun/docs/troubleshooting.md)도 참고하세요.

## FAST-LIO2 빌드

| 증상 | 원인과 조치 |
| --- | --- |
| `'is_convertible_v' is not a member of 'std'`, `expected ')' before 'decltype'` (RCLCPP_INFO 줄) | 원본 CMakeLists가 C++14를 강제합니다. Jazzy rclcpp는 C++17 필요. `build_fast_lio.sh`가 `patches/fast_lio_jazzy_cxx17.patch`를 적용하는지 확인 |
| `Could not find a package configuration file provided by "livox_ros_driver2"` | 메시지 전용 패키지가 작업공간에 없습니다. `build_fast_lio.sh`를 다시 실행 (`third_party/livox_ros_driver2` 복사) |
| `Could not find ... "pcl_ros"` / `PythonLibs` | `scripts/install_dependencies.sh` 실행 (`ros-jazzy-pcl-ros`, `python3-dev`) |
| `git apply` 실패 (`corrupt patch`) | Windows에서 받은 패치가 CRLF입니다. `.gitattributes` 적용 후 다시 checkout하거나 Linux에서 clone |
| `Package 'fast_lio' not found` (실행 시) | 빌드 후 **새 터미널**에서 `source scripts/env.sh`. `FASTLIO_WS`를 바꿨다면 모든 터미널에서 같은 값 사용 |

## 시뮬레이션·센서

| 증상 | 확인 및 조치 |
| --- | --- |
| `/points`는 있는데 `/points_fastlio`가 없음 | 시뮬레이션 터미널에 `points_to_fastlio` 오류가 있는지 확인. venv·conda를 끄고 실행 (`numpy`는 시스템 Python 패키지) |
| `/clock`만 나오고 센서 없음 | GPU LiDAR 렌더링 실패. 그래픽 드라이버·디스플레이 확인 (2주차와 같음) |
| 다른 터미널에서 토픽이 안 보임 | `ROS_DOMAIN_ID`(기본 43)와 `GZ_PARTITION`이 같은지 확인. 2주차 기본값(42)과 다릅니다 |
| 이전 실행의 로봇·노드가 남음 | 실행 터미널을 모두 `Ctrl+C`로 종료 후 다시 시작 |

## FAST-LIO2 실행

| 증상 | 확인 및 조치 |
| --- | --- |
| 시작 직후 `No point, skip this scan!` 몇 번 | 정상입니다. IMU 초기화 동안 첫 스캔들을 건너뜁니다. `IMU Initial Done` 이후 사라져야 합니다 |
| `No point, skip this scan!`이 계속 나옴 | 입력 점군이 비었습니다. `ros2 topic echo /points_fastlio --once --field width`, `lid_topic` 이름 확인 |
| `/Odometry`가 나오지 않음 | `/imu` 수신 확인. FAST-LIO2는 스캔 시각까지의 IMU가 있어야 처리합니다. `use_sim_time:=true`인지 확인 |
| 시작하자마자 궤적이 튀거나 휨 | 로봇이 움직이는 중에 시작했습니다. 정지 상태에서 FAST-LIO2를 다시 시작 |
| `lidar loop back, clear buffer` | 시뮬레이션을 재시작해 시각이 뒤로 갔습니다. FAST-LIO2도 재시작 |
| `Failed to find match for field 'time'` 반복 | `lidar_type: 2`(Velodyne)로 바꿨을 때 나옵니다. Gazebo 점군에는 점별 시각이 없으므로 기본값 5 사용 ([fastlio2.md §5](fastlio2.md#5-시간-처리와-lidar_type-5)) |
| 회전할 때만 지도가 겹쳐 보이거나 방향이 틀어짐 | `extrinsic_T/R`, `lidar_type`을 확인. 기본 설정과 비교 |
| 설정 파일을 바꾼 뒤 FAST-LIO2가 시작하자마자 종료 (`Sequence should be of same type`, `expected [double_array]` 등) | ROS 2 파라미터 YAML의 배열은 모든 값이 같은 타입이어야 합니다. `[0.15, 0, 0.192]`가 아니라 `[0.15, 0.0, 0.192]`처럼 소수로 씁니다 |
| 수직(z) 위치가 수 cm 떠다님 | 16채널 LiDAR·평지에서 z 제약이 약해 생기는 정상 범위입니다. 수 cm보다 크면 IMU 초기화(정지 상태)를 확인 |
| 오래 실행하면 RViz가 느려짐 | `/Laser_map`이 계속 커집니다. `dense_publish_en: false` 유지, 필요하면 FAST-LIO2 재시작 ([rviz.md](rviz.md)) |
| `ros2 service call /map_save ...`가 `Map save disabled.` | `pcd_save.pcd_save_en: true`와 절대 경로 `map_file_path`를 설정 ([fastlio2.md §8](fastlio2.md#8-지도-저장-선택)) |

## RViz

| 증상 | 확인 및 조치 |
| --- | --- |
| `Frame [camera_init] does not exist` | FAST-LIO2가 아직 첫 스캔을 처리하지 않았거나 실행되지 않음 |
| FAST-LIO2 결과와 로봇 모델이 따로 놂 | 두 TF 트리가 연결되지 않았습니다. Fixed Frame `camera_init`으로 보거나 `odom → camera_init` 정적 변환 추가 ([sensors_topics_frames.md §3](sensors_topics_frames.md#3-좌표계tf)) |
| 점군이 안 보임 (Status: Warn, `No messages`) | 토픽 이름과 Reliability 확인. 센서 점군은 Best Effort로 받아도 됩니다 |
| `Message Filter dropping message ... extrapolation` | RViz가 시뮬레이션 시각을 쓰지 않습니다. `--ros-args -p use_sim_time:=true`로 실행 |
