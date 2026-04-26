from io import BytesIO
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / 'fixtures'
DJANGO_RECENT_URL = 'http://django:8000/api/internal/accounts/42/transactions/recent/'
DJANGO_BULK_URL = 'http://django:8000/api/internal/transactions/bulk/'

@pytest.fixture
def chase_csv():
    return (FIXTURES / 'chase_sample.csv').read_bytes()

def _multipart(csv_bytes, bank_id='chase', account_id='42'):
    return {
        'data': {
            'bank_id': bank_id,
            'account_id': account_id,
            'file': (BytesIO(csv_bytes), 'sample.csv'),
        },
        'content_type': 'multipart/form-data'
    }

def test_ingest_happy_path_chase(client, chase_csv, requests_mock):
    requests_mock.get(DJANGO_RECENT_URL, json=[])
    requests_mock.post(DJANGO_BULK_URL, json={'created': 10, 'skipped': 0})
    
    response = client.post('/ingest/csv', **_multipart(chase_csv))

    assert response.status_code == 200
    assert response.json['created'] == 10

def test_ingest_invalid_bank_id_returns_400(client, chase_csv):
    response = client.post('/ingest/csv', **_multipart(chase_csv, bank_id='unknown'))
    assert response.status_code == 400

def test_ingest_missing_csv_returns_400(client):
    response = client.post('/ingest/csv', data={'bank_id': 'chase', 'account_id': '42'}, content_type='multipart/form-data')
    assert response.status_code == 400

def test_ingest_dedups_against_existing(client, chase_csv, requests_mock):
    existing = [
        {'date': '2026-04-01', 'amount': '-15.99', 'merchant': 'netflix.com'},
        {'date': '2026-05-01', 'amount': '-15.99', 'merchant': 'netflix.com'},
    ]

    requests_mock.get(DJANGO_RECENT_URL, json=existing)
    requests_mock.post(DJANGO_BULK_URL, json={'created': 8, 'skipped': 0})

    response = client.post('/ingest/csv', **_multipart(chase_csv))

    assert response.status_code == 200
    assert response.json['deduped'] == 2

def test_ingest_forwards_only_non_duplicates(client, chase_csv, requests_mock):
    existing = [{'date': '2026-04-01', 'amount': '-15.99', 'merchant': 'netflix.com'}]
    requests_mock.get(DJANGO_RECENT_URL, json=existing)
    bulk_mock = requests_mock.post(DJANGO_BULK_URL, json={'created': 9, 'skipped': 0})

    client.post('/ingest/csv', **_multipart(chase_csv))

    posted = bulk_mock.last_request.json()
    merchants = [row['merchant'] for row in posted]
    assert 'netflix.com' not in merchants or merchants.count('netflix.com') < 3