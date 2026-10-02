# 사용한 외부 코드와 라이선스

## 저장소에 포함한 파일

| 로컬 파일 | 원본 | 라이선스 | 변경 |
| --- | --- | --- | --- |
| `third_party/livox_ros_driver2/msg/CustomMsg.msg`, `CustomPoint.msg` | [Livox-SDK/livox_ros_driver2](https://github.com/Livox-SDK/livox_ros_driver2) 커밋 `21445540` | MIT ([사본](third_party/livox_ros_driver2/LICENSE.txt)) | 없음. `package.xml`, `CMakeLists.txt`는 메시지만 빌드하도록 새로 작성 |
| `patches/fast_lio_jazzy_cxx17.patch` | [hku-mars/FAST_LIO](https://github.com/hku-mars/FAST_LIO) `CMakeLists.txt`에 대한 변경분 | FAST_LIO와 같음 (GPL-2.0) | C++14 → C++17 |
| `rviz/sensors.rviz`, `rviz/fast_lio.rviz` | 2주차 `week2-slam/wanjun/rviz/practice.rviz` (Nav2 1.3.13 `nav2_default_view.rviz` 기반)의 구조 | Apache-2.0 ([사본](licenses/Apache-2.0.txt)) | Nav2 디스플레이 제거, 센서·FAST-LIO2 토픽 표시, Fixed Frame `odom` / `camera_init` |
| `models/burger_sensors.urdf.xacro`, `config/bridge.yaml`, `launch/simulation.launch.py` | 2주차 `week2-slam/wanjun`의 같은 파일 | 스터디 저장소 자료 | Nav2 제거, 정답 위치 발행, `points_to_fastlio` 실행 추가 |

## 설치 또는 빌드해서 사용하는 것 (저장소에 복사하지 않음)

| 구성 요소 | 출처 | 라이선스 | 사용 |
| --- | --- | --- | --- |
| FAST-LIO2 | [hku-mars/FAST_LIO](https://github.com/hku-mars/FAST_LIO) `ROS2` 브랜치 `a4743b095409588842a5b30ddfa27e29d2f99164`, 서브모듈 [ikd-Tree](https://github.com/hku-mars/ikd-Tree) `e2e3f4e9` | GPL-2.0 | `scripts/build_fast_lio.sh`가 `~/aistudy_fastlio_ws`에 clone·빌드 |
| TurtleBot3 Burger 모델·메시 | [ROBOTIS turtlebot3_description](https://github.com/ROBOTIS-GIT/turtlebot3) (apt `ros-jazzy-turtlebot3-description` 2.3.6) | Apache-2.0 | URDF에서 include |
| sandbox 월드 | [nav2_minimal_turtlebot_simulation](https://github.com/ros-navigation/nav2_minimal_turtlebot_simulation) (apt `ros-jazzy-nav2-minimal-tb3-sim` 1.0.1) | Apache-2.0 | launch에서 불러오고 물리 간격만 1 ms로 변경 |

FAST-LIO2를 수정해 배포하는 경우 GPL-2.0 조건을 따릅니다. 이 폴더는 원본을 복사하지 않고 빌드 시 받아 오며, 저장소에는 CMake 변경분 패치만 둡니다.
