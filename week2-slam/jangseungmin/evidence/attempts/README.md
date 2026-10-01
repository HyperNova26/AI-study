# 실행 시도 원본

실패한 실행과 비교용 기본 목표 성공 기록을 보존하는 폴더다. 각 파일의 결과, 원인과 후속 조치는 [`../../RUN_HISTORY.md`](../../RUN_HISTORY.md)에 정리한다.

최종 성공 영상, RViz 캡처, 성공 JSON은 이 폴더가 아니라 `media/`에 둔다.

## 보존 파일

- `run_20260928T063716_646260Z.json`: 시뮬레이션 준비 전 실행, startup timeout
- `run_20260928T065734_299160Z.json`: 기본 목표 성공 기록
- `failed_recording_run_20260929.json`: 자동 화면 수집 부하 중 aborted
- `failed-auto-recording.mp4`: 위 실패 시도의 녹화본
- `navigation-run.json`: 개인 목표, `yaw=1.57`, aborted
- `navigation-run_0.json`: 개인 목표, action acknowledgement timeout
- `navigation-run_1.json`: 동일 원인의 재시도
- `navigation-run-3.json`: 서버 대기 시간 수정 후 주행, navigation timeout
