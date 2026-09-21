import pandas as pd
import matplotlib.pyplot as plt

# data 가져오기 
data = pd.read_csv("robot_log.csv")
time_s = data["time_s"]
speed_mps = data["speed_mps"]

# 값 구하기
data_count = len(time_s)
duration_s = time_s.iloc[-1] - time_s.iloc[0] 
average_speed_mps = speed_mps.mean()
maximum_speed_mps = speed_mps.max()

# print 하기
print(f"데이터 개수: {data_count}개")
print(f"기록 구간 길이: {duration_s}초")
print(f"평균 속도: {average_speed_mps:.2f} m/s")
print(f"최대 속도: {maximum_speed_mps:.2f} m/s")

# graph 그리기
plt.figure(figsize=(8,4.5))
plt.plot(time_s, speed_mps, marker = "v", color = "r")

plt.title("Robot Speed Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Speed (m/s)")

plt.grid(True, alpha = 0.3)
plt.tight_layout()

plt.savefig("robot_speed_over_time.png",dpi=150)
plt.close()

print("그래프 저장 완료: robot_speed_over_time.png")