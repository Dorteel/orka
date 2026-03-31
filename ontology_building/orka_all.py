from __future__ import annotations

import sys
from pathlib import Path

from ontology_building.orka_core import OrkaCore
from ontology_building.orka_alignments import OrkaFoundationalAlignments
from ontology_building.orka_conceptualspaces import OrkaConceptualSpaces
from ontology_building.orka_full import OrkaFull
from ontology_building.orka_emotions import OrkaEmotions
from ontology_building.orka_ros import OrkaROS

DEFAULT_OUTPUT = Path(__file__).resolve().with_name("orka-all.owl")


class OrkaAll(OrkaFoundationalAlignments):
    """Composes all ORKA extensions into one ontology."""

    def extend(self):
        super().extend()
        OrkaConceptualSpaces.extend(self)
        OrkaFull.extend(self)
        OrkaEmotions.extend(self)
        OrkaROS.extend(self)


def main():
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    builder = OrkaAll()
    saved_path = builder.save(output_path)
    print(f"Saved ORKA all ontology to: {saved_path}")


if __name__ == "__main__":
    main()