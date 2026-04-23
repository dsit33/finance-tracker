from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import date

from transactions.models import Transaction
from accounts.models import Account
from users.models import User

class TransactionTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='x')
        self.bob = User.objects.create_user(username='bob', password='y')
        self.alice_acc = Account.objects.create(user=self.alice, acc_type='checking', name='A-chk')
        self.bob_acc = Account.objects.create(user=self.bob, acc_type='checking', name='B-chk')

        Transaction.objects.create(
            account=self.alice_acc,
            date=date(2026, 4, 20),
            amount=Decimal('20.50'),
            raw_merchant='Shell Gas Station',
            merchant='shell',
            import_hash='abc123'
        )
        Transaction.objects.create(
            account=self.alice_acc,
            date=date(2026, 4, 21),
            amount=Decimal('12.29'),
            merchant='netflix',
            raw_merchant='NETFLIX.COM 123',
            import_hash='def456'
        )

        Transaction.objects.create(
            account=self.bob_acc,
            date=date(2026, 4, 20),
            amount=Decimal('30.99'),
            merchant='anthropic',
            raw_merchant='ANTHROPIC CLAUDE SUB MAX',
            import_hash='ags239'
        )
        Transaction.objects.create(
            account=self.bob_acc,
            date=date(2026, 4, 21),
            amount=Decimal('450.24'),
            merchant='costco',
            raw_merchant='COSTCO WHOLESALE KEARNY',
            import_hash='csc578'
        )

    def test_list_transactions_filtered_by_account_id_query(self):
        self.client.force_authenticate(user=self.alice)                                                                                                                            
        second = Account.objects.create(user=self.alice, acc_type="credit", name="A-credit")                                                                                       
        Transaction.objects.create(account=second, date=date(2026, 4, 22),                                                                                                         
                                    amount=Decimal("9.00"), merchant="x",                                                                                                           
                                    raw_merchant="X", import_hash="xyz999")                                                                                                         
                                                                                                                                                                                    
        response = self.client.get(                                                                                                                                                
            reverse("transaction-list"), {"account_id": self.alice_acc.pk}                                                                                                         
        )                                                                                                                                                                          
                                        
        hashes = [t["import_hash"] for t in response.data]                                                                                                                         
        assert "xyz999" not in hashes

    def test_list_transactions_filtered_by_account(self):
        self.client.force_authenticate(user=self.alice)

        response = self.client.get(reverse('transaction-list'))

        assert response.status_code == status.HTTP_200_OK
        hashes = [a['import_hash'] for a in response.data]
        assert hashes == ['def456', 'abc123']

    def test_create_transaction_computes_hash_if_missing(self):
        self.client.force_authenticate(user=self.alice)

        payload = {
            'account':self.alice_acc.pk,
            'date':date(2026, 4, 18),
            'amount':Decimal('14.50'),
            'merchant':'vons',
            'raw_merchant':'VONS PAC BEACH',
        }

        response = self.client.post(reverse('transaction-list'), payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['import_hash'] != None

    def test_create_duplicate_hash_returns_400(self):
        self.client.force_authenticate(user=self.alice)

        payload = {
            'account':self.alice_acc.pk,
            'date':date(2026, 4, 18),
            'amount':Decimal('14.50'),
            'merchant':'vons',
            'raw_merchant':'VONS PAC BEACH',
            'import_hash':'abc123'
        }

        response = self.client.post(reverse('transaction-list'), payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_create_transaction_for_other_users_account(self):
        self.client.force_authenticate(user=self.alice)

        payload = {
            'account':self.bob_acc.pk,
            'date':date(2026, 4, 18),
            'amount':Decimal('14.50'),
            'merchant':'vons',
            'raw_merchant':'VONS PAC BEACH',
            'import_hash':'abc123'
        }

        response = self.client.post(reverse('transaction-list'), payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST