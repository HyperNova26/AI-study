from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "robot_log.csv"
PNG_PATH = BASE_DIR / "speed_plot.png"

df = pd.read_csv(CSV_PATH)

count = len(df)
duration = df["time_s"].iloc[-1] - df["time_s"].iloc[0]
mean_speed = df["speed_mps"].mean()
max_speed = df["speed_mps"].max()

print(f"데이터 개수: {count}개")
print(f"기록 구간 길이: {duration:g}초")
print(f"평균 속도: {mean_speed:.2f} m/s")
print(f"최대 속도: {max_speed:.2f} m/s")

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(df["time_s"], df["speed_mps"], marker="o", color="tab:blue")
ax.set_title("Robot Speed over Time")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Speed (m/s)")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(PNG_PATH, dpi=150)
print(f"그래프 저장: {PNG_PATH.name}")
