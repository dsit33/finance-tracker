from datetime import date, timedelta
from decimal import Decimal

from django.urls import reverse
from rest_framework import status

from transactions.factories import TransactionFactory

def _seed_monthly(account, merchant: str, amount: Decimal, count: int = 5):
    start = date(2026, 1, 1)
    for i in range(count):
        TransactionFactory(
            account=account,
            date=start + timedelta(days=30 * i),
            amount=amount,
            merchant=merchant,
            raw_merchant=merchant.upper(),
        )

def test_recurring_requires_auth(api_client, account):
    url = reverse('analytics-recurring', kwargs={'account_id': account.pk})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_recurring_only_returns_users_accounts(authed_client, account2):
    url = reverse('analytics-recurring', kwargs={'account_id': account2.pk})
    response = authed_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_recurring_bad_account_id_returns_404(authed_client):
    url = reverse('analytics-recurring', kwargs={'account_id': 99999})
    response = authed_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_recurring_returns_monthly_correctly(authed_client, account):
    _seed_monthly(account, 'netflix', Decimal('15.99'))

    url = reverse('analytics-recurring', kwargs={'account_id': account.pk})
    response = authed_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    netflix = next(r for r in response.data if r['merchant'] == 'netflix')
    assert netflix['cadence'] == 'monthly'
    assert netflix['amount'] == -15.99 or netflix['amount'] == 15.99

def test_recurring_excludes_non_recurring_merchants(authed_client, account):
    _seed_monthly(account, 'netflix', Decimal('15.99'))
    TransactionFactory(account=account, merchant='random-one-time')

    url = reverse('analytics-recurring', kwargs={'account_id': account.pk})
    response = authed_client.get(url)

    merchants = [r['merchant'] for r in response.data]
    assert 'netflix' in merchants
    assert 'random-one-time' not in merchants