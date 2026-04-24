import pytest
from rest_framework.test import APIClient

from users.factories import UserFactory
from accounts.factories import AccountFactory
from transactions.factories import TransactionFactory

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def user2(db):
    return UserFactory()

@pytest.fixture
def account(user):
    return AccountFactory(user=user)

@pytest.fixture
def other_account(user):
    return AccountFactory(user=user)

@pytest.fixture
def account2(user2):
    return AccountFactory(user=user2)

@pytest.fixture
def transaction(account):
    return TransactionFactory(account=account)

@pytest.fixture
def other_transaction(other_account):
    return TransactionFactory(account=other_account)

@pytest.fixture
def transaction2(account2):
    return TransactionFactory(account=account2)

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authed_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client