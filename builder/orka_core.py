"""ORKA core ontology module.

This module defines ORKA-native core classes and properties (without importing
OBOE/SSN classes directly). External alignments are defined separately in
``builder/orka_alignments.py``.
"""

from __future__ import annotations

from owlready2 import ObjectProperty, Thing, get_ontology

DEFAULT_BASE_IRI = "https://w3id.org/def/orka#"


def get_orka_ontology(base_iri: str = DEFAULT_BASE_IRI):
    """Create or load the ORKA ontology bound to the given base IRI."""
    return get_ontology(base_iri)


def define_core_module(onto) -> dict[str, type]:
    """Define ORKA core classes and properties on the given ontology."""
    existing = {
        "Entity": onto.Entity,
        "Observation": onto.Observation,
        "Measurement": onto.Measurement,
        "Characteristic": onto.Characteristic,
        "MeasurementStandard": onto.MeasurementStandard,
        "Procedure": onto.Procedure,
        "Result": onto.Result,
        "Sensor": onto.Sensor,
        "System": onto.System,
        "Platform": onto.Platform,
        "Robot": onto.Robot,
    }
    if all(existing.values()):
        return existing

    with onto:
        # OBOE-like ORKA-native core
        class Entity(Thing):
            """A thing that can be observed or described."""

        class Observation(Thing):
            """An observation event about an entity."""

        class Measurement(Thing):
            """A measurement produced in an observation context."""

        class Characteristic(Thing):
            """An observable or inferable characteristic."""

        class MeasurementStandard(Thing):
            """A standard/unit used to express measurements."""

        # SSN/SOSA-like ORKA-native core
        class Procedure(Thing):
            """A method used during sensing or computation."""

        class Result(Thing):
            """A result value or output artifact."""

        class Sensor(Thing):
            """A sensing device."""

        class System(Thing):
            """A system that can host sensors or execute procedures."""

        class Platform(Thing):
            """A physical or virtual platform."""

        # ORKA-specific classes used across modules
        class PhysicalEntity(Entity):
            """A material entity in the environment."""

        class Agent(Entity):
            """An acting entity."""

        class DetectableEntity(PhysicalEntity):
            """An entity that can be detected by a sensor/procedure."""

        class Robot(Platform, Agent):
            """A robotic platform."""

        class Knowledge_Repository(Thing):
            """An external/internal knowledge source."""

        class Context(Thing):
            """A task or scene context with required entities."""

        class ComputerVisionAlgorithm(Procedure):
            """A computer-vision procedure."""

        class LocalisationProcedure(Procedure):
            """A procedure for localization."""

        class Position_Sensor(Sensor):
            """A sensor for position-related quantities."""

        class Heading_Sensor(Sensor):
            """A sensor for heading-related quantities."""

        class ProprioceptorSensor(Sensor):
            """A sensor observing robot internal state."""

        # Object properties matching legacy ORKA vocabulary
        class hasMeasurement(ObjectProperty):
            domain = [Observation]
            range = [Measurement]

        class ofEntity(ObjectProperty):
            domain = [Observation]
            range = [Entity]

        class observedIn(ObjectProperty):
            domain = [Entity]
            range = [Observation]

        class ofCharacteristic(ObjectProperty):
            domain = [Measurement]
            range = [Characteristic]

        class hasResult(ObjectProperty):
            domain = [Measurement]
            range = [Result]

        class madeBySensor(ObjectProperty):
            domain = [Measurement]
            range = [Sensor]

        class usedProcedure(ObjectProperty):
            domain = [Measurement]
            range = [Procedure]

        class measuresUsingStandard(ObjectProperty):
            domain = [Measurement]
            range = [MeasurementStandard]

        class hasCharacteristic(ObjectProperty):
            domain = [Entity]
            range = [Characteristic]

        class characteristicFor(ObjectProperty):
            domain = [Characteristic]
            range = [Entity]

        class describedBy(ObjectProperty):
            domain = [Entity]
            range = [Knowledge_Repository]

        class hasRequiredEntity(ObjectProperty):
            domain = [Context]
            range = [Entity]

        class observesCharacteristic(ObjectProperty):
            domain = [Sensor]
            range = [Characteristic]

        class implementedOn(ObjectProperty):
            domain = [Procedure]
            range = [Robot]

        class canDetect(ObjectProperty):
            domain = [Procedure]
            range = [DetectableEntity]

        class canBeDetectedBy(ObjectProperty):
            domain = [DetectableEntity]
            range = [Procedure]

        ofEntity.inverse_property = observedIn
        hasCharacteristic.inverse_property = characteristicFor
        canDetect.inverse_property = canBeDetectedBy

    return {
        "Entity": onto.Entity,
        "Observation": onto.Observation,
        "Measurement": onto.Measurement,
        "Characteristic": onto.Characteristic,
        "MeasurementStandard": onto.MeasurementStandard,
        "Procedure": onto.Procedure,
        "Result": onto.Result,
        "Sensor": onto.Sensor,
        "System": onto.System,
        "Platform": onto.Platform,
        "Robot": onto.Robot,
    }


def build_core_ontology(base_iri: str = DEFAULT_BASE_IRI):
    """Convenience builder for a core-only ontology."""
    onto = get_orka_ontology(base_iri=base_iri)
    define_core_module(onto)
    return onto
