"""Graph loading, querying, and saving utilities for ORKA."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS
from owlready2 import (
    OwlReadyInconsistentOntologyError,
    get_ontology,
    sync_reasoner,
    sync_reasoner_pellet,
)
import yaml

from builder import DEFAULT_BASE_IRI, OrkaBuilder
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

    with target.open("wb") as output_file:
        ontology.save(file=output_file, format=fmt)

    return target


def update_graph(
    ontology,
    subject: str,
    predicate: str,
    object_value: str,
    *,
    object_is_literal: bool = True,
) -> tuple[str, str, str]:
    """Insert one triple into the ontology graph."""
    subject_ref = URIRef(subject)
    predicate_ref = URIRef(predicate)

    if object_is_literal:
        object_ref = Literal(object_value)
    else:
        object_ref = URIRef(object_value)

    with ontology:
        rdf_graph = ontology.world.as_rdflib_graph()
        rdf_graph.add((subject_ref, predicate_ref, object_ref))

    return (subject, predicate, object_value)


def initialize_graph_from_mapping(
    ontology,
    mapping_path: str | Path,
    *,
    robot_name: str = "robot",
    save_path: str | Path | None = None,
    fmt: str = "rdfxml",
) -> dict[str, object]:
    """Build a base graph from one mapping file.

    This creates the passive, structural part of the graph:
    robot, sensors, recognition algorithms, and sensor topics.
    """
    graph_data = build_base_graph_triples(
        mapping_path=mapping_path,
        base_iri=_get_base_iri(ontology),
        robot_name=robot_name,
    )
    triples_added = 0

    for triple in graph_data["triples"]:
        update_graph(
            ontology,
            subject=triple["subject"],
            predicate=triple["predicate"],
            object_value=triple["object_value"],
            object_is_literal=triple["object_is_literal"],
        )
        triples_added += 1

    saved_to = None
    if save_path is not None:
        saved_to = save_graph(ontology, save_path, fmt=fmt)

    return {
        "robot_uri": graph_data["robot_uri"],
        "sensors_added": graph_data["sensors_added"],
        "algorithms_added": graph_data["algorithms_added"],
        "topics_added": graph_data["topics_added"],
        "triples_added": triples_added,
        "saved_to": saved_to,
    }


def reason_graph(
    ontology,
    reasoner: str = "hermit",
    *,
    infer_property_values: bool = True,
    infer_data_property_values: bool = True,
    debug: int = 0,
    save_path: str | Path | None = None,
    fmt: str = "rdfxml",
) -> dict[str, object]:
    """Run reasoning and optionally save a materialized graph.

    Args:
        ontology: Owlready2 ontology object to reason over.
        reasoner: "hermit" (default) or "pellet".
        infer_property_values: Materialize inferred object property assertions.
        infer_data_property_values: Materialize inferred data assertions
            (Pellet only).
        debug: Owlready2 reasoner debug verbosity.
        save_path: Optional file path to persist materialized ontology.
        fmt: Owlready2 save format.
    """
    normalized_reasoner = reasoner.strip().lower()
    if normalized_reasoner not in {"hermit", "pellet"}:
        raise ValueError("Unsupported reasoner. Use 'hermit' or 'pellet'.")

    try:
        with ontology:
            if normalized_reasoner == "pellet":
                sync_reasoner_pellet(
                    infer_property_values=infer_property_values,
                    infer_data_property_values=infer_data_property_values,
                    debug=debug,
                )
            else:
                sync_reasoner(
                    infer_property_values=infer_property_values,
                    debug=debug,
                )
    except OwlReadyInconsistentOntologyError:
        return {
            "consistent": False,
            "reasoner": normalized_reasoner,
            "saved_to": None,
        }

    saved_to = None
    if save_path is not None:
        saved_to = save_graph(ontology=ontology, path=save_path, fmt=fmt)

    return {
        "consistent": True,
        "reasoner": normalized_reasoner,
        "saved_to": saved_to,
    }


def initialize_graph(
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
        created = initialize_graph(
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

    OrkaBuilder().build_and_save(modules=["core"], output_path=ontology_path)
    print(f"Core ontology not found. Built new ontology at: {ontology_path}")
    return ontology_path


def default_base_graph_path() -> Path:
    """Return the default base graph output path."""
    output_directory = Path(__file__).resolve().parents[1] / "obs_graphs"
    output_directory.mkdir(parents=True, exist_ok=True)
    return output_directory / "base_graph.owl"


def build_base_graph_triples(
    mapping_path: str | Path,
    *,
    base_iri: str = DEFAULT_BASE_IRI,
    robot_name: str = "robot",
) -> dict[str, object]:
    """Build the list of base-graph triples from one mapping file."""
    mapping = _read_mapping(mapping_path)

    robot_uri = _orka_uri(base_iri, robot_name)
    triples: list[dict[str, object]] = []
    sensor_topic_uris: dict[str, list[str]] = {}

    triples.append(
        _triple(robot_uri, str(RDF.type), _orka_uri(base_iri, "Robot"), False)
    )
    triples.append(
        _triple(
            _orka_uri(base_iri, "hasRawObservation"),
            str(RDF.type),
            "http://www.w3.org/2002/07/owl#DatatypeProperty",
            False,
        )
    )

    sensor_count = 0
    topic_count = 0
    algorithm_count = 0

    sensors = mapping.get("sensors", {})
    for sensor_key, sensor_definition in sensors.items():
        sensor_uri = _orka_uri(base_iri, sensor_key)
        sensor_class_uri = _resolve_mapping_term(
            sensor_definition.get("orka_class", "orka:Sensor"),
            base_iri,
        )

        triples.append(
            _triple(sensor_uri, str(RDF.type), _orka_uri(base_iri, "Sensor"), False)
        )
        triples.append(_triple(sensor_uri, str(RDF.type), sensor_class_uri, False))
        triples.append(
            _triple(sensor_uri, _orka_uri(base_iri, "mountedOn"), robot_uri, False)
        )
        sensor_count += 1

        namespace = str(sensor_definition.get("namespace", "")).strip()
        topics = sensor_definition.get("topics", {})
        sensor_topic_uris[sensor_key] = []

        if isinstance(topics, dict):
            for _, topic_suffix in topics.items():
                full_topic_name = _join_topic(namespace, str(topic_suffix))
                topic_uri = _orka_uri(base_iri, full_topic_name)

                triples.append(
                    _triple(topic_uri, str(RDF.type), _orka_uri(base_iri, "Topic"), False)
                )
                triples.append(
                    _triple(
                        sensor_uri,
                        _orka_uri(base_iri, "publishesTopic"),
                        topic_uri,
                        False,
                    )
                )
                triples.append(_triple(topic_uri, str(RDFS.label), full_topic_name, True))

                sensor_topic_uris[sensor_key].append(topic_uri)
                topic_count += 1

    algorithms = mapping.get("algorithms", {})
    for algorithm_key, algorithm_definition in algorithms.items():
        algorithm_uri = _orka_uri(base_iri, algorithm_key)
        algorithm_class_uri = _resolve_mapping_term(
            algorithm_definition.get("orka_class", "orka:Procedure"),
            base_iri,
        )

        triples.append(
            _triple(
                algorithm_uri,
                str(RDF.type),
                _orka_uri(base_iri, "Procedure"),
                False,
            )
        )
        triples.append(
            _triple(algorithm_uri, str(RDF.type), algorithm_class_uri, False)
        )
        algorithm_count += 1

        topic_name = str(algorithm_definition.get("topic", "")).strip()
        if topic_name:
            topic_uri = _orka_uri(base_iri, topic_name)
            triples.append(
                _triple(topic_uri, str(RDF.type), _orka_uri(base_iri, "Topic"), False)
            )
            triples.append(
                _triple(
                    algorithm_uri,
                    _orka_uri(base_iri, "publishesTopic"),
                    topic_uri,
                    False,
                )
            )
            triples.append(_triple(topic_uri, str(RDFS.label), topic_name, True))
            topic_count += 1

        inputs = algorithm_definition.get("inputs", [])
        if isinstance(inputs, list):
            for sensor_key in inputs:
                for sensor_topic_uri in sensor_topic_uris.get(sensor_key, []):
                    triples.append(
                        _triple(
                            algorithm_uri,
                            _orka_uri(base_iri, "subscribesToTopic"),
                            sensor_topic_uri,
                            False,
                        )
                    )

    return {
        "robot_uri": robot_uri,
        "sensors_added": sensor_count,
        "algorithms_added": algorithm_count,
        "topics_added": topic_count,
        "triples": triples,
    }


def _read_mapping(mapping_path: str | Path) -> dict:
    """Load one mapping file."""
    return yaml.safe_load(Path(mapping_path).read_text()) or {}


def _get_base_iri(ontology) -> str:
    """Return the ontology base IRI with a trailing separator."""
    base_iri = str(getattr(ontology, "base_iri", "") or DEFAULT_BASE_IRI)
    if base_iri.endswith(("#", "/")):
        return base_iri
    return f"{base_iri}#"


def _orka_uri(base_iri: str, value: str) -> str:
    """Turn one local name into a full ORKA URI."""
    return f"{base_iri}{sanitize_iri_fragment(value)}"


def _resolve_mapping_term(term: str, base_iri: str) -> str:
    """Resolve one mapping term into a full URI."""
    value = str(term).strip()
    if not value:
        raise ValueError("Mapping term cannot be empty.")

    if value.startswith(("http://", "https://")):
        return value
    if value.startswith("orka:"):
        return f"{base_iri}{value.split(':', 1)[1]}"

    return f"{base_iri}{sanitize_iri_fragment(value)}"


def _join_topic(namespace: str, topic_suffix: str) -> str:
    """Join one namespace and one topic suffix into a ROS topic name."""
    cleaned_namespace = namespace.strip().rstrip("/")
    cleaned_suffix = topic_suffix.strip().lstrip("/")

    if cleaned_namespace and cleaned_suffix:
        return f"{cleaned_namespace}/{cleaned_suffix}"
    if cleaned_namespace:
        return cleaned_namespace
    return cleaned_suffix


def _add_type_triple(ontology, subject: str, class_uri: str) -> int:
    """Insert one rdf:type triple."""
    update_graph(
        ontology,
        subject=subject,
        predicate=str(RDF.type),
        object_value=class_uri,
        object_is_literal=False,
    )
    return 1


def _add_object_triple(ontology, subject: str, predicate: str, object_uri: str) -> int:
    """Insert one object-property triple."""
    update_graph(
        ontology,
        subject=subject,
        predicate=predicate,
        object_value=object_uri,
        object_is_literal=False,
    )
    return 1


def _add_literal_triple(
    ontology,
    subject: str,
    predicate: str,
    literal_value: str,
) -> int:
    """Insert one data-property triple."""
    update_graph(
        ontology,
        subject=subject,
        predicate=predicate,
        object_value=literal_value,
        object_is_literal=True,
    )
    return 1


def _triple(
    subject: str,
    predicate: str,
    object_value: str,
    object_is_literal: bool,
) -> dict[str, object]:
    """Create one plain triple description."""
    return {
        "subject": subject,
        "predicate": predicate,
        "object_value": object_value,
        "object_is_literal": object_is_literal,
    }


if __name__ == "__main__":
    main()
