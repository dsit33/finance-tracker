from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Account
from users.models import User

class AccountTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='x')
        self.bob = User.objects.create_user(username='bob', password='y')
        Account.objects.create(user=self.alice, acc_type='checking', name='A-chk')
        Account.objects.create(user=self.bob, acc_type='checking', name='B-chk')

    def test_list_accounts_returns_only_mine(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.get(reverse("account-list"))

        assert response.status_code == status.HTTP_200_OK
        names = [a['name'] for a in response.data]
        assert names == ['A-chk']

    def test_list_accounts_requires_auth(self):
        response = self.client.get(reverse("account-list"))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_assigns_user_from_request(self):
        self.client.force_authenticate(user=self.alice)
        req = {"acc_type": "credit", "name": "A-credit", "currency": "USD"}

        response = self.client.post(reverse("account-list"), req, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        created = Account.objects.get(pk=response.data["id"])
        assert created.user == self.alice

    def test_update_others_account_is_404(self):
        bobs_account = Account.objects.get(user=self.bob)
        self.client.force_authenticate(user=self.alice)

        response = self.client.patch(
            reverse("account-detail", args=[bobs_account.pk]),
            {"name": "hacked"},
            format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        bobs_account.refresh_from_db()
        assert bobs_account.name != "hacked"
        