"""Factory-style ORKA ontology builder."""

from __future__ import annotations

from pathlib import Path

from builder.orka_alignments import define_oboe_alignments, define_ssn_alignments
from builder.orka_characteristics import define_characteristic_module
from builder.orka_core import DEFAULT_BASE_IRI, define_core_module, get_orka_ontology
from builder.orka_measurements import define_measurement_module
from builder.orka_ros import define_ros_module
from builder.orka_sensors import define_sensor_module
from builder.orka_swrl import apply_swrl_rules


VALID_MODULES = {"core", "ros", "sensors", "characteristics", "measurements"}


class OrkaBuilder:
    """Compose ORKA ontology modules and export a single OWL file."""

    def __init__(self, base_iri: str = DEFAULT_BASE_IRI):
        self.base_iri = base_iri

    def build(
        self,
        modules: list[str] | tuple[str, ...] | set[str],
        *,
        align_oboe: bool = False,
        align_ssn: bool = False,
        include_swrl: bool = False,
        swrl_rules_path: str | Path = "swrl/legacy_rules.swrl",
        update_swrl_rules: bool = False,
    ):
        """Build an ontology with selected modules and optional alignments."""
        normalized = {module.lower() for module in modules}
        unknown = normalized - VALID_MODULES
        if unknown:
            unknown_list = ", ".join(sorted(unknown))
            raise ValueError(f"Unknown modules requested: {unknown_list}")

        onto = get_orka_ontology(base_iri=self.base_iri)

        if "core" in normalized or normalized.intersection(
            {"ros", "sensors", "characteristics", "measurements"}
        ):
            define_core_module(onto)
        if "ros" in normalized:
            define_ros_module(onto)
        if "sensors" in normalized:
            define_sensor_module(onto)
        if "characteristics" in normalized:
            define_characteristic_module(onto)
        if "measurements" in normalized:
            define_measurement_module(onto)

        if align_oboe:
            define_oboe_alignments(onto)
        if align_ssn:
            define_ssn_alignments(onto)
        if include_swrl:
            apply_swrl_rules(
                onto=onto,
                rules_path=swrl_rules_path,
                update_existing=update_swrl_rules,
            )

        return onto

    def build_and_save(
        self,
        modules: list[str] | tuple[str, ...] | set[str],
        output_path: str | Path,
        fmt: str = "rdfxml",
        *,
        align_oboe: bool = False,
        align_ssn: bool = False,
        include_swrl: bool = False,
        swrl_rules_path: str | Path = "swrl/legacy_rules.swrl",
        update_swrl_rules: bool = False,
    ) -> Path:
        """Build selected modules and save the ontology to disk."""
        onto = self.build(
            modules=modules,
            align_oboe=align_oboe,
            align_ssn=align_ssn,
            include_swrl=include_swrl,
            swrl_rules_path=swrl_rules_path,
            update_swrl_rules=update_swrl_rules,
        )
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        onto.save(file=str(output), format=fmt)
        return output
