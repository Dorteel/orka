# ORKA Modular Ontology Builder

This repository provides a modular Python framework for building the **ORKA** ontology with `owlready2`.

You can compose ORKA from modules (`core`, `ros`, `sensors`, `characteristics`, `measurements`), add optional OBOE/SSN alignments, run reasoning, and export materialized OWL files.

## Features

- ORKA-native ontology modeling (classes/properties defined locally).
- Modular composition through a factory builder.
- Optional alignment layer (separate from core modeling):
  - OBOE alignments
  - SSN/SOSA alignments
- External ontology import support in alignments via ontology web IRIs.
- Reasoning and materialization support (HermiT default, Pellet optional).
- Integration test that builds all modules and checks consistency.

## Repository Structure

```text
.
├── builder/
│   ├── __init__.py
│   ├── builder.py                # OrkaBuilder factory
│   ├── orka_core.py              # ORKA-native core vocabulary
│   ├── orka_ros.py               # ROS extension module
│   ├── orka_sensors.py           # Legacy ORKA sensor hierarchy
│   ├── orka_characteristics.py   # Legacy ORKA characteristic hierarchy
│   ├── orka_measurements.py      # Measurement classes + datatype properties
│   └── orka_alignments.py        # OBOE/SSN alignment + import mappings
├── graph_manager.py              # Graph IO, robot injection, reasoning helper
├── main.py                       # Example build entrypoint
├── module_test.py                # Consistency test over all modules
├── owl/                          # Generated OWL outputs
└── legacy/                       # Legacy ORKA resources used for reference
```

## Requirements

- Python 3.10+
- `owlready2`
- Java runtime for HermiT/Pellet reasoning through Owlready2

Install dependency:

```bash
./.venv/bin/pip install owlready2
```

## Base IRI

ORKA modules share a single base namespace:

- `https://w3id.org/def/orka#`

## Building Ontologies

### 1. Quick example (`main.py`)

```bash
./.venv/bin/python main.py
```

This builds a full ORKA ontology (all modules, no alignments) and saves:

- `core + ros + sensors + characteristics + measurements`
- no external alignments
- default output:
  - `owl/orka-core-ros-sensors-characteristics-measurements.owl`

Optional custom output:

```bash
./.venv/bin/python main.py --output owl/my-orka.owl
```

### 2. Programmatic factory usage

```python
from builder import OrkaBuilder

builder = OrkaBuilder()
onto = builder.build(
    modules=["core", "ros", "sensors", "characteristics", "measurements"],
    align_oboe=True,
    align_ssn=True,
)

builder.build_and_save(
    modules=["core", "ros", "sensors", "characteristics", "measurements"],
    output_path="owl/orka-all-modules.owl",
    align_oboe=True,
    align_ssn=True,
)
```

### Supported modules

- `core`
- `ros`
- `sensors`
- `characteristics`
- `measurements`

## Alignments

Alignments are intentionally separated from ORKA-native modeling.

- `define_oboe_alignments(...)` in `builder/orka_alignments.py`
- `define_ssn_alignments(...)` in `builder/orka_alignments.py`

Enable them via `OrkaBuilder.build(..., align_oboe=True, align_ssn=True)`.

### How imports work

When alignments are enabled, the builder now also imports external alignment ontologies into the ORKA ontology via `onto.imported_ontologies`.

- OBOE alignment tries to import:
  - `http://ecoinformatics.org/oboe/oboe.1.2/oboe.owl`
  - `http://ecoinformatics.org/oboe/oboe.1.2/oboe-characteristics.owl`
  - `http://ecoinformatics.org/oboe/oboe.1.2/oboe-standards.owl`
  - `http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl#` (for term alignment)
- SSN alignment tries to import:
  - `https://www.w3.org/ns/sosa/`
  - `https://www.w3.org/ns/ssn/`
  - `https://www.w3.org/ns/ssn/systems/`

These ontologies are loaded directly from their web IRIs. The loader requests explicit ontology serializations (RDF/XML or Turtle) via HTTP `Accept` headers and parses returned bytes with the matching parser to avoid namespace endpoint content-negotiation issues. If loading fails (e.g., no network access), alignment setup raises an explicit error.
Note: `ssn/systems` is imported on a best-effort basis because that namespace endpoint can return non-ontology content in some environments.

## Reasoning and Materialization

Use `graph_manager.reason_graph(...)`:

```python
from graph_manager import reason_graph

result = reason_graph(
    ontology=onto,
    reasoner="hermit",                # default
    infer_property_values=True,
    save_path="owl/orka-inferred.owl" # optional
)

print(result)
# {
#   "consistent": True/False,
#   "reasoner": "hermit"|"pellet",
#   "saved_to": Path|None
# }
```

- Default reasoner: **HermiT** (`sync_reasoner`)
- Alternative: **Pellet** (`reasoner="pellet"`)

## Consistency Test

`module_test.py` builds all modules with both alignments, verifies key imported ontologies are present, runs HermiT reasoning, and checks consistency.

Run:

```bash
./.venv/bin/python module_test.py
```

On success, it also saves a materialized ontology to:

- `owl/orka-all-modules-inferred.owl`

## Graph Manager CLI (Robot Injection)

`graph_manager.py` can parse robot Xacro/URDF content and inject individuals into an ontology graph.

Example:

```bash
./.venv/bin/python graph_manager.py tiago --ontology ./owl/orka-core.owl --output ./owl/orka-core-tiago.owl
```

This workflow:

- creates `./owl/orka-core.owl` if missing (using the lightweight builder helper)
- parses robot data from `urdfs/`
- creates robot/system/sensor individuals
- saves updated ontology

## Notes

- Legacy ontology files remain under `legacy/` for reference and migration checks.
- The modular builder is now the recommended path for creating ORKA ontologies.
