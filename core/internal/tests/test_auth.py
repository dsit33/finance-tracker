from django.urls import reverse
from rest_framework import status

def test_no_key_returns_401(api_client, account):
    response = api_client.get(reverse('internal-recent', kwargs={'account_id': account.pk}))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_wrong_key_returns_401(api_client, account):
    api_client.credentials(HTTP_X_INTERNAL_KEY='not-the-right-key')
    response = api_client.get(reverse('internal-recent', kwargs={'account_id': account.pk}))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_right_key_returns_200(internal_client, account):
    response = internal_client.get(reverse('internal-recent', kwargs={'account_id': account.pk}), {'days': 30})

    assert response.status_code == status.HTTP_200_OK