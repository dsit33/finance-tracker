from accounts.models import Account
from users.models import User
from users.factories import UserFactory
import factory

class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)
    acc_type = 'checking'
    name = factory.Sequence(lambda n: 'account-{n}')