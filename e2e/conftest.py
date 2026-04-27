import os
import time

import pytest
import requests

DJANGO_BASE = os.environ.get('DJANGO_BASE', 'http://localhost:8000')
FLASK_BASE = os.environ.get('FLASK_BASE', 'http://localhost:5001')

def _wait_for(url: str, timeout: int = 30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if requests.get(url, timeout=2).status_code < 500:
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)
    raise RuntimeError(f'{url} not ready after {timeout}s')

@pytest.fixture(scope='session', autouse=True)
def services_up():
    _wait_for(f'{FLASK_BASE}/health')
    _wait_for(f'{DJANGO_BASE}/admin/login/')

@pytest.fixture
def auth_token():
    username = 'e2euser'
    password = 'e2etest-pass'

    response = requests.post(
        f'{DJANGO_BASE}/api/auth/token/',
        data={'username': username, 'password': password}
    )
    response.raise_for_status()

    return response.json()['token']