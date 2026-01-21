from rdflib import Namespace

# TODO: set this to the real ORKA namespace (copy from the ontology)
ORKA = Namespace("http://example.org/orka#")

# You mint instances into your own namespace; keep it stable across projects.
EX = Namespace("http://example.org/orvis/")
