"""ORKA ontology builder.

This module only builds and saves the OWL ontology.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import new_class

from owlready2 import ObjectProperty, Thing, get_ontology

DEFAULT_BASE_IRI = "https://w3id.org/def/orka/core#"


@dataclass(frozen=True)
class ClassSpec:
    name: str
    parent: str | None = None


@dataclass(frozen=True)
class ObjectPropertySpec:
    name: str
    domain: str
    range: str


CLASS_SPECS: tuple[ClassSpec, ...] = (
    # OBOE-aligned core
    ClassSpec("Observation"),
    ClassSpec("Measurement"),
    ClassSpec("Entity"),
    ClassSpec("Characteristic"),
    ClassSpec("MeasurementStandard"),
    # SSN-aligned core
    ClassSpec("Procedure"),
    ClassSpec("Result"),
    ClassSpec("Sensor"),
    ClassSpec("System"),
    ClassSpec("Platform"),
    # ORKA lightweight extensions
    ClassSpec("Robot", parent="Platform"),
    ClassSpec("ComputerVisionAlgorithm", parent="Procedure"),
    ClassSpec("LocalisationProcedure", parent="Procedure"),
    ClassSpec("PositionSensor", parent="Sensor"),
    ClassSpec("HeadingSensor", parent="Sensor"),
    ClassSpec("ProprioceptorSensor", parent="Sensor"),
    ClassSpec("KnowledgeRepository"),
    ClassSpec("Context"),
)


OBJECT_PROPERTY_SPECS: tuple[ObjectPropertySpec, ...] = (
    ObjectPropertySpec("hasMeasurement", "Observation", "Measurement"),
    ObjectPropertySpec("ofEntity", "Observation", "Entity"),
    ObjectPropertySpec("hasResult", "Measurement", "Result"),
    ObjectPropertySpec("madeBySensor", "Measurement", "Sensor"),
    ObjectPropertySpec("usedProcedure", "Measurement", "Procedure"),
    ObjectPropertySpec("usesStandard", "Measurement", "MeasurementStandard"),
    ObjectPropertySpec("ofCharacteristic", "Measurement", "Characteristic"),
    ObjectPropertySpec("hasCharacteristic", "Entity", "Characteristic"),
    ObjectPropertySpec("characteristicFor", "Characteristic", "Entity"),
    ObjectPropertySpec("describedBy", "Entity", "KnowledgeRepository"),
    ObjectPropertySpec("hasRequiredEntity", "Context", "Entity"),
    ObjectPropertySpec("observes", "Sensor", "Characteristic"),
    ObjectPropertySpec("implementedBy", "Sensor", "System"),
    ObjectPropertySpec("hostedBy", "System", "Platform"),
    ObjectPropertySpec("implementedOn", "Procedure", "Robot"),
)


def build_orka_core(base_iri: str = DEFAULT_BASE_IRI):
    """Build a lightweight EL-style ORKA core ontology in memory."""
    ontology = get_ontology(base_iri)

    with ontology:
        class_map: dict[str, type] = {}

        for spec in CLASS_SPECS:
            parent = Thing if spec.parent is None else class_map[spec.parent]
            class_map[spec.name] = new_class(spec.name, (parent,))

        for spec in OBJECT_PROPERTY_SPECS:
            prop = new_class(spec.name, (ObjectProperty,))
            prop.domain = [class_map[spec.domain]]
            prop.range = [class_map[spec.range]]

    return ontology


def save_orka_core(ontology, output_path: str | Path, fmt: str = "rdfxml") -> Path:
    """Persist the ontology to disk."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    ontology.save(file=str(output), format=fmt)
    return output


def build_and_save_orka_core(
    output_path: str = './owl/orka-core.owl',
    base_iri: str = DEFAULT_BASE_IRI,
    fmt: str = "rdfxml",
):
    """Convenience wrapper to build and immediately save ORKA core."""
    ontology = build_orka_core(base_iri=base_iri)
    save_orka_core(ontology=ontology, output_path=output_path, fmt=fmt)
    return ontology


if __name__ == "__main__":
    build_and_save_orka_core()