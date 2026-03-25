"""Minimal graph operations for ORKA.

Public API:
- load_graph()
- query_graph()
- save_graph()
- update_graph()
- reason_graph()
- build_graph()
"""

from __future__ import annotations

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


DEFAULT_BASE_IRI = "https://w3id.org/def/orka#"


def load_graph(path: str | Path):
    """Load one ontology graph from disk."""
    source = Path(path)
    return get_ontology(source.resolve().as_uri()).load()


def query_graph(ontology, sparql_query: str):
    """Run one SPARQL query on the graph."""
    rdf_graph = ontology.world.as_rdflib_graph()
    return list(rdf_graph.query(sparql_query))


def save_graph(ontology, path: str | Path, fmt: str = "rdfxml") -> Path:
    """Save one ontology graph to disk."""
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
    """Run reasoning and optionally save the graph."""
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


def build_graph(
    mapping_path: str | Path,
    *,
    base_iri: str = DEFAULT_BASE_IRI,
    robot_name: str = "robot",
) -> dict[str, object]:
    """Build the base graph description from one mapping file.

    The returned value is plain data. The caller decides whether to insert
    these triples into an ontology graph.
    """
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
        triples.append(_triple(algorithm_uri, str(RDF.type), algorithm_class_uri, False))
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


def _orka_uri(base_iri: str, value: str) -> str:
    """Build one ORKA URI from one value."""
    return f"{_normalize_base_iri(base_iri)}{_sanitize_fragment(value)}"


def _resolve_mapping_term(term: str, base_iri: str) -> str:
    """Resolve one mapping term to one full URI."""
    value = str(term).strip()
    if not value:
        raise ValueError("Mapping term cannot be empty.")
    if value.startswith(("http://", "https://")):
        return value
    if value.startswith("orka:"):
        return f"{_normalize_base_iri(base_iri)}{value.split(':', 1)[1]}"
    return f"{_normalize_base_iri(base_iri)}{_sanitize_fragment(value)}"


def _normalize_base_iri(base_iri: str) -> str:
    """Make sure the base IRI ends with a separator."""
    if base_iri.endswith(("#", "/")):
        return base_iri
    return f"{base_iri}#"


def _join_topic(namespace: str, topic_suffix: str) -> str:
    """Join one namespace and one topic suffix."""
    cleaned_namespace = namespace.strip().rstrip("/")
    cleaned_suffix = topic_suffix.strip().lstrip("/")

    if cleaned_namespace and cleaned_suffix:
        return f"{cleaned_namespace}/{cleaned_suffix}"
    if cleaned_namespace:
        return cleaned_namespace
    return cleaned_suffix


def _sanitize_fragment(value: str) -> str:
    """Make one string safe for use in one URI fragment."""
    cleaned = "".join(character if character.isalnum() else "_" for character in value.strip())
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    if not cleaned:
        return "instance"
    if cleaned[0].isdigit():
        return f"n_{cleaned}"
    return cleaned


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
