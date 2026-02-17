"""Build a full ORKA ontology (all modules, no alignments)."""

from __future__ import annotations

import argparse

from builder import DEFAULT_BASE_IRI, OrkaBuilder


def main() -> None:
    modules = ["core", "ros", "sensors", "characteristics", "measurements"]
    default_output = f"owl/orka-{'-'.join(modules)}.owl"

    parser = argparse.ArgumentParser(
        description="Build full ORKA modules without external alignments."
    )
    parser.add_argument(
        "--output",
        default=default_output,
        help="Output OWL file path.",
    )
    args = parser.parse_args()

    builder = OrkaBuilder(base_iri=DEFAULT_BASE_IRI)
    output_path = builder.build_and_save(
        modules=modules,
        output_path=args.output,
        align_oboe=False,
        align_ssn=False,
    )
    print(f"Saved ontology to: {output_path}")


if __name__ == "__main__":
    main()
