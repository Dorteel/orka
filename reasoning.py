import owlready2

# Define the path to the OWL file
owl_file_path = r"c:\Users\dorte\Documents\Repositories\ontologies\orka\owl\orka.owl"  # Replace with the actual path to your file

# Load the ontology
onto = owlready2.get_ontology(owl_file_path).load()

# Print some basic information about the ontology
print(f"Ontology {onto.name} loaded successfully!")
print(f"Number of classes in the ontology: {len(list(onto.classes()))}")
print(f"Number of object properties in the ontology: {len(list(onto.object_properties()))}")
print(f"Number of individuals in the ontology: {len(list(onto.individuals()))}")

# # Optionally, print the names of some classes, object properties, and individuals
# print("\nSome classes in the ontology:")
# for cls in list(onto.classes())[:10]:  # Print the first 10 classes
#     print(cls.name)

# print("\nSome object properties in the ontology:")
# for prop in list(onto.object_properties())[:10]:  # Print the first 10 object properties
#     print(prop.name)

# print("\nSome individuals in the ontology:")
# for ind in list(onto.individuals())[:10]:  # Print the first 10 individuals
#     print(ind.name)

with onto:
    # owlready2.sync_reasoner(infer_property_values = True, debug = 2)
    owlready2.sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True, debug = 1)   
    # print(onto.get_parents_of(onto.yaw_tb_01))
    onto.save(file="orka-inferred.owl", format="rdfxml")