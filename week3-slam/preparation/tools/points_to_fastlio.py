#!/usr/bin/env python3
"""Republish the Gazebo 3D LiDAR cloud in a form FAST-LIO2 can consume.

Gazebo's ``gpu_lidar`` renders every ray of one scan at the same simulation time and
publishes rays without a return as non-finite (inf/NaN) coordinates. FAST-LIO2's
generic point-cloud handler keeps every point farther than ``preprocess.blind``, and
an infinite point passes that test, so it would reach the map. This node therefore:

* keeps only points with finite x/y/z that are at least ``min_range`` away,
* copies the header unchanged (simulation-time stamp, ``lidar_3d_link`` frame),
* keeps the original point layout (x, y, z, intensity as float32, ring as uint16).

No per-point time field is added: the whole scan was captured at ``header.stamp``,
which is what FAST-LIO2 assumes for clouds without per-point time.
"""

import array

import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2, PointField


class PointsToFastLio(Node):
    def __init__(self):
        super().__init__("points_to_fastlio")
        input_topic = self.declare_parameter("input_topic", "/points").value
        output_topic = self.declare_parameter("output_topic", "/points_fastlio").value
        self.min_range = float(self.declare_parameter("min_range", 0.10).value)
        # Reliable output matches both reliable (RViz default) and best-effort (FAST-LIO2) subscribers.
        reliable = QoSProfile(depth=5, history=HistoryPolicy.KEEP_LAST, reliability=ReliabilityPolicy.RELIABLE)
        self.publisher = self.create_publisher(PointCloud2, output_topic, reliable)
        self.create_subscription(PointCloud2, input_topic, self.on_cloud, qos_profile_sensor_data)
        self.get_logger().info(
            f"{input_topic} -> {output_topic}: keep finite points with range >= {self.min_range:.2f} m")

    def on_cloud(self, msg):
        offsets = {field.name: field for field in msg.fields}
        if any(name not in offsets or offsets[name].datatype != PointField.FLOAT32 for name in "xyz"):
            self.get_logger().error("input cloud needs float32 x, y, z fields", throttle_duration_sec=5.0)
            return
        count = msg.width * msg.height
        step = msg.point_step
        raw = np.frombuffer(msg.data, dtype=np.uint8)
        if count == 0 or raw.size < msg.height * msg.row_step:
            return
        # Drop any per-row padding so that the buffer is exactly `count` points.
        raw = raw[:msg.height * msg.row_step].reshape(msg.height, msg.row_step)[:, :msg.width * step]
        raw = np.ascontiguousarray(raw).reshape(-1)

        endian = ">" if msg.is_bigendian else "<"
        xyz_type = np.dtype({
            "names": ["x", "y", "z"],
            "formats": [endian + "f4"] * 3,
            "offsets": [offsets["x"].offset, offsets["y"].offset, offsets["z"].offset],
            "itemsize": step,
        })
        xyz = np.frombuffer(raw, dtype=xyz_type, count=count)
        x, y, z = (xyz[axis].astype(np.float64) for axis in "xyz")
        with np.errstate(invalid="ignore", over="ignore"):
            keep = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
            keep &= x * x + y * y + z * z >= self.min_range * self.min_range

        records = np.frombuffer(raw, dtype=np.dtype((np.void, step)), count=count)
        data = array.array("B")
        data.frombytes(records[keep].tobytes())

        out = PointCloud2()
        out.header = msg.header
        out.height = 1
        out.width = int(np.count_nonzero(keep))
        out.fields = msg.fields
        out.is_bigendian = msg.is_bigendian
        out.point_step = step
        out.row_step = step * out.width
        out.is_dense = True
        out.data = data
        self.publisher.publish(out)
        self.get_logger().info(f"{count} points in, {out.width} valid points out",
                               throttle_duration_sec=30.0)


def main():
    rclpy.init()
    node = PointsToFastLio()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
