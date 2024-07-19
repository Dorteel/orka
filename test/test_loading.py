import rdflib
import owlready2

# Step 1: Load RDF Graph using RDFLib
file_path = r"c:\Users\dorte\Documents\Repositories\ontologies\orka\owl\orka-combined.owl"  # Replace with the actual path to your file
graph = rdflib.Graph()
graph.parse(file_path)

print("RDFLib Graph loaded successfully")

# Step 2: Create an Empty Ontology in Owlready2
onto_world = owlready2.World()
onto = onto_world.get_ontology("http://example.org/converted_ontology.owl")

# Step 3: Add Triples to Owlready2 Ontology
rdf_graph = onto_world.as_rdflib_graph()
with onto:
    for s, p, o in graph:
        rdf_graph.add((s, p, o))

# Step 4: Save the Ontology
onto.save(file="orka.owl", format="rdfxml")

print("Ontology loaded into Owlready2 and saved successfully")

def print_classes(ontology):
    print("\nClasses in the ontology:")
    for cls in ontology.classes():
        print(cls)

def print_individuals(ontology):
    print("\nIndividuals in the ontology:")
    for ind in ontology.individuals():
        print(ind)

def print_relations(ontology):
    print("\nObject Properties in the ontology:")
    try:
        for prop in ontology.object_properties():
            for s, o in prop.get_relations():
                print(f"{s} {prop} {o}")
    except Exception as e:
        print(f"Error accessing object properties: {e}")

    print("\nData Properties in the ontology:")
    try:
        for prop in ontology.data_properties():
            for s, o in prop.get_relations():
                print(f"{s} {prop} {o}")
    except Exception as e:
        print(f"Error accessing data properties: {e}")

# Print the state of the ontology before reasoning
# print("Before reasoning:")
# print_classes(onto)
# print_individuals(onto)
# print_relations(onto)

with onto:
    owlready2.sync_reasoner()   

onto.save(file="orka-inferred.owl", format="rdfxml")
# print("After reasoning:")
# print_classes(onto)
# print_individuals(onto)
# print_relations(onto)