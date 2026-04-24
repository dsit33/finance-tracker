from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from datetime import date

def test_list_transactions_filtered_by_account_id_query(authed_client, account, transaction, other_transaction):
    response = authed_client.get(                                                                                                                                                
        reverse("transaction-list"), {"account_id": account.pk}                                                                                                         
    )                                                                                                                                                                          
    
    assert response.status_code == status.HTTP_200_OK
    hashes = [t["import_hash"] for t in response.data]                                                                                                                         
    assert transaction.import_hash in hashes
    assert other_transaction.import_hash not in hashes

def test_list_transactions_returns_only_mine(authed_client, account, transaction, account2, transaction2):
    response = authed_client.get(reverse('transaction-list'))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['account'] == account.id

def test_create_transaction_computes_hash_if_missing(authed_client, account):
    payload = {
        'account':account.pk,
        'date':date(2026, 4, 18),
        'amount':Decimal('14.50'),
        'merchant':'vons',
        'raw_merchant':'VONS PAC BEACH',
    }

    response = authed_client.post(reverse('transaction-list'), payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['import_hash'] != None

def test_create_duplicate_hash_returns_400(authed_client, account, transaction):
    payload = {
        'account':account.pk,
        'date':date(2026, 4, 18),
        'amount':Decimal('14.50'),
        'merchant':'vons',
        'raw_merchant':'VONS PAC BEACH',
        'import_hash':transaction.import_hash
    }

    response = authed_client.post(reverse('transaction-list'), payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'import_hash' in response.data

def test_cannot_create_transaction_for_other_users_account(authed_client, account2):
    payload = {
        'account':account2.pk,
        'date':date(2026, 4, 18),
        'amount':Decimal('14.50'),
        'merchant':'vons',
        'raw_merchant':'VONS PAC BEACH',
        'import_hash':'abc123'
    }

    response = authed_client.post(reverse('transaction-list'), payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'account' in response.data