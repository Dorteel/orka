# ORKA TIAGO Graph Builder

This repo builds an OWL graph for a robot using ORKA classes and sensor mappings from Xacro/URDF files.

## Prerequisites

- Python 3.10+
- `owlready2`

Install dependency:

```bash
./.venv/bin/pip install owlready2
```

## Build TIAGO Graph (CLI)

Run:

```bash
./.venv/bin/python graph_manager.py tiago --ontology ./owl/orka-core.owl --output ./owl/orka-core-tiago.owl
```

This will:

- create `./owl/orka-core.owl` if it does not exist
- parse TIAGO files from `./urdfs/tiago`
- add robot/system/sensor individuals
- save the updated graph to `./owl/orka-core-tiago.owl`

## Run Test Script

Use the included runnable test script:

```bash
./.venv/bin/python test_tiago_graph.py
```

Optional custom output:

```bash
./.venv/bin/python test_tiago_graph.py --output ./owl/orka-core-tiago-test.owl
```

The script builds a TIAGO-based graph and validates:

- robot/system instances are created
- at least one sensor is created
- each created sensor links to the created system with `implementedBy`
- output ontology file is written
