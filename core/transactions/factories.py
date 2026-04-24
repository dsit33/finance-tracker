import random

import factory
from transactions.models import Transaction
from users.models import User
from accounts.models import Account
from accounts.factories import AccountFactory
from datetime import date as _date, timedelta

class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    account = factory.SubFactory(AccountFactory)
    date = factory.LazyFunction(lambda: _date.today() - timedelta(days=random.randint(0, 365)))
    amount = factory.Faker(
        'pydecimal',
        left_digits=3,
        right_digits=2,
        positive=True,
        min_value=1.00,
        max_value=999.99
    )
    merchant = 'test-merchant'
    raw_merchant = 'TEST MERCHANT'
    import_hash = factory.Sequence(lambda n: f'hash-{n}')