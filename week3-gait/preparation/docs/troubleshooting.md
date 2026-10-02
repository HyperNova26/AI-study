# 문제 해결

| 증상 | 확인 및 조치 |
| --- | --- |
| `Isaac Lab을 찾지 못했습니다` | `ISAACLAB_ROOT=/경로/IsaacLab bash scripts/...`로 실행하거나 `~/.bashrc`에 `export ISAACLAB_ROOT=...` |
| `rsl-rl-lib` 버전 오류로 학습이 종료됨 | Isaac Lab 3.0의 학습 명령은 RSL-RL 5.0.1 이상이 필요합니다. `${ISAACLAB_ROOT:-$HOME/IsaacLab}/isaaclab.sh -p -m pip show rsl-rl-lib`로 확인 |
| `--rl_library` 관련 오류 | 3.0 통합 명령은 `isaaclab.sh train --rl_library rsl_rl --task ...` 형식입니다 |
| 학습이 시작되지만 창이 안 뜸 | 정상입니다. 3.0은 기본 headless입니다. 보려면 `--viz kit` |
| `CUDA out of memory`, PhysX GPU 버퍼 오류 | `--num_envs 2048` 또는 `1024`. 다른 GPU 프로그램 종료 ([gpu_and_time.md](gpu_and_time.md)) |
| 학습 중 `obs_groups` 경고 | Go2 설정이 `obs_groups`를 지정하지 않아 actor·critic 모두 `policy` 관측을 쓴다는 안내입니다. 무시해도 됩니다 |
| `Ctrl+C` 후 `model_299.pt`가 없음 | 중단 시 마지막 저장은 생략됩니다. 가장 최근 `model_<k×50>.pt`를 사용하거나 이어서 학습 |
| play가 run을 못 찾음 | play의 `--checkpoint`는 파일 경로입니다. 학습과 같은 폴더(`~/aistudy_go2_runs`)에서 실행하거나 절대 경로 사용 |
| `exported/policy.pt`가 오래된 파일 | play를 다시 실행하면 덮어씁니다. 시각과 sha256(`inspect_policy.py` 출력)을 확인 |
| `export_policy.sh`가 파일이 생긴 뒤에도 잠시 멈춤 | play(Isaac Sim) 종료를 기다리는 중입니다. SIGTERM 후 최대 30초 뒤 강제 종료합니다. 중간에 `Ctrl+C`를 눌러도 play는 함께 종료됩니다. 이후 GPU 메모리가 남아 있으면 `nvidia-smi`로 남은 프로세스를 확인 |
| 내보낸 정책을 `--checkpoint`로 넣으면 오류 | `policy.pt`는 TorchScript입니다. `--policy`로 넣으세요 ([policy_format.md](policy_format.md)) |
| `inspect_policy.py`가 입력 차원 경고 | Rough 작업(235차원)으로 학습했을 가능성. Flat 작업으로 학습 |
| 미로 실행기에서 `ROS 2 Python modules are unavailable` | `scripts/run_teleop_policy.sh`로 실행해야 Isaac Sim 내장 rclpy 경로가 설정됩니다 |
| teleop을 눌러도 로봇이 안 움직임 | 두 터미널의 `ROS_DOMAIN_ID`가 같은지, `ros2 topic echo /cmd_vel`에 메시지가 나오는지 확인. teleop 창에 포커스가 있어야 키 입력이 전달됩니다 |
| 로봇이 시작하자마자 재시작을 반복 | 시작 위치가 벽과 겹치거나 너무 낮음. `--spawn X Y 0.42`로 통로 한가운데 지정 |
| 걷지 않고 넘어지거나 떨림 | 학습이 덜 됐거나(평균 에피소드 길이 확인) 관측·행동 설정이 학습과 다름. 제공 정책으로 같은 미로가 잘 되는지 비교 |
| 본인 미로가 안 보이거나 로봇이 벽을 통과 | 미로 USD에 `PhysicsCollisionAPI`가 있는지, 단위가 m(`metersPerUnit = 1`)이고 `upAxis = "Z"`인지 확인 |
| 셸 스크립트 `set: pipefail` 오류 (WSL/Windows에서 받은 경우) | 줄바꿈이 CRLF입니다. 저장소의 `.gitattributes`가 `*.sh`를 LF로 유지하도록 다시 checkout |
