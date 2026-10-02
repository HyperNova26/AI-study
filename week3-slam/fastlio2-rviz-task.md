## 3주차 — 팀별 핵심 기능 적용

**기한: 2026년 10월 4일**

### 인지팀: FAST-LIO2 위치추정과 RViz 시각화

#### 과제

3D LiDAR와 IMU가 장착된 TurtleBot 시뮬레이션에서 센서 데이터를 받아 FAST-LIO2로 odometry와 지도를 추정하고, RViz에 표시합니다. 로봇을 이동시키면서 추정 결과가 갱신되는 것을 확인합니다.

```
3D LiDAR + IMU → FAST-LIO2 → 추정 odometry·지도 → RViz
```

#### 제공되는 것

- 3D LiDAR·IMU의 장착 위치가 정의된 TurtleBot URDF 및 관련 자산
- 센서 데이터가 실제로 생성·발행되는 시뮬레이션 설정
- FAST-LIO2 입력과 호환되는 센서 데이터 형식 및 시간 설정
- 사용할 FAST-LIO2 구현·버전과 기본 설정 예제
- 센서 토픽, 좌표계, FAST-LIO2, RViz 관련 교보재

제공 환경은 운영자가 센서 입력과 FAST-LIO2 실행 가능 여부를 사전에 검증합니다.

> 제공 자료: [실습 안내](guide.md) · [실행 환경과 교보재](preparation/README.md) · [예시 답안](Solution-HJ1/README.md)

#### GitHub 제출물

- FAST-LIO2 연결·실행에 사용한 코드와 launch·설정 파일
- 센서 토픽·좌표계 및 실행 방법이 포함된 `README.md`
- **RViz에서 추정 궤적과 지도가 보이는 스크린샷**
- **로봇 이동에 따라 추정 궤적·지도가 갱신되는 영상**

#### 완료 시 설명할 내용

FAST-LIO2의 입력과 출력, 기존 TurtleBot odometry와 FAST-LIO2가 추정한 odometry의 차이를 설명합니다. 이번 과제는 추정 결과 확인까지이며, 이를 Nav2에 다시 연결하는 작업은 선택 확장으로 둡니다.
