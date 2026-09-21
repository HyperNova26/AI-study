import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("robot_log.csv")

data_num = len(df)
record_len = df["time_s"].iloc[-1] - df["time_s"].iloc[0]
avg_speed = df["speed_mps"].mean()
max_speed = df["speed_mps"].max()

time_s = df["time_s"]
speed_mps = df["speed_mps"]

plt.plot(time_s, speed_mps, color = "red")
plt.title("robot log")
plt.xlabel("Time  (s)")
plt.ylabel("Speed  (m/s)")
plt.savefig("graph.png")


print("데이터 개수 : ", data_num, "개", "\n기록 구간 길이 : ", record_len, "초", "\n평균속도 : ", avg_speed, "m/s", "\n최대속도 : ", max_speed, "m/s")