#!/usr/bin/env python3
"""Record wheel odometry, FAST-LIO2 odometry and the simulator ground truth, then compare them.

  /odom               Gazebo DiffDrive wheel odometry   odom -> base_footprint, 2D, 30 Hz
  /Odometry           FAST-LIO2                         camera_init -> body (IMU), 6-DoF, per scan
  /ground_truth/odom  simulator-only true pose          world -> base_footprint, 50 Hz

Both estimates are converted to base_footprint poses and aligned to the ground truth at their
first sample (FAST-LIO2 in 3D, the planar /odom in x, y and heading), so the errors show how far
each estimate drifts after the start. Stop with Ctrl+C
or --duration; CSV, metrics.json and trajectories.png are written to --output-dir.
While running, /wheel_odom/path and /ground_truth/path (frame odom) are published for RViz.
"""

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from nav_msgs.msg import Path as PathMsg
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

SOURCES = {"wheel": "/odom", "fastlio": "/Odometry", "truth": "/ground_truth/odom"}


def quat_matrix(x, y, z, w):
    n = math.sqrt(x * x + y * y + z * z + w * w)
    x, y, z, w = x / n, y / n, z / n, w / n
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def pose_matrix(row):
    """row = (t, x, y, z, qx, qy, qz, qw) -> 4x4 homogeneous transform."""
    T = np.eye(4)
    T[:3, :3] = quat_matrix(*row[4:8])
    T[:3, 3] = row[1:4]
    return T


def yaw_of(T):
    return math.atan2(T[1, 0], T[0, 0])


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def planar(x, y, yaw, z=0.0):
    T = np.eye(4)
    T[:2, :2] = [[math.cos(yaw), -math.sin(yaw)], [math.sin(yaw), math.cos(yaw)]]
    T[:3, 3] = (x, y, z)
    return T


def planar_part(T):
    """Keep x, y, z and heading; drop roll/pitch."""
    return planar(T[0, 3], T[1, 3], yaw_of(T), T[2, 3])


class Recorder(Node):
    def __init__(self, args):
        super().__init__("odom_compare")
        self.args = args
        self.samples = {name: [] for name in SOURCES}
        for name, topic in SOURCES.items():
            self.create_subscription(Odometry, topic, lambda msg, n=name: self.on_odom(n, msg), 50)
        self.path_pubs = {name: self.create_publisher(PathMsg, topic, 1)
                          for name, topic in (("wheel", "/wheel_odom/path"), ("truth", "/ground_truth/path"))}
        self.paths = {name: PathMsg() for name in self.path_pubs}
        self.world_to_odom = None  # planar transform, fixed once both sources are seen
        self.last_path_time = {name: -1.0 for name in self.path_pubs}
        self.create_timer(0.5, self.publish_paths)

    def on_odom(self, name, msg):
        p, q = msg.pose.pose.position, msg.pose.pose.orientation
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        row = (t, p.x, p.y, p.z, q.x, q.y, q.z, q.w)
        self.samples[name].append(row)
        if name in self.paths:
            self.add_path_pose(name, row, msg.header.stamp)

    def add_path_pose(self, name, row, stamp):
        if row[0] - self.last_path_time[name] < 0.2:
            return
        T = pose_matrix(row)
        if name == "truth":
            if self.world_to_odom is None:
                if not self.samples["wheel"]:
                    return
                # odom origin in the world = true pose composed with the inverse wheel pose (planar).
                W = pose_matrix(self.samples["wheel"][-1])
                world_base = planar(T[0, 3], T[1, 3], yaw_of(T))
                odom_base = planar(W[0, 3], W[1, 3], yaw_of(W))
                self.world_to_odom = np.linalg.inv(world_base @ np.linalg.inv(odom_base))
            T = self.world_to_odom @ T
        self.last_path_time[name] = row[0]
        pose = PoseStamped()
        pose.header.stamp = stamp
        pose.header.frame_id = "odom"
        pose.pose.position.x, pose.pose.position.y, pose.pose.position.z = T[:3, 3]
        yaw = yaw_of(T)
        pose.pose.orientation.z, pose.pose.orientation.w = math.sin(yaw / 2), math.cos(yaw / 2)
        self.paths[name].poses.append(pose)

    def publish_paths(self):
        for name, publisher in self.path_pubs.items():
            path = self.paths[name]
            if path.poses:
                path.header.frame_id = "odom"
                path.header.stamp = path.poses[-1].header.stamp
                publisher.publish(path)

    def finished(self):
        truth = self.samples["truth"]
        return self.args.duration > 0 and len(truth) > 1 and truth[-1][0] - truth[0][0] >= self.args.duration


def truth_at(truth, t):
    """Ground-truth pose at time t: linear position, normalized-lerp orientation."""
    times = truth[:, 0]
    i = int(np.clip(np.searchsorted(times, t), 1, len(times) - 1))
    a, b = truth[i - 1], truth[i]
    s = 0.0 if b[0] == a[0] else float(np.clip((t - a[0]) / (b[0] - a[0]), 0.0, 1.0))
    qa, qb = a[4:8], b[4:8]
    if np.dot(qa, qb) < 0:
        qb = -qb
    row = np.concatenate(([t], a[1:4] + s * (b[1:4] - a[1:4]), qa + s * (qb - qa)))
    return pose_matrix(row)


def evaluate(samples, imu_offset, out_dir):
    truth = np.array(samples["truth"])
    if len(truth) < 2:
        raise RuntimeError("no /ground_truth/odom samples; is the week-3 simulation running?")
    # FAST-LIO2 reports the IMU (body) pose; move it to base_footprint with the URDF offset.
    body_to_base = np.eye(4)
    body_to_base[:3, 3] = -np.asarray(imu_offset)
    increments = np.linalg.norm(np.diff(truth[:, 1:3], axis=0), axis=1)
    metrics = {"duration_s": float(truth[-1, 0] - truth[0, 0]),
               "truth_path_length_m": float(increments.sum()), "estimates": {}}
    series = {}
    for name in ("wheel", "fastlio"):
        est = np.array(samples[name])
        if len(est) < 2:
            print(f"[odom_compare] no samples for {SOURCES[name]}, skipped")
            continue
        est = est[(est[:, 0] >= truth[0, 0]) & (est[:, 0] <= truth[-1, 0])]
        if len(est) < 2:
            print(f"[odom_compare] {SOURCES[name]} does not overlap the ground truth in time, skipped")
            continue
        poses = [pose_matrix(row) @ (body_to_base if name == "fastlio" else np.eye(4)) for row in est]
        gts = [truth_at(truth, t) for t in est[:, 0]]
        if name == "fastlio":
            # camera_init is the IMU frame at start, tilted like the robot: align in full 3D.
            align = gts[0] @ np.linalg.inv(poses[0])
        else:
            # /odom is planar by construction; the robot's static ~0.3 deg pitch must not tilt its path.
            align = planar_part(gts[0]) @ np.linalg.inv(planar_part(poses[0]))
        rows = []
        for t, T, G in zip(est[:, 0], poses, gts):
            A = align @ T
            dxy = float(np.linalg.norm(A[:2, 3] - G[:2, 3]))
            rows.append((t, *G[:3, 3], math.degrees(yaw_of(G)), *A[:3, 3], math.degrees(yaw_of(A)),
                         dxy, float(A[2, 3] - G[2, 3]), math.degrees(wrap(yaw_of(A) - yaw_of(G)))))
        data = np.array(rows)
        series[name] = data
        with open(out_dir / f"{name}_vs_truth.csv", "w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["t", "gt_x", "gt_y", "gt_z", "gt_yaw_deg", "est_x", "est_y", "est_z",
                             "est_yaw_deg", "err_xy_m", "err_z_m", "err_yaw_deg"])
            writer.writerows(np.round(data, 6).tolist())
        metrics["estimates"][name] = {
            "topic": SOURCES[name], "samples": len(data),
            "rate_hz": float((len(data) - 1) / (data[-1, 0] - data[0, 0])),
            "final_err_xy_m": float(data[-1, 9]), "final_err_z_m": float(data[-1, 10]),
            "final_err_yaw_deg": float(data[-1, 11]),
            "rmse_xy_m": float(np.sqrt(np.mean(data[:, 9] ** 2))), "max_err_xy_m": float(data[:, 9].max()),
            "max_abs_err_z_m": float(np.abs(data[:, 10]).max()),
            "max_abs_err_yaw_deg": float(np.abs(data[:, 11]).max()),
        }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    plot(truth[:, :3], series, out_dir / "trajectories.png")
    return metrics


def plot(truth_txy, series, path):
    """truth_txy: rows of (t, x, y); series: name -> rows of the CSV columns written by evaluate()."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    style = {"wheel": ("tab:blue", "wheel /odom"), "fastlio": ("tab:orange", "FAST-LIO2 /Odometry")}
    fig = plt.figure(figsize=(13, 7))
    grid = fig.add_gridspec(2, 2, width_ratios=[1, 1.3])
    ax_xy, ax_err, ax_z = fig.add_subplot(grid[:, 0]), fig.add_subplot(grid[0, 1]), fig.add_subplot(grid[1, 1])
    t0 = truth_txy[0, 0]
    ax_xy.plot(truth_txy[:, 1], truth_txy[:, 2], color="black", lw=2.5, alpha=0.35, label="ground truth")
    for name, data in series.items():
        color, label = style[name]
        ax_xy.plot(data[:, 5], data[:, 6], color=color, lw=1.2, label=label)
        ax_err.plot(data[:, 0] - t0, data[:, 9] * 100, color=color, label=label)
        ax_z.plot(data[:, 0] - t0, data[:, 10] * 100, color=color,
                  label=label + (" (2D, z fixed)" if name == "wheel" else ""))
    ax_xy.set(title="Trajectory in the world frame (aligned at start)", xlabel="x (m)", ylabel="y (m)")
    ax_xy.set_aspect("equal")
    ax_xy.grid(alpha=0.3)
    ax_xy.legend(loc="best", fontsize=9)
    ax_err.set(title="Horizontal position error vs ground truth", ylabel="error (cm)")
    ax_z.set(title="Vertical position error vs ground truth", xlabel="time (s)", ylabel="error (cm)")
    for ax in (ax_err, ax_z):
        ax.grid(alpha=0.3)
        ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def replot(out_dir):
    """Redraw trajectories.png from the CSV files of an earlier run."""
    series = {}
    for name in ("wheel", "fastlio"):
        csv_path = out_dir / f"{name}_vs_truth.csv"
        if csv_path.is_file():
            series[name] = np.loadtxt(csv_path, delimiter=",", skiprows=1, ndmin=2)
    if not series:
        raise RuntimeError(f"no *_vs_truth.csv in {out_dir}")
    reference = series.get("wheel", next(iter(series.values())))  # densest ground-truth samples
    plot(reference[:, :3], series, out_dir / "trajectories.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--duration", type=float, default=0.0,
                        help="stop after this many seconds of simulation time (0: until Ctrl+C)")
    parser.add_argument("--imu-offset", type=float, nargs=3, default=(-0.032, 0.0, 0.078),
                        metavar=("X", "Y", "Z"), help="imu_link position in base_footprint (URDF)")
    parser.add_argument("--replot", action="store_true",
                        help="only redraw trajectories.png from the CSV files in --output-dir")
    args, _ = parser.parse_known_args()  # leave --ros-args ... to rclpy
    if args.replot:
        replot(args.output_dir)
        print(f"[odom_compare] redrew {args.output_dir / 'trajectories.png'}")
        return
    rclpy.init()
    node = Recorder(args)
    try:
        while rclpy.ok() and not node.finished():
            rclpy.spin_once(node, timeout_sec=0.1)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        samples = node.samples
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics = evaluate(samples, args.imu_offset, args.output_dir)
    print(json.dumps(metrics, indent=2))
    print(f"[odom_compare] results written to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
