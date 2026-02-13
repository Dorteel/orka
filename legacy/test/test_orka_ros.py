from pathlib import Path
from PIL import Image

from graph_manager.main import GraphManager
from orka_ros.vision_sensor import initiate_sensor, add_vision_sensor_observation


def test_vision_sensor_observation_graph():
    gm = GraphManager()

    sensor_name = "vision_sensor"
    sensor_topic = "/camera/image"
    initiate_sensor(gm, sensor_name, sensor_topic)

    image = Image.new("RGB", (64, 48), color=(10, 20, 30))

    observation_name = "obs_vision_1"
    measurement_name = "meas_vision_1"
    result_name = "res_vision_1"

    output_dir = Path("observation_graph")
    output_dir.mkdir(parents=True, exist_ok=True)

    image_path = add_vision_sensor_observation(
        gm,
        sensor_name=sensor_name,
        observation_name=observation_name,
        measurement_name=measurement_name,
        result_name=result_name,
        image=image,
        save_image=True,
        image_dir=str(output_dir),
        image_filename="vision_1.jpg",
    )

    graph_path = output_dir / "vision_1.ttl"
    gm.save_graph(str(graph_path))

    assert image_path is not None
    assert image_path.exists()
    assert graph_path.exists()
