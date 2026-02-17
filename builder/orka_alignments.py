"""External ontology alignments for ORKA.

Alignments are intentionally separated from the ORKA-native core so the project
can define its own conceptualization while still mapping to OBOE and SSN/SOSA.
"""

from __future__ import annotations

import io
from urllib.request import Request, urlopen

from owlready2 import ObjectProperty, Thing, get_ontology

OBOE_CORE_DOC_IRI = "http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl"
OBOE_CORE_NS_IRI = "http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl#"
OBOE_IRI = "http://ecoinformatics.org/oboe/oboe.1.2/oboe.owl"
OBOE_CHARACTERISTICS_IRI = "http://ecoinformatics.org/oboe/oboe.1.2/oboe-characteristics.owl"
OBOE_STANDARDS_IRI = "http://ecoinformatics.org/oboe/oboe.1.2/oboe-standards.owl"
SSN_IRI = "https://www.w3.org/ns/ssn/"
SOSA_IRI = "https://www.w3.org/ns/sosa/"
SSN_SYSTEMS_IRI = "https://www.w3.org/ns/ssn/systems/"


def _append_equivalent(target, candidate) -> None:
    """Append an equivalent axiom once."""
    if candidate not in target.equivalent_to:
        target.equivalent_to.append(candidate)


def _append_import(onto, imported_ontology) -> None:
    """Append imported ontology once."""
    if imported_ontology not in onto.imported_ontologies:
        onto.imported_ontologies.append(imported_ontology)


def _candidate_web_iris(iri: str) -> tuple[str, ...]:
    """Return candidate web URLs for known ontology namespaces."""
    if iri == SOSA_IRI:
        return (
            SOSA_IRI,
            "https://www.w3.org/ns/sosa/sosa.ttl",
            "https://www.w3.org/ns/sosa/sosa.rdf",
        )
    if iri == SSN_IRI:
        return (
            SSN_IRI,
            "https://www.w3.org/ns/ssn/ssn.ttl",
            "https://www.w3.org/ns/ssn/ssn.rdf",
        )
    if iri == SSN_SYSTEMS_IRI:
        return (
            SSN_SYSTEMS_IRI,
            "https://www.w3.org/ns/ssn/systems",
            "https://www.w3.org/ns/ssn/systems.owl",
            "https://www.w3.org/ns/ssn/systems.ttl",
            "https://www.w3.org/ns/ssn/systems.rdf",
            "https://www.w3.org/ns/ssn/systems/ssn-system.ttl",
            "https://www.w3.org/ns/ssn/systems/ssn-system.rdf",
        )
    return (iri,)


def _candidate_web_sources(iri: str) -> tuple[tuple[str, str, str], ...]:
    """Return (url, parser_format, accept_header) candidates."""
    if iri == SOSA_IRI:
        return (
            ("https://www.w3.org/ns/sosa/sosa.rdf", "rdfxml", "application/rdf+xml"),
            ("https://www.w3.org/ns/sosa/sosa.ttl", "turtle", "text/turtle"),
            (SOSA_IRI, "rdfxml", "application/rdf+xml"),
            (SOSA_IRI, "turtle", "text/turtle"),
        )
    if iri == SSN_IRI:
        return (
            ("https://www.w3.org/ns/ssn/ssn.rdf", "rdfxml", "application/rdf+xml"),
            ("https://www.w3.org/ns/ssn/ssn.ttl", "turtle", "text/turtle"),
            (SSN_IRI, "rdfxml", "application/rdf+xml"),
            (SSN_IRI, "turtle", "text/turtle"),
        )
    if iri == SSN_SYSTEMS_IRI:
        return (
            (
                "https://www.w3.org/ns/ssn/systems/ssn-system.rdf",
                "rdfxml",
                "application/rdf+xml",
            ),
            (
                "https://www.w3.org/ns/ssn/systems/ssn-system.ttl",
                "turtle",
                "text/turtle",
            ),
            ("https://www.w3.org/ns/ssn/systems.owl", "rdfxml", "application/rdf+xml"),
        )
    return ((iri, "rdfxml", "application/rdf+xml"),)


def _fetch_web_bytes(url: str, accept: str) -> bytes:
    """Fetch bytes from URL using explicit Accept header."""
    request = Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": "orka-alignments/1.0",
        },
    )
    with urlopen(request, timeout=20) as response:
        return response.read()


def _looks_like_html(payload: bytes) -> bool:
    """Detect HTML payloads that Owlready2 cannot parse as ontology files."""
    head = payload[:512].lower().lstrip()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html")


def _load_ontology_from_web(iri: str):
    """Load ontology from the ontology IRI over the web.

    Raises:
        RuntimeError: If ontology cannot be loaded from the provided IRI.
    """
    last_exc = None
    for candidate, fmt, accept in _candidate_web_sources(iri):
        try:
            payload = _fetch_web_bytes(candidate, accept=accept)
            if _looks_like_html(payload):
                continue
            return get_ontology(candidate).load(
                fileobj=io.BytesIO(payload),
                format=fmt,
            )
        except Exception as exc:  # pragma: no cover - depends on network/runtime
            last_exc = exc

    raise RuntimeError(f"Failed to load ontology from web IRI: {iri}") from last_exc


def _try_append_import(onto, iri: str, required: bool) -> None:
    """Try importing ontology by IRI; optionally fail hard."""
    try:
        imported = _load_ontology_from_web(iri)
        _append_import(onto, imported)
    except RuntimeError:
        if required:
            raise


def _ensure_oboe_core_terms():
    """Load OBOE core terms; fallback to minimal stubs only if absent after import."""
    oboe_core = _load_ontology_from_web(OBOE_CORE_DOC_IRI)

    # Some environments bind the namespace ontology separately.
    ns_ontology = get_ontology(OBOE_CORE_NS_IRI)
    if ns_ontology.Entity is not None:
        oboe_core = ns_ontology

    if oboe_core.Entity is not None:
        return oboe_core

    # Last-resort stubs if the ontology loads but expected entities are missing.
    with oboe_core:
        class Entity(Thing):
            pass

        class Observation(Thing):
            pass

        class Measurement(Thing):
            pass

        class Characteristic(Thing):
            pass

        class IdentifyingCharacteristic(Thing):
            pass

        class Standard(Thing):
            pass

        class hasMeasurement(ObjectProperty):
            pass

        class ofEntity(ObjectProperty):
            pass

        class ofCharacteristic(ObjectProperty):
            pass

        class hasValue(ObjectProperty):
            pass

        class usesStandard(ObjectProperty):
            pass

        class characteristicFor(ObjectProperty):
            pass

    return oboe_core


def _ensure_ssn_sosa_terms():
    """Load SSN/SOSA terms; fallback to minimal stubs only if absent after import."""
    sosa = _load_ontology_from_web(SOSA_IRI)
    ssn = _load_ontology_from_web(SSN_IRI)

    if sosa.Sensor is None:
        with sosa:
            class Observation(Thing):
                pass

            class Procedure(Thing):
                pass

            class Result(Thing):
                pass

            class Sensor(Thing):
                pass

            class Platform(Thing):
                pass

            class ObservableProperty(Thing):
                pass

            class hasResult(ObjectProperty):
                pass

            class madeBySensor(ObjectProperty):
                pass

            class usedProcedure(ObjectProperty):
                pass

            class observes(ObjectProperty):
                pass

            class observedProperty(ObjectProperty):
                pass

    if ssn.System is None:
        with ssn:
            class System(Thing):
                pass

            class implementedBy(ObjectProperty):
                pass

    return ssn, sosa


def define_oboe_alignments(onto) -> None:
    """Align ORKA core entities/properties with OBOE terms and import OBOE ontologies."""
    _append_import(onto, _load_ontology_from_web(OBOE_IRI))
    _append_import(onto, _load_ontology_from_web(OBOE_CHARACTERISTICS_IRI))
    _append_import(onto, _load_ontology_from_web(OBOE_STANDARDS_IRI))

    oboe = _ensure_oboe_core_terms()
    _append_import(onto, oboe)

    _append_equivalent(onto.Entity, oboe.Entity)
    _append_equivalent(onto.Observation, oboe.Observation)
    _append_equivalent(onto.Measurement, oboe.Measurement)
    _append_equivalent(onto.Characteristic, oboe.Characteristic)
    _append_equivalent(onto.MeasurementStandard, oboe.Standard)

    _append_equivalent(onto.hasMeasurement, oboe.hasMeasurement)
    _append_equivalent(onto.ofEntity, oboe.ofEntity)
    _append_equivalent(onto.ofCharacteristic, oboe.ofCharacteristic)
    _append_equivalent(onto.hasResult, oboe.hasValue)
    _append_equivalent(onto.measuresUsingStandard, oboe.usesStandard)
    _append_equivalent(onto.characteristicFor, oboe.characteristicFor)

    if onto.ActivityType is not None:
        _append_equivalent(onto.ActivityType, oboe.IdentifyingCharacteristic)
    if onto.ObjectType is not None:
        _append_equivalent(onto.ObjectType, oboe.IdentifyingCharacteristic)


def define_ssn_alignments(onto) -> None:
    """Align ORKA core entities/properties with SSN/SOSA terms and import ontologies."""
    _try_append_import(onto, SOSA_IRI, required=True)
    _try_append_import(onto, SSN_IRI, required=True)
    # systems namespace endpoint is inconsistent across environments; non-fatal.
    _try_append_import(onto, SSN_SYSTEMS_IRI, required=False)

    ssn, sosa = _ensure_ssn_sosa_terms()
    _append_import(onto, sosa)
    _append_import(onto, ssn)

    _append_equivalent(onto.Observation, sosa.Observation)
    _append_equivalent(onto.Procedure, sosa.Procedure)
    _append_equivalent(onto.Result, sosa.Result)
    _append_equivalent(onto.Sensor, sosa.Sensor)
    _append_equivalent(onto.Platform, sosa.Platform)
    _append_equivalent(onto.System, ssn.System)

    _append_equivalent(onto.hasResult, sosa.hasResult)
    _append_equivalent(onto.madeBySensor, sosa.madeBySensor)
    _append_equivalent(onto.usedProcedure, sosa.usedProcedure)
    _append_equivalent(onto.observesCharacteristic, sosa.observes)
    _append_equivalent(onto.ofCharacteristic, sosa.observedProperty)
    _append_equivalent(onto.implementedOn, ssn.implementedBy)

    if onto.EnvironmentProperty is not None:
        _append_equivalent(onto.EnvironmentProperty, sosa.ObservableProperty)
    if onto.ObjectProperty is not None:
        _append_equivalent(onto.ObjectProperty, sosa.ObservableProperty)
