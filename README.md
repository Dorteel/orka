# ORKA: Ontology-Driven Robotics Knowledge Architecture

## Overview

ORKA is a **semantic knowledge representation system** for robotics. It's built on **ontologies** — machine-readable formal descriptions of concepts, relationships, and properties. ORKA provides a structured way to represent "what things are" in a robot system (sensors, measurements, observations, etc.) so a computer can reason about them.

---

## Dependencies

The system uses two core semantic web libraries:

- **owlready2 (0.50)** — Python library for creating and manipulating OWL ontologies
- **rdflib (7.6.0)** — Library for working with RDF graphs and running SPARQL queries

These libraries enable you to define knowledge in a machine-understandable format and perform automated reasoning.

---

## Architecture: Layered Ontology Building

The `ontology_building/` directory contains a layered architecture where each module builds on previous ones, enabling incremental knowledge representation:

### Layer-by-Layer Breakdown

1. **orka_core.py**
   - Base vocabulary and fundamental concepts
   - Defines: Entity, Observation, Measurement, Sensor, System, Robot, Platform

2. **orka_alignments.py**
   - Connects ORKA to W3C (World Wide Web Consortium) standards
   - Enables interoperability with: SSN (Semantic Sensor Network), SOSA (Sensor/Observation), OBOE
   - Ensures ORKA integrates with broader semantic web standards

3. **orka_conceptualspaces.py**
   - Adds cognitive modeling capabilities
   - Defines: ConceptualSpace, Domain, Concept, QualityDimension, PrototypicalInstance
   - Enables reasoning about abstract spaces and quality characteristics

4. **orka_full.py**
   - Defines 10+ sensor types organized in hierarchies
   - Sensor types: Distance, Light, Speed, Position, Heading, Touch, Altitude, Motor, and more
   - Provides concrete sensor vocabulary for robotics applications

5. **orka_ros.py**
   - Bridges ORKA to the Robot Operating System (ROS)
   - Defines: ROSTopic, ROSService, ROSMessageType
   - Properties: `publishesTo`, `subscribesTo`
   - Enables semantic representation of ROS communication

6. **orka_emotions.py**
   - Extends conceptual spaces for affective modeling
   - Adds emotion and affect-related concepts to the ontology

7. **orka_all.py**
   - **Composite builder** that orchestrates all modules
   - Combines all layers into one unified, comprehensive ontology
   - Entry point for building the complete knowledge graph

This layering allows you to:
- Test core concepts independently
- Add ROS integration incrementally
- Extend with domain-specific reasoning (emotions, cognitive spaces, etc.)
- Maintain modularity while building a unified system

---

## Runtime Management: The Manager

The `ontology_manager/manager.py` provides the runtime engine for working with ontologies:

### GraphManager (Base Class)

Core functionality for graph manipulation:

- **`load_graph(path)`** — Load an OWL file from disk into memory
- **`save_graph(path)`** — Write ontology back to disk (RDF/XML format)
- **`query_graph(sparql_query)`** — Execute SPARQL queries to extract data and facts
- **`reason_graph(reasoner='hermit')`** — Run semantic inference to derive new facts
  - Supports two reasoners: Hermit (default) or Pellet
  - Options: `infer_property_values`, `infer_data_property_values`, `debug`
  - Can save inferred ontology to separate file
- **`uid(prefix)`** — Generate unique identifiers with prefix
- **`safe_name(value, prefix)`** — Sanitize names for use in ontology

### OrkaManager (Extended Class)

Robotics-specific functionality:

- **`build_robot_base_graph(sensors=[...])`** — Create a robot instance with hierarchy
  - Instantiates Robot → System → Sensor hierarchy
  - Associates software procedures with each sensor
  - Initializes semantic representation of a concrete robot

---

## Execution Pipeline: main.py

The `main.py` file orchestrates the complete workflow:

```python
# Step 1: Build the complete ontology
from ontology_building.orka_all import OrkaAll
builder = OrkaAll()
onto = builder.build()
builder.save("owl/orka-all.owl")

# Step 2: Load it into the manager (reasoning engine)
from ontology_manager.manager import OrkaManager
manager = OrkaManager()
manager.load_graph("owl/orka-all.owl")

# Step 3: Create a robot instance with sensors
manager.build_robot_base_graph(sensors=['camera', 'lidar'])

# Step 4: Run semantic reasoning (infer new facts)
manager.reason_graph(save_path='owl/orka-reasoner.owl')

# Step 5: Save the result
manager.save_graph("owl/orka-test.owl")
```

**Workflow Summary:**
1. **Build** — Compose all ontology layers into unified vocabulary
2. **Load** — Initialize reasoning engine with unified ontology
3. **Instantiate** — Create robot instance with concrete sensors
4. **Reason** — Derive new facts through semantic inference
5. **Persist** — Save results to disk

---

## Output Files: The OWL Directory

The `owl/` directory contains ontology snapshots and outputs at various stages:

| File | Purpose |
|------|---------|
| **orka-core.owl** | Base vocabulary only (foundational concepts) |
| **orka-alignments.owl** | Base + W3C standard alignments (SSN, SOSA, OBOE) |
| **orka-cs.owl** | + Conceptual spaces extension |
| **orka-full.owl** | + All sensor types and hierarchies |
| **orka-all.owl** | **Complete unified vocabulary** (main composite output from `main.py`) |
| **orka-reasoner.owl** | All inferred facts after semantic reasoning |
| **orka-test.owl** | Snapshot after building a robot instance |
| **orka-base-graph.owl** | Robot base graph structure |

Each file represents a stage in the ontology development, from basic concepts to the fully reasoned, instantiated knowledge graph.

---

## The Complete Picture

```
ontology_building/*.py (7 layers)
    ↓ (composed via OrkaAll)
owl/orka-all.owl (unified vocabulary)
    ↓ (loaded into OrkaManager)
main.py
    ↓ (instantiate robot + reasoning)
owl/orka-reasoner.owl (inferred knowledge)
    ↓
owl/orka-test.owl (final snapshot)
```

## What ORKA Does

You're building a **semantic knowledge graph** where you:

1. **Define** what concepts mean (sensors, measurements, observations, ROS topics, etc.)
2. **Align** with international standards (W3C, SSN, SOSA) for interoperability
3. **Create instances** of those concepts (this robot, with this camera and lidar, etc.)
4. **Use automated reasoning** to infer new facts
   - Example: "This sensor produces images, therefore this robot can see"
   - Reasoning engine automatically derives consequences from ontology rules

This enables machines to:
- Understand the semantic meaning of robot capabilities
- Automatically derive new knowledge
- Enable interoperability across systems
- Support complex queries and reasoning tasks

---

## Getting Started

To run the ORKA system:

```bash
cd orka/
pip install -r requirements.txt
python main.py
```

This will:
- Build all ontology layers
- Create a test robot with camera and lidar sensors
- Run semantic reasoning
- Generate output files in `owl/`
