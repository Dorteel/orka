from rdflib import Graph, Literal, RDF, URIRef, Namespace
oro = Graph().parse("http://kb.openrobots.org/", format='xml')
print(oro.serialize(format="turtle"))