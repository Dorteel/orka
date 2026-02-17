"""ORKA sensors ontology module.

This module extends the ORKA core ontology with sensor taxonomies.
"""

from __future__ import annotations

from owlready2 import ObjectProperty

from builder.orka_core import DEFAULT_BASE_IRI, define_core_module, get_orka_ontology


MODULE_NAME = "sensors"


def define_sensor_module(onto) -> dict[str, type]:
    """Define sensor-specific classes and properties on the given ontology."""
    existing = {
        "Sensor": onto.Sensor,
        "Lidar": onto.Lidar,
        "Camera": onto.Camera,
        "IMU": onto.IMU,
    }
    if all(existing.values()):
        return existing

    if onto.Entity is None:
        define_core_module(onto)

    with onto:
        class Sensor(onto.PhysicalObject):
            """A physical device that measures the environment."""

        class Lidar(Sensor):
            """A range sensor based on laser scanning."""

        class Camera(Sensor):
            """A visual sensor capturing image streams."""

        class IMU(Sensor):
            """An inertial measurement unit."""

        class observes(ObjectProperty):
            domain = [Sensor]
            range = [onto.Entity]

        class mountedOn(ObjectProperty):
            domain = [Sensor]
            range = [onto.Robot]

    return {
        "Sensor": onto.Sensor,
        "Lidar": onto.Lidar,
        "Camera": onto.Camera,
        "IMU": onto.IMU,
    }


def build_sensor_ontology(base_iri: str = DEFAULT_BASE_IRI):
    """Convenience builder for core + sensors ontology."""
    onto = get_orka_ontology(base_iri=base_iri)
    define_core_module(onto)
    define_sensor_module(onto)
    return onto
