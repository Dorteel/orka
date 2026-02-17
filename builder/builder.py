"""Factory-style ORKA ontology builder."""

from __future__ import annotations

from pathlib import Path

from builder.orka_core import DEFAULT_BASE_IRI, define_core_module, get_orka_ontology
from builder.orka_ros import define_ros_module
from builder.orka_sensors import define_sensor_module


VALID_MODULES = {"core", "ros", "sensors"}


class OrkaBuilder:
    """Compose ORKA ontology modules and export a single OWL file."""

    def __init__(self, base_iri: str = DEFAULT_BASE_IRI):
        self.base_iri = base_iri

    def build(self, modules: list[str] | tuple[str, ...] | set[str]):
        """Build an ontology with the selected modules."""
        normalized = {module.lower() for module in modules}
        unknown = normalized - VALID_MODULES
        if unknown:
            unknown_list = ", ".join(sorted(unknown))
            raise ValueError(f"Unknown modules requested: {unknown_list}")

        onto = get_orka_ontology(base_iri=self.base_iri)

        if "core" in normalized or normalized.intersection({"ros", "sensors"}):
            define_core_module(onto)
        if "ros" in normalized:
            define_ros_module(onto)
        if "sensors" in normalized:
            define_sensor_module(onto)

        return onto

    def build_and_save(
        self,
        modules: list[str] | tuple[str, ...] | set[str],
        output_path: str | Path,
        fmt: str = "rdfxml",
    ) -> Path:
        """Build selected modules and save the ontology to disk."""
        onto = self.build(modules=modules)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        onto.save(file=str(output), format=fmt)
        return output
