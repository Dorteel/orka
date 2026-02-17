"""Module integration consistency test for ORKA.

Builds all ORKA modules, runs reasoning (HermiT by default), and checks
consistency.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from builder import OrkaBuilder
from graph_manager import reason_graph


class TestOrkaModulesConsistency(unittest.TestCase):
    """Validate that the composed ORKA ontology remains consistent."""

    def test_all_modules_consistent_with_reasoning(self) -> None:
        builder = OrkaBuilder()
        ontology = builder.build(
            modules=["core", "ros", "sensors", "characteristics", "measurements"],
            align_oboe=True,
            align_ssn=True,
        )

        imported_iris = {imported.base_iri for imported in ontology.imported_ontologies}
        self.assertTrue(
            any("www.w3.org/ns/ssn/" in iri for iri in imported_iris),
            "Expected SSN import to be present.",
        )
        self.assertTrue(
            any("www.w3.org/ns/sosa/" in iri for iri in imported_iris),
            "Expected SOSA import to be present.",
        )

        result = reason_graph(
            ontology,
            reasoner="hermit",
            infer_property_values=True,
            save_path=Path("owl/orka-all-modules-inferred.owl"),
        )

        self.assertTrue(result["consistent"], "Ontology is inconsistent after reasoning")
        self.assertEqual(result["reasoner"], "hermit")
        self.assertIsNotNone(result["saved_to"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
