"""Graph loading, querying, and saving utilities for ORKA."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from owlready2 import get_ontology
from orka_builder import build_and_save_orka_core
from utils.xacro_loader import parse_robot_spec, sanitize_iri_fragment


def load_graph(path: str | Path):
    """Load an ontology graph from a local OWL file."""
    source = Path(path)
    return get_ontology(source.resolve().as_uri()).load()


def query_graph(ontology, sparql_query: str):
    """Run a SPARQL query against the ontology graph."""
    rdf_graph = ontology.world.as_rdflib_graph()
    return list(rdf_graph.query(sparql_query))


def save_graph(ontology, path: str | Path, fmt: str = "rdfxml") -> Path:
    """Save an ontology graph to disk."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    ontology.save(file=str(target), format=fmt)
    return target


def create_robot_graph(
    ontology,
    xacro_path: str | Path,
    robot_instance_name: str | None = None,
):
    """Add a robot and its sensors from xacro into the ontology graph."""
    robot_spec = parse_robot_spec(xacro_path)

    robot_cls = ontology["Robot"]
    sensor_cls = ontology["Sensor"]
    system_cls = ontology["System"]
    hosted_by = ontology["hostedBy"]
    implemented_by = ontology["implementedBy"]

    if robot_cls is None or sensor_cls is None:
        raise ValueError("Ontology must include Robot and Sensor classes.")
    if system_cls is None or hosted_by is None or implemented_by is None:
        raise ValueError(
            "Ontology must include System class and hostedBy/implementedBy properties."
        )

    robot_base_name = sanitize_iri_fragment(robot_instance_name or robot_spec.name)
    robot_id = _generate_robot_id(ontology, robot_base_name)

    robot = robot_cls(f"{robot_id}robot")
    system = system_cls(f"{robot_id}system")
    if robot not in system.hostedBy:
        system.hostedBy.append(robot)

    created_sensors = []
    for index, sensor in enumerate(robot_spec.sensors, start=1):
        sensor_class_name = _map_sensor_class(sensor.sensor_type)
        sensor_individual_cls = ontology[sensor_class_name] or sensor_cls

        raw_name = sensor.name or f"sensor_{index}"
        sensor_name = f"{robot_id}{sanitize_iri_fragment(raw_name)}"
        sensor_individual = sensor_individual_cls(sensor_name)

        if system not in sensor_individual.implementedBy:
            sensor_individual.implementedBy.append(system)

        created_sensors.append(sensor_individual)

    return {
        "robot_id": robot_id,
        "robot": robot,
        "system": system,
        "sensors": created_sensors,
    }


def _map_sensor_class(sensor_type: str) -> str:
    """Map common xacro sensor types to ORKA sensor subclasses."""
    normalized = sensor_type.strip().lower()
    mapping = {
        "imu": "ProprioceptorSensor",
        "gpu_ray": "PositionSensor",
        "ray": "PositionSensor",
        "lidar": "PositionSensor",
        "laser": "PositionSensor",
    }
    return mapping.get(normalized, "Sensor")




def main() -> None:
    """Load a xacro file and optionally inject its robot graph into an ontology."""
    robot = "tiago"
    parser = argparse.ArgumentParser(description="Load xacro and build robot graph.")
    parser.add_argument(
        "robot",
        nargs="?",
        default=f"{robot}",
        help="Robot key under urdfs/ (e.g. turtlebot3, tiago), or a path.",
    )
    parser.add_argument(
        "--xacro",
        default=None,
        help="Optional explicit path to xacro/URDF file or folder.",
    )
    parser.add_argument(
        "--ontology",
        default=f'./owl/orka-core.owl',
        help="Optional path to an OWL ontology to update.",
    )
    parser.add_argument(
        "--output",
        default=f'./owl/orka-core-{robot}.owl',
        help="Optional output OWL path (defaults to overwriting --ontology).",
    )
    args = parser.parse_args()

    source = _resolve_robot_source(args.robot, args.xacro)
    robot_spec = parse_robot_spec(source)
    print(f"Loaded xacro source: {source}")
    print(f"Robot: {robot_spec.name}")
    print("Sensors:")
    for sensor in robot_spec.sensors:
        print(f"- {sensor.name} ({sensor.sensor_type})")

    if args.ontology:
        ensure_ontology_exists(args.ontology)
        ontology = load_graph(args.ontology)
        created = create_robot_graph(
            ontology=ontology,
            xacro_path=source,
            robot_instance_name=args.robot if not args.xacro else None,
        )
        target = args.output or args.ontology
        save_graph(ontology, target)
        print(f"Robot ID prefix: {created['robot_id']}")
        print(f"Updated ontology saved to: {target}")


def _resolve_robot_source(robot: str, xacro_override: str | None) -> Path:
    """Resolve robot input to a concrete xacro/URDF file or folder path."""
    if xacro_override:
        override_path = Path(xacro_override)
        if not override_path.exists():
            raise FileNotFoundError(f"Provided --xacro path does not exist: {override_path}")
        return override_path

    direct = Path(robot)
    if direct.exists():
        return direct

    urdfs_path = Path("urdfs") / robot
    if urdfs_path.exists():
        return urdfs_path

    raise FileNotFoundError(
        f"Could not resolve robot '{robot}'. Expected path '{direct}' or '{urdfs_path}'."
    )


def _generate_robot_id(ontology, robot_base_name: str, max_attempts: int = 1000) -> str:
    """Generate a unique robot ID prefix like '<name>_12345_'."""
    for _ in range(max_attempts):
        suffix = random.randint(10000, 99999)
        robot_id = f"{robot_base_name}_{suffix}_"
        if ontology[f"{robot_id}robot"] is None:
            return robot_id
    raise RuntimeError("Failed to generate a unique robot ID prefix.")


def ensure_ontology_exists(path: str | Path) -> Path:
    """Build the ORKA core ontology at path when it does not exist."""
    ontology_path = Path(path)
    if ontology_path.exists():
        return ontology_path

    build_and_save_orka_core(output_path=ontology_path)
    print(f"Core ontology not found. Built new ontology at: {ontology_path}")
    return ontology_path


if __name__ == "__main__":
    main()
