import requests

# Define the SPARQL query
query = """
SELECT ?entity ?entityLabel WHERE {
  { ?entity wdt:P279* wd:Q107649491. }
  UNION
  { ?instance wdt:P31* ?subclass.
  ?subclass wdt:P279* wd:Q107649491.
  BIND(?instance AS ?entity) }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

# Specify the URL of the Wikidata Query Service
url = 'https://query.wikidata.org/sparql'

# Set the headers to accept JSON format
headers = {
    'Accept': 'application/sparql-results+json'
}

# Send the request
response = requests.get(url, headers=headers, params={'query': query, 'format': 'json'})

# Check if the request was successful
if response.ok:
    data = response.json()
    entities = [(result['entity']['value'], result['entityLabel']['value'])
                for result in data['results']['bindings']]
    for entity in entities:
        print(f"Entity: {entity[0]}, Label: {entity[1]}")
else:
    print("Failed to fetch data")
