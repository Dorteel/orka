from __future__ import annotations

import sys
from pathlib import Path

from owlready2 import DataProperty, FunctionalProperty, ObjectProperty, Thing

from ontology_building.orka_core import OrkaCore

DEFAULT_OUTPUT = Path(__file__).resolve().with_name("orka-ros.owl")


class OrkaROS(OrkaCore):
    """Extends ORKA core with minimal ROS vocabulary."""

    def extend(self):
        onto = self.onto

        with onto:
            # -----------------------------------------------------------------
            # Core ROS classes
            # -----------------------------------------------------------------

            class ROSInterface(Thing):
                """A generic ROS communication interface."""

            class ROSTopic(ROSInterface):
                """A ROS topic used for publish/subscribe communication."""

            class ROSService(ROSInterface):
                """A ROS service used for request/response communication."""

            class ROSMessageType(Thing):
                """A ROS message or service type."""

            # -----------------------------------------------------------------
            # Object properties
            # -----------------------------------------------------------------

            class usesInterface(ObjectProperty):
                domain = [onto.System]
                range = [ROSInterface]

            class hasMessageType(ObjectProperty):
                domain = [ROSInterface]
                range = [ROSMessageType]

            # optional but handy from the start
            class publishesTo(ObjectProperty):
                domain = [onto.System]
                range = [ROSTopic]

            class subscribesTo(ObjectProperty):
                domain = [onto.System]
                range = [ROSTopic]

            class callsService(ObjectProperty):
                domain = [onto.System]
                range = [ROSService]

            class providesService(ObjectProperty):
                domain = [onto.System]
                range = [ROSService]

            # -----------------------------------------------------------------
            # Data properties
            # -----------------------------------------------------------------

            class hasROSName(DataProperty, FunctionalProperty):
                domain = [ROSInterface]
                range = [str]

            class hasROSPackage(DataProperty, FunctionalProperty):
                domain = [ROSMessageType]
                range = [str]

            class hasROSTypeName(DataProperty, FunctionalProperty):
                domain = [ROSMessageType]
                range = [str]


def main():
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    builder = OrkaROS()
    saved_path = builder.save(output_path)
    print(f"Saved ORKA ROS ontology to: {saved_path}")


if __name__ == "__main__":
    main()