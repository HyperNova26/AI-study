# 제공 코드와 외부 의존성

- `../preparation/`: 시뮬레이션, 로봇 센서 정의, 점군 변환기, FAST-LIO2 기본 설정과 빌드 패치를 그대로 사용합니다. 공통 파일은 수정하지 않았습니다. 외부 라이선스는 [제공 환경의 고지](../preparation/THIRD_PARTY.md)를 따릅니다.
- `../Solution-HJ1/`: 개인 launch, RViz, odometry 비교·고정 경로 주행 도구와 실행 스크립트의 출발점입니다. 해당 코드를 전부 직접 작성한 것으로 주장하지 않습니다. 가져온 기준은 AI-study `572b4ab`입니다.
- 개인 수정: launch의 임시 파일 식별자, RViz 촬영 화면, 저속 주행·중간 정지·odometry 끊김 및 시간제한 처리, 비교 입력 검증과 원시 샘플 보관입니다.
- 개인 추가: 사용자 권한 설치 스크립트, 시뮬레이션·환경 점검 래퍼, 입력 rosbag 기록과 격리된 재생 실험 도구, 비교 좌표계 회귀 테스트입니다.
- FAST-LIO2: [hku-mars/FAST_LIO](https://github.com/hku-mars/FAST_LIO), `a4743b095409588842a5b30ddfa27e29d2f99164`, 제공 C++17 패치 적용. 소스·빌드는 `~/aistudy_fastlio_ws`에 두며 이 제출 폴더에 복사하지 않습니다.
- 로봇 모델: [ROBOTIS-GIT/turtlebot3](https://github.com/ROBOTIS-GIT/turtlebot3), `2.3.6` 태그의 `da785b7201d317e6e2a662e41bb3d3fd50ebd503`에서 `turtlebot3_description`만 빌드합니다. 원본 저장소의 라이선스를 유지합니다.

`media/`의 영상·스크린샷·측정 결과는 이 PC에서 직접 실행해 생성합니다. 제공 예제의 영상이나 수치를 제출 결과로 복사하지 않습니다.
