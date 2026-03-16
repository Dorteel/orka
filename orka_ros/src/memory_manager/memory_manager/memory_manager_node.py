"""ROS2 memory manager node for ORKA KG initialization and observation ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any
from types import new_class

from owlready2 import ObjectProperty
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import yaml

from memory_manager_interfaces.srv import (
    InitializeMemoryGraph,
    StartObserve,
    StopObserve,
)


def _sanitize_fragment(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        return "instance"
    if cleaned[0].isdigit():
        return f"n_{cleaned}"
    return cleaned


def _resolve_orkav2_path() -> Path:
    # Best-effort: when running from source workspace, path is usually:
    # .../orka_ros/src/memory_manager/memory_manager/memory_manager_node.py
    workspace_src = Path(__file__).resolve().parents[3]
    candidate = workspace_src / "orkav2"
    if candidate.exists():
        return candidate

    from_env = Path(str(Path.cwd()))
    if (from_env / "builder").exists() and (from_env / "graph_manager.py").exists():
        return from_env

    return candidate


ORKAV2_PATH = _resolve_orkav2_path()
if str(ORKAV2_PATH) not in sys.path:
    sys.path.insert(0, str(ORKAV2_PATH))

from builder import OrkaBuilder  # noqa: E402
from graph_manager import save_graph  # noqa: E402


@dataclass
class SensorTopicBinding:
    sensor_name: str
    topic_name: str
    message_type: str = "std_msgs/msg/String"


class MemoryManagerNode(Node):
    """Service node managing KG initialization and live observations."""

    def __init__(self) -> None:
        super().__init__("memory_manager")

        self.ontology = None
        self.ontology_path = Path("owl/orka-memory.owl")
        self.sensor_topic_map: dict[str, SensorTopicBinding] = {}
        self.subscriptions_by_sensor: dict[str, Any] = {}
        self._has_topic_prop = None

        self.create_service(
            InitializeMemoryGraph,
            "/memory_manager/initialize_memory_graph",
            self._handle_initialize,
        )
        self.create_service(
            StartObserve,
            "/memory_manager/start_observe",
            self._handle_start_observe,
        )
        self.create_service(
            StopObserve,
            "/memory_manager/stop_observe",
            self._handle_stop_observe,
        )

        self.get_logger().info("Memory manager services ready.")

    def _handle_initialize(self, request, response):
        try:
            mapping_path = Path(request.mapping_file)
            if not mapping_path.exists():
                raise FileNotFoundError(f"Mapping file not found: {mapping_path}")

            output = Path(request.output_owl_path) if request.output_owl_path else self.ontology_path
            output.parent.mkdir(parents=True, exist_ok=True)

            builder = OrkaBuilder()
            self.ontology = builder.build(
                modules=["core", "ros", "sensors", "characteristics", "measurements"],
                include_swrl=bool(request.include_swrl),
                update_swrl_rules=False,
            )
            self._has_topic_prop = self._ensure_has_topic_property()
            self.ontology_path = output

            mapping = yaml.safe_load(mapping_path.read_text()) or {}
            sensors = mapping.get("sensors", {})
            algorithms = mapping.get("algorithms", {})

            sensor_count = 0
            topic_count = 0
            for sensor_key, sensor_def in sensors.items():
                sensor_name = _sanitize_fragment(sensor_key)
                sensor_cls = self._resolve_sensor_class(sensor_def.get("orka_class", "Sensor"))
                sensor_individual = self._ensure_individual(sensor_cls, sensor_name)
                sensor_count += 1

                namespace = str(sensor_def.get("namespace", "")).strip()
                topics = sensor_def.get("topics", {})
                if isinstance(topics, dict):
                    for _, topic_suffix in topics.items():
                        full_topic = self._join_topic(namespace, str(topic_suffix))
                        topic_individual_name = _sanitize_fragment(full_topic)
                        topic_class = self.ontology["Topic"] or self.ontology["Entity"]
                        topic_individual = self._ensure_individual(topic_class, topic_individual_name)

                        if self._has_topic_prop is not None:
                            current_topics = list(self._has_topic_prop[sensor_individual])
                            if topic_individual not in current_topics:
                                self._has_topic_prop[sensor_individual].append(topic_individual)

                        self.sensor_topic_map[sensor_name] = SensorTopicBinding(
                            sensor_name=sensor_name,
                            topic_name=full_topic,
                        )
                        topic_count += 1

            # Register algorithm/topic metadata as part of initialization graph state.
            for algo_key, algo_def in algorithms.items():
                algo_name = _sanitize_fragment(algo_key)
                algo_cls = self._resolve_class(
                    algo_def.get("orka_class", "Procedure"),
                    fallback_name="Procedure",
                )
                algo_individual = self._ensure_individual(algo_cls, algo_name)

                topic_value = str(algo_def.get("topic", "")).strip()
                if topic_value:
                    topic_individual_name = _sanitize_fragment(topic_value)
                    topic_class = self.ontology["Topic"] or self.ontology["Entity"]
                    topic_individual = self._ensure_individual(topic_class, topic_individual_name)
                    if self._has_topic_prop is not None:
                        current_topics = list(self._has_topic_prop[algo_individual])
                        if topic_individual not in current_topics:
                            self._has_topic_prop[algo_individual].append(topic_individual)
                    topic_count += 1

            save_graph(self.ontology, self.ontology_path)

            response.success = True
            response.message = f"Initialized memory graph at {self.ontology_path}"
            response.sensors_registered = sensor_count
            response.topics_registered = topic_count
        except Exception as exc:  # pragma: no cover
            response.success = False
            response.message = str(exc)
            response.sensors_registered = 0
            response.topics_registered = 0
        return response

    def _handle_start_observe(self, request, response):
        try:
            if self.ontology is None:
                raise RuntimeError("Memory graph is not initialized.")

            sensor_name = _sanitize_fragment(request.sensor_name)
            if not sensor_name:
                raise ValueError("sensor_name is required")

            if sensor_name in self.subscriptions_by_sensor:
                raise RuntimeError(f"Observation already active for sensor '{sensor_name}'")

            topic_name = request.topic_name.strip()
            if not topic_name:
                binding = self.sensor_topic_map.get(sensor_name)
                if binding is None:
                    raise ValueError(
                        f"No topic provided and no topic mapping found for sensor '{sensor_name}'"
                    )
                topic_name = binding.topic_name

            subscription = self.create_subscription(
                String,
                topic_name,
                lambda msg, s=sensor_name, t=topic_name: self._on_sensor_message(s, t, msg),
                10,
            )
            self.subscriptions_by_sensor[sensor_name] = subscription

            response.success = True
            response.message = f"Started observing sensor '{sensor_name}' on '{topic_name}'"
        except Exception as exc:  # pragma: no cover
            response.success = False
            response.message = str(exc)
        return response

    def _handle_stop_observe(self, request, response):
        try:
            sensor_name = _sanitize_fragment(request.sensor_name)
            subscription = self.subscriptions_by_sensor.pop(sensor_name, None)
            if subscription is None:
                raise ValueError(f"No active observation for sensor '{sensor_name}'")

            self.destroy_subscription(subscription)
            response.success = True
            response.message = f"Stopped observing sensor '{sensor_name}'"
        except Exception as exc:  # pragma: no cover
            response.success = False
            response.message = str(exc)
        return response

    def _resolve_class(self, orka_class_value: str, fallback_name: str):
        candidate = str(orka_class_value).split(":")[-1]
        class_name = _sanitize_fragment(candidate)
        resolved = self.ontology[class_name]
        return resolved or self.ontology[fallback_name]

    def _resolve_sensor_class(self, orka_class_value: str):
        return self._resolve_class(orka_class_value, fallback_name="Sensor")

    def _ensure_individual(self, cls, name: str):
        existing = self.ontology[name]
        if existing is not None:
            return existing
        return cls(name)

    def _join_topic(self, namespace: str, topic_suffix: str) -> str:
        ns = namespace.rstrip("/")
        suffix = topic_suffix.lstrip("/")
        if not ns:
            return f"/{suffix}" if suffix else "/"
        return f"{ns}/{suffix}" if suffix else ns

    def _on_sensor_message(self, sensor_name: str, topic_name: str, msg: String) -> None:
        if self.ontology is None:
            return

        now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        obs_id = _sanitize_fragment(f"obs_{sensor_name}_{now}")
        meas_id = _sanitize_fragment(f"meas_{sensor_name}_{now}")

        observation = self._ensure_individual(self.ontology["Observation"], obs_id)
        measurement = self._ensure_individual(self.ontology["Measurement"], meas_id)

        if measurement not in observation.hasMeasurement:
            observation.hasMeasurement.append(measurement)

        sensor_ind = self.ontology[_sanitize_fragment(sensor_name)]
        if sensor_ind is not None:
            if sensor_ind not in measurement.madeBySensor:
                measurement.madeBySensor.append(sensor_ind)

        # Persist observed payload as JSON text sidecar to keep ontology clean.
        sidecar = self.ontology_path.with_suffix(".observations.jsonl")
        with sidecar.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "observation": obs_id,
                        "measurement": meas_id,
                        "sensor": sensor_name,
                        "topic": topic_name,
                        "payload": msg.data,
                        "timestamp": now,
                    }
                )
                + "\n"
            )

        save_graph(self.ontology, self.ontology_path)

    def _ensure_has_topic_property(self):
        """Create a simple Sensor->Topic relation for runtime graph bindings."""
        existing = self.ontology["hasTopic"]
        if existing is not None:
            return existing

        with self.ontology:
            has_topic = new_class("hasTopic", (ObjectProperty,))
            has_topic.domain = [self.ontology["Entity"]]
            has_topic.range = [self.ontology["Topic"] or self.ontology["Entity"]]
        return has_topic


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = MemoryManagerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
