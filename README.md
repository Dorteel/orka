# ORKA Ontology Builder And Runtime Utilities

This repository provides the current Python implementation of **ORKA** in three layers:

- the modular ontology builder in `builder/`
- graph utilities in `graph_manager.py`
- ROS 2 runtime services in `orka_ros/`

The intended flow is:

1. define and export the ontology with the builder
2. load/query/reason/inject runtime individuals with `graph_manager`
3. expose selected runtime functionality as ROS services in `orka_ros`

## Current Status

- `builder/` is the main ontology-definition path.
- `orka_builder.py` remains only as a compatibility wrapper and should not be used for new code.
- `graph_manager.py` is the main place for graph IO, reasoning, and robot injection.
- `orka_ros/` wraps the builder/graph functionality as ROS 2 services.
- External ontology alignments are not part of the stable runtime path yet and should be treated as TODO/integration work.

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
├── module_test.py                # Integration test (currently alignment-dependent)
├── builder/swrl/                 # SWRL rule files (text format)
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

# Optional: add SWRL rules from builder/swrl/legacy_rules.swrl
onto_with_rules = builder.build(
    modules=["core", "ros", "sensors", "characteristics", "measurements"],
    include_swrl=True,
    swrl_rules_path="builder/swrl/legacy_rules.swrl",
    update_swrl_rules=True,
)
```

### Supported modules

- `core`
- `ros`
- `sensors`
- `characteristics`
- `measurements`

## Alignments

Alignments are intentionally separated from ORKA-native modeling and are not
currently part of the recommended local runtime workflow.

- `define_oboe_alignments(...)` in `builder/orka_alignments.py`
- `define_ssn_alignments(...)` in `builder/orka_alignments.py`

Today this path still depends on fetching external ontologies over the network,
so it is best treated as TODO/integration work rather than a baseline feature.

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

## Testing

`module_test.py` currently exercises the alignment path and reasoning together.
Because alignments are fetched from the web, it can fail in offline or
restricted environments.

Run:

```bash
./.venv/bin/python module_test.py
```

On success, it also saves a materialized ontology to:

- `owl/orka-all-modules-inferred.owl`

## Graph Manager

`graph_manager.py` is the main runtime utility layer. It provides:

- ontology load/save helpers
- SPARQL querying
- reasoning with HermiT or Pellet
- robot instance injection from `urdfs/`

## Graph Manager CLI (Robot Injection)

`graph_manager.py` can parse robot Xacro/URDF content and inject individuals into an ontology graph.

Example:

```bash
./.venv/bin/python graph_manager.py tiago --ontology ./owl/orka-core.owl --output ./owl/orka-core-tiago.owl
```

This workflow:

- creates `./owl/orka-core.owl` if missing (using the modular builder)
- parses robot data from `urdfs/`
- creates robot/system/sensor individuals
- saves updated ontology

## Notes

- Legacy ontology files remain under `legacy/` for reference and migration checks.
- The modular builder is the recommended path for creating ORKA ontologies.
- Runtime class names used by ROS mappings should be taken from:
  - `builder/orka_core.py`
  - `builder/orka_ros.py`
  - `builder/orka_sensors.py`
  - `builder/orka_characteristics.py`
  - `builder/orka_measurements.py`
