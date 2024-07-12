from SPARQLWrapper import SPARQLWrapper, JSON
import networkx as nx
import matplotlib.pyplot as plt
import rdflib
from rdflib.namespace import Namespace

color_graph = rdflib.Graph()
orka_full = Namespace("http://www.semanticweb.org/dorte/orka-full#")


# Set up the SPARQL endpoint
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setQuery("""
    SELECT ?color ?colorLabel ?colorValue ?superclass ?superclassLabel
    WHERE {
      ?color wdt:P31 wd:Q1075;  # Instance of color
             wdt:P465 ?colorValue.  # Color value property

      OPTIONAL {
        ?color wdt:P279 ?superclass.  # Superclass property
        FILTER(EXISTS { ?superclass wdt:P31 wd:Q1075 }).  # Filter to only include superclasses that are colors
      }

      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    LIMIT 100
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()
# Create a directed graph using networkx
G = nx.DiGraph()
color_graphs = {}
color_dict = {}
# Add nodes and edges to the graph
for result in results["results"]["bindings"]:
    color = result["color"]["value"]
    color_label = result["colorLabel"]["value"].replace(' ', '_')
    color_value = result["colorValue"]["value"]
    superclass = result.get("superclass", {}).get("value", None)
    superclass_label = result.get("superclassLabel", {}).get("value", None)
    R,G,B = [color_value[0:2], color_value[2:4],color_value[4:6]]
    color_code = [int(x,16) for x in [R,G,B]]
    color_graph.add((orka_full[color_label], orka_full["hasValue"], rdflib.Literal(color_value)))
    color_dict[color_label] = color_code
    # G.add_node(color, label=f"{color_label}\n{color_value}", node_color='#fff4d9')
    
    # if superclass:
    #     G.add_node(superclass, label=f"{superclass_label}", node_color='#fff4d9')
    #     G.add_edge(color, superclass)  # Reverse the direction to correctly represent subclass relationship

# print(color_graphs)
# Draw the graph with labels
# pos = nx.spring_layout(G)
# labels = nx.get_node_attributes(G, 'label')

# nx.draw(G, pos, node_size=700, labels=labels, with_labels=True, font_size=8, font_color='black', font_weight='bold', node_color='skyblue', edge_color='gray', linewidths=0.5, arrowsize=10)

# plt.axis('off')
# plt.show()

for s,p,o in color_graph:
    print(s, p, o)


import numpy as np

print(list(color_dict.values()))
list_of_colors = [[255,0,0],[150,33,77],[75,99,23],[45,88,250],[250,0,255]]
color = [155,155,155]

# Example colours from the use-case
colours = [[201, 127, 34], [179, 96, 53], [190, 186, 76]]

def closest(colors,color):
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors-color)**2,axis=1))
    index_of_smallest = np.where(distances==np.amin(distances))
    smallest_distance = colors[index_of_smallest]
    return smallest_distance 

def find_key_by_value(dictionary, target_value):
    for key, value in dictionary.items():
        if np.array_equal(value, target_value):
            return key
    return None

for color in colours:
  closest_color = closest(list(color_dict.values()), color)
  print(color, closest_color[0], find_key_by_value(color_dict, closest_color[0]))