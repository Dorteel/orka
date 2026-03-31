"""Build the ORKA core ontology.

This module defines the ORKA-native core vocabulary and can also be run as a
script to generate ``orka-core.owl``.

Usage:
    python orka_core.py
    python orka_core.py /path/to/orka-core.owl
"""

from __future__ import annotations

import sys
from pathlib import Path

from owlready2 import ObjectProperty, Thing, get_ontology

DEFAULT_BASE_IRI = "https://w3id.org/def/orka#"
DEFAULT_OUTPUT = Path(__file__).resolve().with_name("orka-core.owl")


class OrkaCore:
    """Base builder for the ORKA core ontology.

    Later ontology builders can inherit from this class and extend the ontology
    by overriding ``extend()``.
    """

    def __init__(self, base_iri: str = DEFAULT_BASE_IRI):
        self.base_iri = base_iri
        self.onto = get_ontology(base_iri)

    def build(self):
        """Build the ontology in memory and return it."""
        if getattr(self.onto, "Entity", None) is None:
            self._define_core()
            self.extend()
        return self.onto

    def extend(self):
        """Hook for child classes to add more vocabulary."""
        pass

    def save(self, output_path: str | Path = DEFAULT_OUTPUT):
        """Build and save the ontology to disk."""
        output_path = Path(output_path).resolve()
        self.build().save(file=str(output_path), format="rdfxml")
        return output_path

    def _define_core(self):
        """Define the ORKA core vocabulary."""
        with self.onto:
            # -----------------------------------------------------------------
            # Core classes
            # -----------------------------------------------------------------

            class Entity(Thing):
                """A thing that can be observed or described."""

            class Observation(Thing):
                """An observation event about an entity."""

            class Measurement(Thing):
                """A measurement produced in an observation context."""

            class Characteristic(Thing):
                """An observable or inferable characteristic."""

            class Standard(Thing):
                """A standard or unit used to express measurements."""

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

            # -----------------------------------------------------------------
            # ORKA-specific classes
            # -----------------------------------------------------------------

            class PhysicalEntity(Entity):
                """A material entity in the environment."""

            class Agent(Entity):
                """An acting entity."""

            class DetectableEntity(PhysicalEntity):
                """An entity that can be detected by a sensor or procedure."""

            class Robot(Platform, Agent):
                """A robotic platform."""

            class KnowledgeRepository(Thing):
                """An external or internal knowledge source."""

            class Context(Thing):
                """A task or scene context with required entities."""

            class ComputerVisionAlgorithm(Procedure):
                """A computer-vision procedure."""

            class LocalisationProcedure(Procedure):
                """A procedure for localization."""

            class PositionSensor(Sensor):
                """A sensor for position-related quantities."""

            class HeadingSensor(Sensor):
                """A sensor for heading-related quantities."""

            class ProprioceptorSensor(Sensor):
                """A sensor observing the robot's internal state."""

            # -----------------------------------------------------------------
            # Object properties
            # -----------------------------------------------------------------

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

            class madeMeasurement(ObjectProperty):
                domain = [Sensor]
                range = [Measurement]

            class measuresUsingStandard(ObjectProperty):
                domain = [Sensor]
                range = [Standard]

            class usedBySensor(ObjectProperty):
                domain = [Standard]
                range = [Sensor]

            class usedProcedure(ObjectProperty):
                domain = [Measurement]
                range = [Procedure]

            class hasCharacteristic(ObjectProperty):
                domain = [Entity]
                range = [Characteristic]

            class characteristicFor(ObjectProperty):
                domain = [Characteristic]
                range = [Entity]

            class describedBy(ObjectProperty):
                domain = [Entity]
                range = [KnowledgeRepository]

            class hasRequiredEntity(ObjectProperty):
                domain = [Context]
                range = [Entity]

            class observesCharacteristic(ObjectProperty):
                domain = [Sensor]
                range = [Characteristic]

            class implementedOn(ObjectProperty):
                domain = [Procedure]
                range = [Robot]

            class implementedBy(ObjectProperty):
                domain = [Sensor]
                range = [System]

            class canDetect(ObjectProperty):
                domain = [Procedure]
                range = [DetectableEntity]

            class canBeDetectedBy(ObjectProperty):
                domain = [DetectableEntity]
                range = [Procedure]

            class hostedBy(ObjectProperty):
                domain = [System]
                range = [Platform]
            # -----------------------------------------------------------------
            # Inverse properties
            # -----------------------------------------------------------------

            madeBySensor.inverse_property = madeMeasurement
            measuresUsingStandard.inverse_property = usedBySensor
            ofEntity.inverse_property = observedIn
            hasCharacteristic.inverse_property = characteristicFor
            canDetect.inverse_property = canBeDetectedBy


def main():
    """CLI entry point."""
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    builder = OrkaCore()
    saved_path = builder.save(output_path)
    print(f"Saved ORKA core ontology to: {saved_path}")


if __name__ == "__main__":
    main()