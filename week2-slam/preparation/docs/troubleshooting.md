# 실행 문제 확인 순서

모든 명령은 `week2-slam/preparation`에서 `source scripts/env.sh`를 실행한 별도 터미널 기준입니다. `echo`, `hz`, `tf2_echo`가 계속 실행되면 확인 후 `Ctrl+C`로 종료합니다.

## 설치·실행 단계

| 증상 | 확인 및 조치 |
| --- | --- |
| `ros2: command not found` | Jazzy 설치 후 `source scripts/env.sh` 실행. 다른 배포판을 source했다면 새 터미널 사용 |
| `Package ... not found` | `./scripts/check_environment.sh`로 확인 후 `./scripts/install_dependencies.sh` 실행 |
| apt가 `ros-jazzy-*`를 찾지 못함 | Ubuntu 24.04인지, 공식 ROS apt 저장소 설정과 `apt-get update`가 완료됐는지 확인 |
| Python 모듈·타입 지원 오류 | venv/Conda를 비활성화하고 시스템 Python을 쓰는 새 터미널에서 실행 |
| `gazebo` 명령을 찾지 못함 | 이 환경의 명령은 `gz sim`이며 실행 스크립트를 사용 |
| Gazebo GUI·RViz가 열리지 않음 | 데스크톱의 디스플레이와 OpenGL 지원 확인. 원격 접속·VM의 그래픽 설정 점검 |
| 센서 없이 `/clock`만 나옴 | GPU LiDAR가 렌더링 가능한지 확인. `headless:=True`도 GPU 센서 렌더링을 완전히 끄지 않음 |
| 이전 월드·로봇이 남거나 노드가 중복됨 | 이전 실행 터미널을 `Ctrl+C`로 끝낸 뒤 재실행. 한 실습당 launch 하나만 사용 |

Nav2 Jazzy의 CPU·그래픽 부하는 PC마다 다릅니다. 우선 Gazebo 창만 생략해 보세요.

```bash
./scripts/run_simulation.sh headless:=True
```

## 통신·시뮬레이션 시간

```bash
printenv ROS_DISTRO ROS_DOMAIN_ID ROS_AUTOMATIC_DISCOVERY_RANGE GZ_PARTITION
ros2 node list
ros2 topic echo /clock --once
ros2 topic hz /scan
```

실행 터미널과 점검 터미널의 `ROS_DOMAIN_ID`가 같아야 합니다. 이 폴더의 기본값은 `42`이므로 `0`을 사용하는 다른 터미널에서는 노드가 보이지 않을 수 있습니다. Gazebo 인스턴스를 구분하는 `GZ_PARTITION`도 확인합니다. 도메인을 바꾼 뒤 CLI 결과가 이상하다면 해당 환경에서 `ros2 daemon stop` 후 다시 조회합니다.

`/clock`이 오지 않으면 Gazebo와 브리지가 살아 있는지 확인합니다. 시간이 증가하지 않으면 Gazebo가 일시정지 상태인지 확인합니다. 센서가 늦거나 MPPI 주기를 놓치는 경고가 반복되면 다른 고부하 프로그램을 닫고 GUI를 줄여 봅니다.

```bash
ros2 param get /amcl use_sim_time
ros2 param get /controller_server use_sim_time
ros2 param get /rviz2 use_sim_time  # RViz를 실행한 경우
```

모두 `True`여야 합니다. 서로 다른 시간 기준에서는 TF extrapolation 오류가 발생할 수 있습니다.

## 지도·TF·초기 위치

```bash
ros2 lifecycle get /map_server
ros2 topic echo /map --once --field info --qos-durability transient_local
ros2 topic echo /scan --once --field header --qos-reliability best_effort
ros2 run tf2_ros tf2_echo odom base_footprint
```

지도 서버는 `active`여야 하며 이미지 경로는 `maps/tb3_sandbox.yaml` 기준으로 해석됩니다. RViz Map의 Durability를 `Transient Local`로 맞추면 이미 발행된 지도도 받을 수 있습니다.

`odom → base_footprint`는 보이는데 `map → base_link`가 없으면 공통 설정의 `amcl.set_initial_pose`가 적용됐는지 확인하고, RViz의 **2D Pose Estimate**로 위치를 다시 지정합니다. 시작 위치는 `(-2.0, -0.5)`, 방향은 +X입니다. 여전히 변환이 없다면 AMCL의 Active 상태와 `/scan` 수신을 확인합니다. 시작 직후의 일시적인 `map` TF 경고와 위치 적용 후에도 지속되는 오류를 구분합니다.

개인 설정에서 자동 초기 위치를 껐다면 Nav2 시작 시 TF 대기 제한 시간 안에 2D Pose Estimate를 지정해야 합니다. `Failed to activate global_costmap` 이후에는 위치만 지정해도 자동 복구되지 않을 수 있으므로 공통 설정으로 launch를 재시작해 확인하세요.

로봇과 스캔이 지도 밖에 보이거나 벽과 크게 어긋나면 초기 위치·방향을 다시 지정합니다. 이 폴더의 지도는 sandbox 월드용입니다. 다른 예제의 `map.yaml`을 연결하면 맞지 않을 수 있습니다.

## 경로·이동

```bash
ros2 lifecycle get /bt_navigator
ros2 lifecycle get /controller_server
ros2 action list -t
ros2 topic info /cmd_vel -v
```

초기 위치와 TF가 정상이고 Nav2가 Active인 상태에서 목표를 지정합니다. 벽·미지 영역·높은 costmap 비용의 영역에 목표를 두지 말고 가까운 빈 공간부터 확인합니다.

기본 MPPI 설정으로 아주 가까운 옆 방향 목표를 주면 `Failed to make progress` 이후 costmap 초기화나 회전 복구가 실행될 수 있습니다. 검증에서도 이 복구를 거쳐 목표에 도착했습니다. 목표 방향·주변 costmap을 함께 확인하고, 처음에는 로봇 앞쪽의 충분히 열린 공간에서 시작하세요.

경로는 보이지만 로봇이 움직이지 않으면 `/cmd_vel`의 발행자와 구독자, `/scan`의 최신 수신 여부, collision monitor의 메시지를 확인합니다. 이 준비 환경의 브리지는 `geometry_msgs/msg/Twist`를 사용합니다. 다른 ROS 배포판이나 `TwistStamped` 설정을 가져오면 연결이 맞지 않을 수 있습니다.

오류를 확인할 때는 launch 터미널의 최초 오류와 관련 노드 이름부터 살펴보세요. 전체 ROS 프로세스를 일괄 종료하기보다 자신이 실행한 launch를 종료하고 다시 시작합니다.
