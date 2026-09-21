from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# 현재 Python 파일이 있는 폴더
folder = Path(__file__).resolve().parent

# CSV 읽기
data = pd.read_csv(folder / "robot_log.csv")


# 데이터 분석
data_count = len(data)

duration = data["time_s"].iloc[-1] - data["time_s"].iloc[0]

average_speed = data["speed_mps"].mean()

max_speed = data["speed_mps"].max()


# 결과 출력
print(f"데이터 개수: {data_count}개")
print(f"기록 구간 길이: {duration}초")
print(f"평균 속도: {average_speed:.2f} m/s")
print(f"최대 속도: {max_speed:.2f} m/s")


# 그래프 생성
plt.plot(data["time_s"], data["speed_mps"])

plt.title("Robot Speed over Time")
plt.xlabel("Time (s)")
plt.ylabel("Speed (m/s)")

plt.grid()

# PNG 파일로 저장
plt.savefig(folder / "speed_plot.png")

plt.close()