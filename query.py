import requests, time

def query_wikidata(property_id):
    # SPARQL query to get instances and subclasses of the given property
    sparql_query = """
    SELECT ?item ?itemLabel WHERE {
      { ?item wdt:P31* wd:""" + property_id + """ . }
      UNION
      { ?item wdt:P1647 wd:""" + property_id + """ . }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    LIMIT 200
    """

    url = 'https://query.wikidata.org/sparql'
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    params = {'query': sparql_query, 'format': 'json'}
    max_retries = 5

    for attempt in range(max_retries):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json()['results']['bindings']
            for result in results:
                print("Label:\t{}\t\tURI:\t{}".format(result['itemLabel']['value'], result['item']['value']))
        else:
            print("Failed to retrieve data: {}".format(response.status_code))
            wait = 2 ** attempt  # Exponential backoff
            time.sleep(wait)
    return None  # or raise an exception
    



# Example usage: Query for instances and subclasses of Q5 (human)
property_id = "Q1075"  # Replace Q5 with the Wikidata ID of your property
query_wikidata(property_id)
