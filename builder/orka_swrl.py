"""SWRL rule utilities for ORKA builds."""

from __future__ import annotations

from pathlib import Path

from owlready2 import get_ontology

DEFAULT_LEGACY_OWL_PATH = Path("legacy/owl/orka.owl")
DEFAULT_SWRL_RULES_PATH = Path("swrl/orka_legacy_swrl.owl")


def update_swrl_rules_file(
    source_owl_path: str | Path = DEFAULT_LEGACY_OWL_PATH,
    output_path: str | Path = DEFAULT_SWRL_RULES_PATH,
) -> Path:
    """Extract legacy SWRL rules from ORKA OWL into a dedicated SWRL file."""
    source = Path(source_owl_path)
    if not source.exists():
        raise FileNotFoundError(f"Legacy OWL not found: {source}")

    text = source.read_text()
    start = text.find(
        """<!-- 
    ///////////////////////////////////////////////////////////////////////////////////////
    //
    // Rules"""
    )
    if start == -1:
        raise ValueError(f"Rules section not found in: {source}")

    end = text.rfind("</rdf:RDF>")
    if end == -1 or end <= start:
        raise ValueError(f"Could not locate RDF end tag in: {source}")

    raw_rules_section = text[start:end]
    rule_count = raw_rules_section.count(
        '<rdf:type rdf:resource="http://www.w3.org/2003/11/swrl#Imp"/>'
    )
    if rule_count == 0:
        raise ValueError(f"No SWRL rule blocks found in: {source}")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    header = """<?xml version=\"1.0\"?>
<rdf:RDF xmlns=\"https://w3id.org/def/orka/swrl#\"
     xml:base=\"https://w3id.org/def/orka/swrl\"
     xmlns:owl=\"http://www.w3.org/2002/07/owl#\"
     xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"
     xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\"
     xmlns:xml=\"http://www.w3.org/XML/1998/namespace\"
     xmlns:xsd=\"http://www.w3.org/2001/XMLSchema#\"
     xmlns:swrl=\"http://www.w3.org/2003/11/swrl#\"
     xmlns:swrla=\"http://swrl.stanford.edu/ontologies/3.3/swrla.owl#\">
    <owl:Ontology rdf:about=\"https://w3id.org/def/orka/swrl\">
        <owl:imports rdf:resource=\"https://w3id.org/def/orka#\"/>
    </owl:Ontology>
"""
    footer = "\n</rdf:RDF>\n"
    body = raw_rules_section

    output.write_text(header + "\n" + body + footer)
    return output


def apply_swrl_rules(
    onto,
    rules_path: str | Path = DEFAULT_SWRL_RULES_PATH,
    *,
    update_from_legacy: bool = False,
    source_owl_path: str | Path = DEFAULT_LEGACY_OWL_PATH,
):
    """Import SWRL rules ontology into the given ORKA ontology."""
    rules_file = Path(rules_path)

    if update_from_legacy or not rules_file.exists():
        rules_file = update_swrl_rules_file(
            source_owl_path=source_owl_path,
            output_path=rules_file,
        )

    swrl_onto = get_ontology(rules_file.resolve().as_uri()).load()
    if swrl_onto not in onto.imported_ontologies:
        onto.imported_ontologies.append(swrl_onto)

    return swrl_onto
