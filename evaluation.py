import rdflib

# Path to your ontology file
ontology_path = 'owl/orka-core.owl'

# Create a Graph
g = rdflib.Graph()

# Parse the ontology file
g.parse(ontology_path, format=rdflib.util.guess_format(ontology_path))

# Print out all triples in the ontology
for subj, pred, obj in g:
    print(f"Subject: {subj}\tPredicate: {pred}\tObject: {obj}")

# Example: Querying the ontology using SPARQL
query = """
SELECT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object
}
LIMIT 10
"""

# Execute the SPARQL query
for row in g.query(query):
    print(f"Row: {row}")

# List all namespaces with their prefixes
print("Existing namespaces and prefixes:")
for prefix, namespace in g.namespace_manager.namespaces():
    print(f"{prefix}: {namespace}")

for subj, pred, obj in g:
    print(f"{subj.n3(g.namespace_manager)} {pred.n3(g.namespace_manager)} {obj.n3(g.namespace_manager)}")