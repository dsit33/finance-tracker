from pathlib import Path

import requests
import os              

DJANGO_BASE = os.environ.get('DJANGO_BASE', 'http://localhost:8000')
FLASK_BASE = os.environ.get('FLASK_BASE', 'http://localhost:5001')

FIXTURES = Path(__file__).parent / 'fixtures'

def test_full_csv_to_analytics_flow(auth_token):
    headers = {'Authorization': f'Token {auth_token}'}

    account_resp = requests.post(
        f'{DJANGO_BASE}/api/accounts/',
        json={'name': 'e2e-checking', 'acc_type': 'checking'},
        headers=headers,
    )

    assert account_resp.status_code == 201
    account_id = account_resp.json()['id']

    with open(FIXTURES / 'full_flow.csv', 'rb') as f:
        ingest_resp = requests.post(
            f'{FLASK_BASE}/ingest/csv',
            data={'bank_id': 'chase', 'account_id': str(account_id)},
            files={'file': ('full_flow.csv', f, 'text/csv')},
        )

    assert ingest_resp.status_code == 200
    assert ingest_resp.json()['created'] >= 10

    recurring_resp = requests.get(
        f'{DJANGO_BASE}/api/analytics/accounts/{account_id}/recurring/',
        headers=headers,
    )

    assert recurring_resp.status_code == 200

    merchants_to_cadence = {r['merchant']: r['cadence'] for r in recurring_resp.json()}
    assert merchants_to_cadence.get('netflix.com') == 'monthly'
    assert merchants_to_cadence.get('spotify usa') == 'monthly'