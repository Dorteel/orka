from __future__ import annotations

import sys
from pathlib import Path
from urllib.request import Request, urlopen

from rdflib import Graph
from owlready2 import get_ontology, PREDEFINED_ONTOLOGIES
from ontology_building.orka_core import OrkaCore

DEFAULT_OUTPUT = Path(__file__).resolve().with_name("orka-foundational-alignments.owl")
CACHE_DIR = Path(__file__).resolve().with_name("external")

DEFAULT_SSN_IRI = "https://www.w3.org/ns/ssn/"
DEFAULT_SOSA_IRI = "https://www.w3.org/ns/sosa/"

SSN_DOWNLOAD_URL = "https://raw.githubusercontent.com/w3c/sdw/gh-pages/ssn/integrated/ssn.ttl"
SOSA_DOWNLOAD_URL = "https://raw.githubusercontent.com/w3c/sdw/gh-pages/ssn/integrated/sosa.ttl"
OBOE_DOWNLOAD_URL = "https://raw.githubusercontent.com/NCEAS/oboe/master/oboe-core.owl"


class OrkaFoundationalAlignments(OrkaCore):
    """Extends ORKA core with foundational alignments to SSN, SOSA, and OBOE."""

    def __init__(
        self,
        base_iri: str = "https://w3id.org/def/orka#",
        ssn_iri: str = DEFAULT_SSN_IRI,
        sosa_iri: str = DEFAULT_SOSA_IRI,
    ):
        super().__init__(base_iri=base_iri)
        self.ssn_iri = ssn_iri
        self.sosa_iri = sosa_iri
        self.ssn = None
        self.sosa = None
        self.oboe = None

    def extend(self):
        self._load_external_ontologies()
        self._align_classes()
        self._align_properties()

    def _download_if_missing(self, url: str, filename: str) -> Path:
        """Download a file once and cache it locally."""
        CACHE_DIR.mkdir(exist_ok=True)
        path = CACHE_DIR / filename

        if not path.exists():
            req = Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "text/turtle, application/rdf+xml, application/xml;q=0.9, */*;q=0.8",
                },
            )
            with urlopen(req) as response, open(path, "wb") as f:
                f.write(response.read())

        return path

    def _convert_ttl_to_rdfxml(self, ttl_path: Path) -> Path:
        """Convert Turtle to RDF/XML because Owlready2 does not natively load Turtle well."""
        rdfxml_path = ttl_path.with_suffix(".owl")

        if rdfxml_path.exists():
            return rdfxml_path

        graph = Graph()
        graph.parse(str(ttl_path), format="turtle")
        graph.serialize(destination=str(rdfxml_path), format="xml")
        return rdfxml_path

    def _load_external_ontologies(self):
        """Load SSN, SOSA, and OBOE into Owlready2."""
        ssn_ttl_path = self._download_if_missing(SSN_DOWNLOAD_URL, "ssn.ttl")
        sosa_ttl_path = self._download_if_missing(SOSA_DOWNLOAD_URL, "sosa.ttl")
        oboe_path = self._download_if_missing(OBOE_DOWNLOAD_URL, "oboe-core.owl")

        ssn_rdfxml_path = self._convert_ttl_to_rdfxml(ssn_ttl_path)
        sosa_rdfxml_path = self._convert_ttl_to_rdfxml(sosa_ttl_path)

        # Map ontology IRIs to local cached files so owl:imports resolves locally.
        PREDEFINED_ONTOLOGIES["https://www.w3.org/ns/sosa/"] = str(sosa_rdfxml_path)
        PREDEFINED_ONTOLOGIES["http://www.w3.org/ns/sosa/"] = str(sosa_rdfxml_path)
        PREDEFINED_ONTOLOGIES["https://www.w3.org/ns/ssn/"] = str(ssn_rdfxml_path)
        PREDEFINED_ONTOLOGIES["http://www.w3.org/ns/ssn/"] = str(ssn_rdfxml_path)

        self.sosa = get_ontology(self.sosa_iri).load()
        self.ssn = get_ontology(self.ssn_iri).load()
        self.oboe = get_ontology(oboe_path.as_uri()).load()

    def _align_classes(self):
        onto = self.onto
        ssn = self.ssn
        sosa = self.sosa
        oboe = self.oboe

        # OBOE-style alignments
        onto.Entity.equivalent_to.append(oboe.Entity)
        onto.Observation.equivalent_to.append(oboe.Observation)
        onto.Measurement.equivalent_to.append(oboe.Measurement)
        onto.Characteristic.equivalent_to.append(oboe.Characteristic)
        onto.Standard.equivalent_to.append(oboe.Standard)

        # SSN/SOSA-style alignments
        onto.Procedure.equivalent_to.append(sosa.Procedure)
        onto.Result.equivalent_to.append(sosa.Result)
        onto.Sensor.equivalent_to.append(sosa.Sensor)
        onto.Platform.equivalent_to.append(sosa.Platform)
        onto.System.equivalent_to.append(ssn.System)

        # ORKA-specific specializations
        onto.Robot.is_a.append(onto.Platform)
        onto.ComputerVisionAlgorithm.is_a.append(onto.Procedure)
        onto.LocalisationProcedure.is_a.append(onto.Procedure)
        onto.PositionSensor.is_a.append(onto.Sensor)
        onto.HeadingSensor.is_a.append(onto.Sensor)
        onto.ProprioceptorSensor.is_a.append(onto.Sensor)

    def _align_properties(self):
        onto = self.onto
        sosa = self.sosa
        oboe = self.oboe

        onto.hasMeasurement.equivalent_to.append(oboe.hasMeasurement)
        onto.ofEntity.equivalent_to.append(oboe.ofEntity)
        onto.ofCharacteristic.equivalent_to.append(oboe.ofCharacteristic)

        # Keep only if your core defines it with this exact name.
        if hasattr(onto, "measuresUsingStandard") and hasattr(oboe, "measuresUsingStandard"):
            onto.measuresUsingStandard.equivalent_to.append(oboe.measuresUsingStandard)

        onto.observesCharacteristic.is_a.append(sosa.observes)

    def save(self, output_path: str | Path = DEFAULT_OUTPUT):
        output_path = Path(output_path).resolve()
        self.build()

        for imported in (self.ssn, self.sosa, self.oboe):
            if imported and imported not in self.onto.imported_ontologies:
                self.onto.imported_ontologies.append(imported)

        self.onto.save(file=str(output_path), format="rdfxml")
        return output_path


def main():
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    builder = OrkaFoundationalAlignments()
    saved_path = builder.save(output_path)
    print(f"Saved ORKA foundational alignment ontology to: {saved_path}")


if __name__ == "__main__":
    main()