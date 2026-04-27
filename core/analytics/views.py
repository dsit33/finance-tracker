from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Account
from analytics.serializers import RecurringTransactionSerializer
from analytics.services import detect_recurring

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recurring(request, account_id: int):
    # multi-tenancy guard - 404 if not your account
    get_object_or_404(Account, pk=account_id, user=request.user)

    results = detect_recurring(account_id)
    serializer = RecurringTransactionSerializer(results, many=True)
    return Response(serializer.data)