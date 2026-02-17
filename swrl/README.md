# ORKA SWRL Rules

This folder stores SWRL rule resources for ORKA.

- `orka_legacy_swrl.owl` is extracted from `legacy/owl/orka.owl`.
- It currently contains the three legacy rule implications:
  - `Proprioception`
  - `CanDetect`
  - `Touch Sensor Detection`

You can refresh this file programmatically via the builder SWRL utility:

```python
from builder.orka_swrl import update_swrl_rules_file

update_swrl_rules_file(
    source_owl_path="legacy/owl/orka.owl",
    output_path="swrl/orka_legacy_swrl.owl",
)
```
