import argparse
from pathlib import Path
from datetime import datetime

import numpy as np
from PIL import Image

try:
    from cv_bridge import CvBridge
except Exception:
    CvBridge = None

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image as RosImage

from graph_manager.main import GraphManager
from .vision_sensor import initiate_sensor, add_vision_sensor_observation


def ros_image_to_pil(msg):
    enc = msg.encoding.lower()
    if CvBridge is not None:
        bridge = CvBridge()
        cv_img = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        if enc in ("bgra8", "rgba8"):
            rgb = cv_img[..., :3]
            if enc == "bgra8":
                rgb = rgb[..., ::-1]
            return Image.fromarray(rgb)
        if enc.startswith("bgr"):
            cv_img = cv_img[..., ::-1]
        return Image.fromarray(cv_img)

    if enc in ("rgb8", "bgr8", "bgra8", "rgba8"):
        data = np.frombuffer(msg.data, dtype=np.uint8)
        if enc in ("bgra8", "rgba8"):
            img = data.reshape((msg.height, msg.width, 4))[..., :3]
        else:
            img = data.reshape((msg.height, msg.width, 3))
        if enc in ("bgr8", "bgra8"):
            img = img[..., ::-1]
        return Image.fromarray(img)

    raise ValueError(f"Unsupported encoding: {msg.encoding}")


class OneShotImage(Node):
    def __init__(self, topic):
        super().__init__("orka_vision_capture")
        self.msg = None
        self.sub = self.create_subscription(RosImage, topic, self._cb, 1)

    def _cb(self, msg):
        if self.msg is None:
            self.msg = msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="/TIAGO_PP/Astra_rgb/image_color")
    parser.add_argument("--sensor-name", default="vision_sensor")
    parser.add_argument("--sensor-topic", default="/TIAGO_PP/Astra_rgb/image_color")
    parser.add_argument("--sensor-class", default="Camera")
    parser.add_argument("--save-image", action="store_true")
    parser.add_argument("--output-dir", default="observation_graph")
    parser.add_argument("--session-dir", default=None)
    parser.add_argument("--image-filename", default=None)
    parser.add_argument("--observation-name", default="obs_vision_1")
    parser.add_argument("--measurement-name", default="meas_vision_1")
    parser.add_argument("--result-name", default="res_vision_1")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    rclpy.init()
    node = OneShotImage(args.topic)

    start = node.get_clock().now()
    while rclpy.ok() and node.msg is None:
        rclpy.spin_once(node, timeout_sec=0.1)
        if (node.get_clock().now() - start).nanoseconds / 1e9 > args.timeout:
            break

    if node.msg is None:
        node.destroy_node()
        rclpy.shutdown()
        raise RuntimeError("No image received")

    image = ros_image_to_pil(node.msg)

    gm = GraphManager()
    initiate_sensor(gm, args.sensor_name, args.sensor_topic, args.sensor_class)

    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    session_name = args.session_dir or datetime.now().strftime("session_%Y%m%d_%H%M%S")
    session_dir = output_root / session_name
    raw_dir = session_dir / "raw_data"
    processed_dir = session_dir / "processed_data"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    image_path = add_vision_sensor_observation(
        gm,
        sensor_name=args.sensor_name,
        observation_name=args.observation_name,
        measurement_name=args.measurement_name,
        result_name=args.result_name,
        image=image,
        save_image=args.save_image,
        image_dir=str(raw_dir),
        image_filename=args.image_filename,
    )

    graph_path = session_dir / f"{args.observation_name}.ttl"
    gm.save_graph(str(graph_path))

    node.destroy_node()
    rclpy.shutdown()

    if image_path is not None:
        print(f"saved image: {image_path}")
    print(f"saved graph: {graph_path}")


if __name__ == "__main__":
    main()
