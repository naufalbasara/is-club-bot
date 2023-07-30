import requests
import os

def get_stackoverflow_result(query):
    base_url = 'https://api.stackexchange.com/2.3/search'
    params = {
        'order': 'desc',
        'sort': 'relevance',
        'intitle': query,
        'site': 'stackoverflow',
        'key': os.getenv('STACK_OVERFLOW_API_KEY')
    }

    response = requests.get(base_url, params=params)
    return response.json()

