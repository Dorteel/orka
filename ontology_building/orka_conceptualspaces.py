from __future__ import annotations

import sys
from pathlib import Path

from owlready2 import DataProperty, FunctionalProperty, ObjectProperty, Thing

from ontology_building.orka_core import OrkaCore

DEFAULT_OUTPUT = Path(__file__).resolve().with_name("orka-conceptualspaces.owl")


class OrkaConceptualSpaces(OrkaCore):
    """Extends ORKA core with conceptual spaces vocabulary."""

    def extend(self):
        onto = self.onto

        with onto:
            class ConceptualSpace(Thing):
                """A conceptual space."""

            class Domain(Thing):
                """A domain in a conceptual space."""

            class Concept(Thing):
                """A concept represented in conceptual space."""

            class Instance(Thing):
                """An instance of a concept."""

            class ContrastClass(Thing):
                """A contrast class for contextual interpretation."""

            class Property(Thing):
                """A property represented in conceptual space."""

            class QualityDimension(Thing):
                """A quality dimension."""

            class ConvexRegion(Thing):
                """A convex region in conceptual space."""

            class MeasurementSystem(Thing):
                """A measurement system for a quality dimension."""

            class PrototypicalInstance(Instance):
                """A prototypical instance."""

            class SimilaritySensitivityParameter(Thing):
                """A parameter controlling similarity sensitivity."""

            class hasContext(ObjectProperty):
                domain = [ConceptualSpace]
                range = [onto.Context]

            class hasDomain(ObjectProperty):
                domain = [ConceptualSpace]
                range = [Domain]

            class hasConcept(ObjectProperty):
                domain = [ConceptualSpace]
                range = [Concept]

            class hasInstance(ObjectProperty):
                domain = [ConceptualSpace]
                range = [Instance]

            class hasContrastClass(ObjectProperty):
                domain = [ConceptualSpace]
                range = [ContrastClass]

            class hasSimParam(ObjectProperty):
                domain = [onto.Context]
                range = [SimilaritySensitivityParameter]

            class hasQualityDimension(ObjectProperty):
                domain = [Domain]
                range = [QualityDimension]

            class hasRegion(ObjectProperty):
                domain = [Property]
                range = [ConvexRegion]

            class correspondsTo(ObjectProperty):
                domain = [Concept]
                range = [Property]

            class hasPrototypicalInstance(ObjectProperty):
                domain = [Concept]
                range = [PrototypicalInstance]

            class hasMeasurementSystem(ObjectProperty):
                domain = [QualityDimension]
                range = [MeasurementSystem]

            class isCircular(DataProperty, FunctionalProperty):
                domain = [QualityDimension]
                range = [bool]

            class hasRangeMin(DataProperty, FunctionalProperty):
                domain = [QualityDimension]
                range = [float]

            class hasRangeMax(DataProperty, FunctionalProperty):
                domain = [QualityDimension]
                range = [float]

            class hasMeasurementLevel(DataProperty, FunctionalProperty):
                domain = [QualityDimension]
                range = [str]

            Property.is_a.append(ConvexRegion)


def main():
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    builder = OrkaConceptualSpaces()
    saved_path = builder.save(output_path)
    print(f"Saved ORKA conceptual spaces ontology to: {saved_path}")


if __name__ == "__main__":
    main()