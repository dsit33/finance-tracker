from django.urls import reverse
from rest_framework import status

from accounts.factories import AccountFactory
from accounts.models import Account


def test_list_accounts_requires_auth(api_client):
    response = api_client.get(reverse("account-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_accounts_returns_only_mine(authed_client, account, user2):
    AccountFactory(user=user2, name="B-chk")

    response = authed_client.get(reverse("account-list"))

    assert response.status_code == status.HTTP_200_OK
    names = [a["name"] for a in response.data]
    assert names == [account.name]


def test_create_assigns_user_from_request(authed_client, user):
    payload = {"acc_type": "credit", "name": "A-credit", "currency": "USD"}

    response = authed_client.post(reverse("account-list"), payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    created = Account.objects.get(pk=response.data["id"])
    assert created.user == user


def test_update_others_account_is_404(authed_client, user2):
    bobs_account = AccountFactory(user=user2)

    response = authed_client.patch(
        reverse("account-detail", args=[bobs_account.pk]),
        {"name": "hacked"},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    bobs_account.refresh_from_db()
    assert bobs_account.name != "hacked"
