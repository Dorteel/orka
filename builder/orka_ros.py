"""ORKA ROS ontology module.

This module extends the ORKA core ontology with ROS concepts.
"""

from __future__ import annotations

from owlready2 import ObjectProperty

from builder.orka_core import DEFAULT_BASE_IRI, define_core_module, get_orka_ontology


def define_ros_module(onto) -> dict[str, type]:
    """Define ROS-specific classes and properties on the given ontology."""
    existing = {
        "ROSNode": onto.ROSNode,
        "Topic": onto.Topic,
        "Message": onto.Message,
        "Publisher": onto.Publisher,
        "Subscriber": onto.Subscriber,
        "ROSService": onto.ROSService,
    }
    if all(existing.values()):
        return existing

    if onto.Entity is None:
        define_core_module(onto)

    with onto:
        class ROSNode(onto.Agent):
            """An executable ROS computation unit."""

        class Topic(onto.Entity):
            """A named communication channel in ROS."""

        class Message(onto.Entity):
            """A data payload exchanged over ROS interfaces."""

        class Publisher(onto.Procedure):
            """A procedure that sends messages to a topic."""

        class Subscriber(onto.Procedure):
            """A procedure that receives messages from a topic."""

        class ROSService(onto.Procedure):
            """A request-reply interaction in ROS."""

        class publishesTopic(ObjectProperty):
            domain = [ROSNode]
            range = [Topic]

        class subscribesToTopic(ObjectProperty):
            domain = [ROSNode]
            range = [Topic]

        class carriesMessage(ObjectProperty):
            domain = [Topic]
            range = [Message]

    return {
        "ROSNode": onto.ROSNode,
        "Topic": onto.Topic,
        "Message": onto.Message,
        "Publisher": onto.Publisher,
        "Subscriber": onto.Subscriber,
        "ROSService": onto.ROSService,
    }


def build_ros_ontology(base_iri: str = DEFAULT_BASE_IRI):
    """Convenience builder for core + ROS ontology."""
    onto = get_orka_ontology(base_iri=base_iri)
    define_core_module(onto)
    define_ros_module(onto)
    return onto
