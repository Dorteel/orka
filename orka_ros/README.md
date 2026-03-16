# ORKA ROS2 Workspace

This folder contains a ROS 2 workspace for ORKA runtime services.

## Layout

- `src/orkav2`: ORKA v2 repository (as subrepo/submodule)
- `src/memory_manager_interfaces`: service definitions
- `src/memory_manager`: service node implementation

## Memory Manager Services

- `/memory_manager/initialize_memory_graph` (`InitializeMemoryGraph`)
  - Builds ORKA graph and registers sensors/topics from a mapping file.
- `/memory_manager/start_observe` (`StartObserve`)
  - Starts observing one sensor (subscribes to its topic).
- `/memory_manager/stop_observe` (`StopObserve`)
  - Stops observation subscription for one sensor.

## orkav2 subrepo

Add ORKA v2 into this workspace as a subrepo/submodule at:

- `orka_ros/src/orkav2`

Example (submodule):

```bash
git submodule add <ORKAV2_REPO_URL> orka_ros/src/orkav2
```

## Build

```bash
cd orka_ros
colcon build
source install/setup.bash
```

## Run

```bash
ros2 run memory_manager memory_manager_node
```

## Service Examples

Initialize graph:

```bash
ros2 service call /memory_manager/initialize_memory_graph \
  memory_manager_interfaces/srv/InitializeMemoryGraph \
  "{robot_name: tiago, mapping_file: /home/kai/Repositories/orka/mappings/sensor_map.yaml, output_owl_path: /home/kai/Repositories/orka/owl/orka-memory.owl, include_swrl: true}"
```

Start observe:

```bash
ros2 service call /memory_manager/start_observe \
  memory_manager_interfaces/srv/StartObserve \
  "{sensor_name: astra_rgb, topic_name: /TIAGO_PP/Astra_rgb/image_color, message_type: std_msgs/msg/String}"
```

Stop observe:

```bash
ros2 service call /memory_manager/stop_observe \
  memory_manager_interfaces/srv/StopObserve \
  "{sensor_name: astra_rgb}"
```

