from datetime import date as _date
from datetime import timedelta
from transactions.factories import TransactionFactory

from decimal import Decimal
from django.urls import reverse
from rest_framework import status

def test_recent_days_defaults_to_60(internal_client, account):
    in_window = TransactionFactory(account=account, date=_date.today())
    out_of_window = TransactionFactory(account=account, date=_date.today() - timedelta(days=90))

    response = internal_client.get(reverse('internal-recent', kwargs={'account_id': account.pk}))

    assert response.status_code == status.HTTP_200_OK
    hashes = [t['import_hash'] for t in response.data]
    assert in_window.import_hash in hashes
    assert out_of_window.import_hash not in hashes

def test_bulk_create_skips_existing_rows(internal_client, account):
    transactions = [
        {
            'account': account.pk,
            'date': _date(2026, 4, 20),
            'amount': Decimal('10.00'),
            'merchant': f'test merchant {i}',
            'raw_merchant': f'TEST MERCHANT {i}'
        } for i in range(10)]

    response = internal_client.post(reverse('internal-bulk'), transactions, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['created'] == 10
    assert response.data['skipped'] == 0
    response = internal_client.post(reverse('internal-bulk'), transactions, format='json')
    assert response.data['created'] == 0
    assert response.data['skipped'] == 10
