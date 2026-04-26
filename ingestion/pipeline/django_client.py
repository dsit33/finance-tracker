import os
import requests

DJANGO_BASE_URL = os.environ.get('DJANGO_BASE_URL', 'http://django:8000')
INTERNAL_API_KEY = os.environ['INTERNAL_API_KEY']

def _headers():
    return {'X-Internal-Key': INTERNAL_API_KEY}

def fetch_recent(account_id: int, days: int = 60) -> list[dict]:
    url = f'{DJANGO_BASE_URL}/api/internal/accounts/{account_id}/transactions/recent/'
    response = requests.get(url, params={'days': days}, headers=_headers(), timeout=10)
    response.raise_for_status()
    return response.json()

def post_bulk(rows: list[dict]) -> dict:
    url = f'{DJANGO_BASE_URL}/api/internal/transactions/bulk/'
    response = requests.post(url, json=rows, headers=_headers(), timeout=30)
    response.raise_for_status()
    return response.json()