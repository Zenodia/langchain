"""Utilities to init Vertex AI."""
import requests
import json

def fetch_collection_id(collection_name, pipeline, endpoint_url):    
    """implement curl to request """
    headers = {
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
    }

    json_data = {
        'name': collection_name,
        'pipeline': pipeline,
    }

    response = requests.post(endpoint_url, headers=headers, json=json_data)
    d=response.text
    outd=json.loads(d)
    return outd['collection']['id']  
