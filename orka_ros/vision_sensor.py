from pathlib import Path
from rdflib import Literal


def initiate_sensor(gm, sensor_name, sensor_topic, sensor_class="Camera"):
    sensor_type = gm.ORKA[sensor_class]
    sensor_uri = gm.add_sensor(sensor_name, sensor_type)
    gm.graph.add((sensor_uri, gm.ORKA.hasTopic, Literal(sensor_topic)))
    return sensor_uri


def add_vision_sensor_observation(gm, sensor_name, observation_name, measurement_name, result_name, image=None, save_image=True, image_dir="observation_graph", image_filename=None):
    sensor_uri = gm.obs_graph_base[sensor_name]
    gm.update_graph_with_observation(observation_name, measurement_name, sensor_uri, result_name)

    observation_uri = gm.obs_graph_base[observation_name]
    result_uri = gm.obs_graph_base[result_name]
    image_path = None

    if image is not None and save_image:
        image_dir_path = Path(image_dir)
        image_dir_path.mkdir(parents=True, exist_ok=True)
        if image_filename is None:
            image_filename = f"{result_name}.jpg"
        image_path = image_dir_path / image_filename
        if image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(image_path, format="JPEG")
        gm.graph.add((observation_uri, gm.ORKA.hasRawObservation, Literal(str(image_path))))
        gm.graph.add((result_uri, gm.ORKA.hasValue, Literal(str(image_path))))

    return image_path
