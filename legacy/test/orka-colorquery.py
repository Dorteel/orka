import requests
import owlready2

# Load existing ontology
ontology = owlready2.get_ontology("/home/user/pel_ws/src/orvis/orka/orvis_demo.owl").load()

# SPARQL query to get color data with subclass relationships
query = """
SELECT ?color ?colorLabel ?hex ?parent WHERE {
  ?color (wdt:P279|wdt:P31) wd:Q1075.
  ?color wdt:P465 ?hex.
  ?color rdfs:label ?colorLabel.
  OPTIONAL { ?color wdt:P279 ?parent. }
  FILTER(LANG(?colorLabel) = "en")
}
"""

# Fetch data from Wikidata
url = "https://query.wikidata.org/sparql"
headers = {"User-Agent": "WikidataColorAddition/1.0"}
response = requests.get(url, headers=headers, params={"format": "json", "query": query})

try:
    data = response.json()["results"]["bindings"]
except requests.exceptions.JSONDecodeError:
    print("Error: Failed to parse JSON response")
    print(response.text)
    exit()

# Retrieve Color class from ontology
with ontology:
    if not hasattr(ontology, "Color"):
        class Color(owlready2.Thing):
            pass
    else:
        Color = ontology.Color
    
    color_dict = {}
    
    # First pass: create all color classes
    for item in data:
        color_name = item["colorLabel"]["value"]
        hex_value = item["hex"]["value"]
        color_id = item["color"]["value"].split("/")[-1]
        parent_id = item["parent"]["value"].split("/")[-1] if "parent" in item else None
        
        # Exclude colors with names starting with '#' or containing spaces
        if color_name.startswith("#") or " " in color_name:
            continue
        
        # Create color subclass but don't assign parent yet
        color_class = type(color_id, (Color,), {})
        color_dict[color_id] = color_class
        
        # Assign attributes
        color_class.label = [color_name.capitalize()]
        color_class.hasRGBvalue = [hex_value]
        color_class.hasWikiDataURI = [f"https://www.wikidata.org/wiki/{color_id}"]
    
    # Second pass: assign correct parent relationships
    for item in data:
        color_id = item["color"]["value"].split("/")[-1]
        parent_id = item["parent"]["value"].split("/")[-1] if "parent" in item else None
        
        if color_id in color_dict:
            color_class = color_dict[color_id]
            
            # Assign parent if it exists, otherwise default to Color
            if parent_id and parent_id in color_dict:
                color_class.is_a.append(color_dict[parent_id])
                # Remove direct subclass relationship to Color
                if Color in color_class.is_a:
                    color_class.is_a.remove(Color)
            else:
                color_class.is_a.append(Color)

# Save updated ontology
ontology.save("updated_ontology.owl")
print("Ontology updated and saved as updated_ontology.owl")