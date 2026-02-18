# ORKA SWRL Rules

SWRL rules are stored as text and loaded with Owlready2.

## Rule file format

File: `swrl/legacy_rules.swrl`

Each non-empty, non-comment line must be:

`<Label>: <SWRL rule>`

Example:

`CanDetect: inDataSet(?e, ?d), trainedOnDataSet(?a, ?d), Procedure(?a) -> canDetect(?a, ?e)`

## Applying rules

```python
from builder import OrkaBuilder

onto = OrkaBuilder().build(
    modules=["core", "ros", "sensors", "characteristics", "measurements"],
    include_swrl=True,
    swrl_rules_path="swrl/legacy_rules.swrl",
    update_swrl_rules=True,
)
```
