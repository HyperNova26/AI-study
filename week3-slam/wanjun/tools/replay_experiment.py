#!/usr/bin/env python3
"""Replay identical inputs into a fresh FAST-LIO2 process and record comparable metrics.

Use a separate ROS_DOMAIN_ID from the simulator. The bag contains its own /clock.
Only processes started by this script are stopped on completion or failure.
"""
import argparse
import os
from pathlib import Path
import signal
import subprocess
import time

import rclpy
from rclpy.node import Node


def stop(process):
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGINT)
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bag", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--duration", type=float, default=0.0,
                        help="bag playback seconds, 0 plays the entire recording")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    bag, config, output = (path.expanduser().resolve() for path in (args.bag, args.config, args.output))
    if not (bag / "metadata.yaml").is_file() or not config.is_file():
        parser.error("bag metadata and config must exist")
    if output.exists():
        parser.error("output already exists; choose a fresh directory")
    rclpy.init()
    probe = Node("replay_readiness")
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        rclpy.spin_once(probe, timeout_sec=0.1)
    if probe.count_publishers("/clock") or "laser_mapping" in probe.get_node_names():
        raise RuntimeError("ROS domain is already active; use a separate ROS_DOMAIN_ID")
    output.mkdir(parents=True)
    processes = []
    streams = []

    def start(name, command):
        stream = (output / f"{name}.log").open("w")
        streams.append(stream)
        process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        processes.append(process)
        return process

    try:
        mapping = start("fastlio", ["bash", str(root / "scripts/run_fast_lio_rviz.sh"),
                                    "use_rviz:=False", f"overrides_file:={config}"])
        compare = start("compare", ["bash", str(root / "scripts/run_compare.sh"), "--output-dir", str(output)])
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if mapping.poll() is not None or compare.poll() is not None:
                raise RuntimeError(f"worker exited before replay; see {output}")
            rclpy.spin_once(probe, timeout_sec=0.1)
            if (probe.count_subscribers("/imu") and probe.count_subscribers("/points_fastlio")
                    and probe.count_subscribers("/ground_truth/odom") and probe.count_subscribers("/Odometry")):
                break
        else:
            raise RuntimeError("timed out waiting for input subscribers")
        command = ["ros2", "bag", "play", str(bag), "--disable-keyboard-controls", "--delay", "2"]
        if args.duration > 0:
            command += ["--playback-duration", str(args.duration)]
        player = start("player", command)
        player.wait(timeout=600)
        if player.returncode:
            raise RuntimeError(f"bag player exited with {player.returncode}")
        time.sleep(2)
        stop(compare)
        if compare.returncode or not (output / "metrics.json").is_file():
            raise RuntimeError(f"comparison failed; see {output / 'compare.log'}")
        print((output / "metrics.json").read_text())
    finally:
        for process in reversed(processes):
            stop(process)
        for stream in streams:
            stream.close()
        probe.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
