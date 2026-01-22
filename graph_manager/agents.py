"""
Agent management utilities for ORKA ontology.
"""

from rdflib import Graph, URIRef, Namespace, RDF
from typing import List

# Define ORKA namespace
ORKA = Namespace("https://w3id.org/def/orka#")


def load_orka(graph: Graph) -> None:
    """
    Load ORKA ontology into the graph.
    
    Args:
        graph: RDFlib Graph to load ORKA into
    """
    orka_url = "owl/orka.owl"
    try:
        graph.parse(orka_url, format="xml")
    except Exception as e:
        print(f"Note: Could not load ORKA from {orka_url}: {e}")
        print("Proceeding with manual ORKA namespace definitions")
    
    # Bind namespace
    graph.bind("orka", ORKA)


def add_agent(graph: Graph, agent_id: str, agent_type: str, sensors: List[str] = None) -> URIRef:
    """
    Add an agent (human or robot) with sensors to the RDF graph.
    
    Args:
        graph: RDFlib Graph to add the agent to
        agent_id: Unique identifier for the agent
        agent_type: Either "robot" or "human"
        sensors: Optional list of sensor IDs to add to the agent
    
    Returns:
        URIRef of the created agent
    
    Raises:
        ValueError: If agent_type is not "robot" or "human"
    """
    if agent_type.lower() not in ["robot", "human"]:
        raise ValueError(f"agent_type must be 'robot' or 'human', got '{agent_type}'")
    
    # Create agent URI
    agent_uri = ORKA[agent_id]
    
    # Determine the correct ORKA class
    if agent_type.lower() == "robot":
        agent_class = ORKA.Robot
    else:  # human
        agent_class = ORKA.Human
    
    # Add agent to graph
    graph.add((agent_uri, RDF.type, agent_class))
    
    # Add sensors if provided
    if sensors:
        for sensor_id in sensors:
            sensor_uri = ORKA[sensor_id]
            # Create sensor with basic type
            graph.add((sensor_uri, RDF.type, ORKA.Sensor))
            # Link sensor to agent
            graph.add((agent_uri, ORKA.hasSensor, sensor_uri))
    
    return agent_uri
