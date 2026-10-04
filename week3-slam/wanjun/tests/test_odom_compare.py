"""Verify the comparison frame conversion with synthetic known poses, not simulator claims."""
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

spec = importlib.util.spec_from_file_location("odom_compare", Path(__file__).resolve().parents[1] / "tools/odom_compare.py")
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)


def row(t, position, yaw):
    return (t, *position, 0.0, 0.0, math.sin(yaw / 2), math.cos(yaw / 2))


class ComparisonTests(unittest.TestCase):
    def samples(self):
        offset = np.array([-0.032, 0.0, 0.078])
        samples = {name: [] for name in compare.SOURCES}
        # Wheel/IMU have different origins; the robot translates and rotates 180 degrees.
        for t, x, y, yaw in [(1, 0, 0, 0), (2, 1, 0, math.pi / 2), (3, 1, 1, math.pi)]:
            rotation = compare.planar(0, 0, yaw)[:3, :3]
            base = np.array([x, y, 0.0])
            samples["truth"].append(row(t, base + [-2, -0.5, 0], yaw))
            samples["wheel"].append(row(t, base, yaw))
            samples["fastlio"].append(row(t, base + rotation @ offset - offset, yaw))
        return samples, offset

    def evaluate(self, samples, offset):
        with tempfile.TemporaryDirectory() as directory, patch.object(compare, "plot"):
            return compare.evaluate(samples, offset, Path(directory))

    def test_imu_lever_arm_removed_during_turn(self):
        samples, offset = self.samples()
        metrics = self.evaluate(samples, offset)
        for value in metrics["estimates"].values():
            self.assertLess(value["max_err_xy_m"], 1e-10)
            self.assertLess(value["max_abs_err_yaw_deg"], 1e-10)

    def test_wrong_imu_offset_exposes_rotation_error(self):
        samples, _ = self.samples()
        metrics = self.evaluate(samples, np.zeros(3))
        self.assertAlmostEqual(metrics["estimates"]["fastlio"]["final_err_xy_m"], 0.064)

    def test_missing_stream_is_not_success(self):
        samples, offset = self.samples()
        samples["fastlio"] = []
        with self.assertRaisesRegex(RuntimeError, "/Odometry"):
            self.evaluate(samples, offset)

    def test_clock_reset_is_not_success(self):
        samples, offset = self.samples()
        samples["wheel"].reverse()
        with self.assertRaisesRegex(RuntimeError, "timestamps"):
            self.evaluate(samples, offset)

    def test_nonoverlapping_times_are_not_success(self):
        samples, offset = self.samples()
        samples["fastlio"] = [(r[0] + 10, *r[1:]) for r in samples["fastlio"]]
        with self.assertRaisesRegex(RuntimeError, "overlap"):
            self.evaluate(samples, offset)


if __name__ == "__main__":
    unittest.main()
