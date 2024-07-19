import rdflib
import owlready2

# Define the file path of the Turtle file
file_path = r"c:\Users\dorte\Documents\Repositories\ontologies\orka\owl\orka-combined.owl"  # Replace with the actual path to your file

# Load the RDF graph using RDFLib
graph = rdflib.Graph()
graph.parse(file_path, format="turtle")

print("RDFLib Graph loaded successfully")

# Create a new empty ontology in Owlready2
onto_world = owlready2.World()
onto = onto_world.get_ontology("http://example.org/converted_ontology.owl")

# Manually add triples from RDFLib graph to Owlready2 ontology
for s, p, o in graph:
    if isinstance(s, rdflib.URIRef) and isinstance(p, rdflib.URIRef):
        s_iri = owlready2.IRI(str(s))
        p_iri = owlready2.IRI(str(p))
        if isinstance(o, rdflib.URIRef):
            o_iri = owlready2.IRI(str(o))
            onto_world.add_triple(s_iri, p_iri, o_iri)
        else:
            o_literal = str(o)
            onto_world.add_triple(s_iri, p_iri, o_literal)

# Save the ontology
onto.save(file="converted_ontology.owl", format="rdfxml")

print("Ontology loaded into Owlready2 and saved successfully")
