"""Build a ROS + Sensors ORKA ontology."""

from __future__ import annotations

from builder import DEFAULT_BASE_IRI, OrkaBuilder


def main() -> None:
    builder = OrkaBuilder(base_iri=DEFAULT_BASE_IRI)
    output_path = builder.build_and_save(
        modules=["ros", "sensors"],
        output_path="owl/orka-ros-sensors.owl",
    )
    print(f"Saved ontology to: {output_path}")


if __name__ == "__main__":
    main()
