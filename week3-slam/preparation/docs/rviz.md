# RViz에서 FAST-LIO2 결과 보기와 촬영

제출물에는 **추정 궤적과 지도가 보이는 RViz 스크린샷**과 **로봇 이동에 따라 궤적·지도가 갱신되는 영상**이 필요합니다.

## 1. 바로 볼 수 있는 화면

| 실행 | 화면 | Fixed Frame |
| --- | --- | --- |
| `scripts/run_simulation.sh` | [rviz/sensors.rviz](../rviz/sensors.rviz): 로봇, TF, `/scan`, `/points_fastlio`, `/odom` 화살표 | `odom` |
| `scripts/run_fast_lio.sh` | [rviz/fast_lio.rviz](../rviz/fast_lio.rviz): `/Laser_map`, `/cloud_registered`, `/path`, `/Odometry` | `camera_init` |

두 RViz가 동시에 떠도 됩니다. 센서 확인 RViz를 끄려면 `run_simulation.sh use_rviz:=False`, FAST-LIO2 쪽 RViz를 끄려면 `run_fast_lio.sh rviz:=false`를 사용합니다.

- FAST-LIO2 저장소의 원래 `rviz/fastlio.rviz`는 넓은 실외 지도용 시점이라 이 작은 월드가 점 하나로 보입니다. 그래서 `run_fast_lio.sh`는 이 폴더의 `fast_lio.rviz`를 넘깁니다.
- 원본 `mapping.launch.py`는 RViz를 `use_sim_time` 없이 실행합니다. 고정 프레임(`camera_init`)의 점군·경로·Odometry는 정상으로 보이지만, TF 디스플레이는 시뮬레이션 시각의 프레임을 오래된 것으로 표시합니다. TF까지 보려면 본인 launch에서 RViz를 `use_sim_time: true`로 실행합니다([예시 답안](../../Solution-HJ1/launch/fast_lio_rviz.launch.py)).

## 2. 직접 구성할 때 추가할 디스플레이

`Add` → `By topic`에서 고르면 타입이 자동으로 맞습니다.

| 디스플레이 | 토픽 | 권장 설정 |
| --- | --- | --- |
| PointCloud2 (지도) | `/Laser_map` | Style `Points`, Size 2 px, Color Transformer `AxisColor`(Z) — 높이별 색 |
| PointCloud2 (현재 스캔) | `/cloud_registered` | FlatColor 흰색, Size 3 px — 지도 위에 지금 보는 점이 겹치는지 확인 |
| Path | `/path` | 주황색, Line Style `Billboards`, 폭 0.04 |
| Odometry | `/Odometry` | Shape `Arrow`, Keep 1 — 현재 추정 자세 |
| TF | — | `camera_init`, `body` 등 필요한 프레임만 켜고 Show Names |
| RobotModel | `/robot_description` | Durability `Transient Local` |

- Fixed Frame이 `camera_init`이면 FAST-LIO2를 시작하기 전에는 프레임이 없다는 경고가 나옵니다. FAST-LIO2가 첫 스캔을 처리하면 사라집니다.
- 바퀴 odometry와 한 화면에서 비교하려면 `odom → camera_init` 정적 변환을 추가하고 Fixed Frame을 `odom`으로 둡니다([sensors_topics_frames.md §3](sensors_topics_frames.md#3-좌표계tf)). RobotModel은 바퀴 odometry 위치에 그려지고, `body` 축과 `/path`는 FAST-LIO2 추정 위치에 그려집니다.
- `/Laser_map`은 계속 커지므로 오래 실행하면 RViz가 느려집니다. 촬영 전에는 FAST-LIO2를 새로 시작해 지도를 비우거나, `/Laser_map` 대신 `/cloud_registered`에 Decay Time(예: 30초)을 주어 최근 지도만 보이게 할 수 있습니다.
- 설정을 바꾼 뒤 `File → Save Config As`로 `.rviz` 파일을 본인 폴더에 저장하고 launch에서 `-d`로 불러오면 매번 같은 화면이 나옵니다.

## 3. 좋은 스크린샷의 조건

- 지도 전체와 지나온 궤적이 함께 보이는 비스듬한 Orbit 시점 (위에서 약 50°)
- 왼쪽 Displays 패널에서 사용한 토픽 이름이 보이도록
- 로봇이 한 바퀴 이상 움직인 뒤 — 지도가 채워지고 궤적이 닫힌 모습
- 가능하면 바퀴 odometry 궤적이나 정답 궤적을 함께 표시해 차이를 설명

## 4. 촬영 방법

| 환경 | 스크린샷 | 영상 |
| --- | --- | --- |
| Ubuntu 24.04 (GNOME) | `PrtSc` → 창 또는 영역 선택 | `Shift+Ctrl+Alt+R`로 녹화 시작·중지 (`~/Videos/Screencasts`), 또는 OBS Studio |
| WSL2 (WSLg) | Windows `Win+Shift+S` | OBS의 **디스플레이 캡처** (2주차에 창 캡처는 검은 화면) 또는 `Win+Alt+R` |

- 영상은 FAST-LIO2 시작(로봇 정지) → 이동 → 지도·궤적이 늘어나는 모습 → 정지까지 이어서 촬영합니다. 1~2분이면 충분합니다.
- 촬영 부하로 시뮬레이션이 느려지면 Gazebo 창을 끄고(`headless:=True`) RViz 하나만 띄웁니다. 센서와 물리는 계속 동작합니다.
- 파일이 크면 해상도를 1280×800 정도로 줄입니다. 2주차 제출 영상은 8~10 MB였습니다.
