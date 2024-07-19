import os
from owlready2 import *

# Ensure the correct path to the ontology file
file_path = r"c:\Users\dorte\Documents\Repositories\ontologies\orka\owl\orka-combined.owl"  # Replace with the actual path to your file

# Check if the file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file {file_path} does not exist. Please check the path.")


def print_triples(onto):
    # Iterate over all individuals in the ontology
    for s in onto.individuals():
        for p in s.get_properties():
            for o in s.get_pvalues(p):
                print(f"Subject: {s}")
                print(f"Predicate: {p}")
                print(f"Object: {o}")
                print('-' * 20)

# Load the ontology
try:
    onto = get_ontology(file_path).load(format="rdfxml")  # Specify the format explicitly
    print("Ontology loaded successfully.")
except OwlReadyOntologyParsingError as e:
    print(f"An ontology parsing error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


graph = default_world.as_rdflib_graph() 

print_triples(onto)
# print(list(onto.classes()))
owlready2.sync_reasoner()
