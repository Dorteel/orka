"""ORKA core ontology module.

This module defines the shared ORKA base IRI and high-level taxonomy.
"""

from __future__ import annotations

from owlready2 import ObjectProperty, Thing, get_ontology

DEFAULT_BASE_IRI = "https://w3id.org/def/orka/core#"


def get_orka_ontology(base_iri: str = DEFAULT_BASE_IRI):
    """Create or load the ORKA ontology bound to the given base IRI."""
    return get_ontology(base_iri)


def define_core_module(onto) -> dict[str, type]:
    """Define ORKA core classes and properties on the given ontology."""
    existing = {
        "Entity": onto.Entity,
        "Process": onto.Process,
        "SpatialThing": onto.SpatialThing,
        "PhysicalObject": onto.PhysicalObject,
        "Agent": onto.Agent,
        "Robot": onto.Robot,
    }
    if all(existing.values()):
        return existing

    with onto:
        class Entity(Thing):
            """Anything that can be represented in ORKA."""

        class Process(Thing):
            """A temporal activity or operation."""

        class SpatialThing(Thing):
            """Anything with a spatial extent."""

        class PhysicalObject(Entity, SpatialThing):
            """A material entity that occupies space."""

        class Agent(Entity):
            """An entity capable of acting in processes."""

        class Robot(Agent, PhysicalObject):
            """A robotic agent."""

        class hasPart(ObjectProperty):
            domain = [Entity]
            range = [Entity]

        class participatesIn(ObjectProperty):
            domain = [Entity]
            range = [Process]

        class locatedIn(ObjectProperty):
            domain = [SpatialThing]
            range = [SpatialThing]

    return {
        "Entity": onto.Entity,
        "Process": onto.Process,
        "SpatialThing": onto.SpatialThing,
        "PhysicalObject": onto.PhysicalObject,
        "Agent": onto.Agent,
        "Robot": onto.Robot,
    }


def build_core_ontology(base_iri: str = DEFAULT_BASE_IRI):
    """Convenience builder for a core-only ontology."""
    onto = get_orka_ontology(base_iri=base_iri)
    define_core_module(onto)
    return onto
