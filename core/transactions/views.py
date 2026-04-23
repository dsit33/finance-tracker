from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from rest_framework import viewsets

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = Transaction.objects.filter(account__user=self.request.user)
        account_id = self.request.query_params.get('account_id')

        if account_id:
            qs = qs.filter(account_id=account_id)

        return qs
