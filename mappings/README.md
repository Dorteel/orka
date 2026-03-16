This folder contains the mappings between ROS 2 runtime topics and ORKA
individuals/classes used by `orka_ros`.

The main file is `sensor_map.yaml`.

When choosing `orka_class` values, use class names that actually exist in the
ontology builder modules:

- `builder/orka_core.py`
- `builder/orka_ros.py`
- `builder/orka_sensors.py`
- `builder/orka_characteristics.py`
- `builder/orka_measurements.py`

The current runtime path primarily uses:

- sensor classes from `builder/orka_sensors.py` such as `Camera`, `Lidar`, `Sonar`
- procedure classes from `builder/orka_core.py` or `builder/orka_measurements.py`
  such as `Procedure` or `ComputerVisionAlgorithm`

Some mapping fields are not fully consumed yet by the runtime node and should be
treated as placeholders/TODO:

- `pattern`
- `type`
- `inputs`
- `output_type`
- `frame_id`
