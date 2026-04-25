from transactions.serializers import TransactionSerializer
from transactions.models import Transaction
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from internal.authentication import InternalAPIKeyAuthentication

from datetime import timedelta
from django.utils import timezone

@api_view(['GET'])
@authentication_classes([InternalAPIKeyAuthentication])
@permission_classes([IsAuthenticated])
def recent(request, account_id):
    days = request.query_params.get('days', 60)
    try:
        days = int(days)
    except (TypeError, ValueError):
        return Response({'days': 'Must be an integer.'}, status=400)
    
    cutoff = timezone.localdate() - timedelta(days=days)

    qs = Transaction.objects.filter(account=account_id, date__gte=cutoff)
    serializer = TransactionSerializer(qs, many=True)

    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([InternalAPIKeyAuthentication])
@permission_classes([IsAuthenticated])
def bulk(request):
    payload = request.data
    serializer = TransactionSerializer(data=payload, many=True)
    serializer.is_valid(raise_exception=True)

    instances = [Transaction(**d) for d in serializer.validated_data]
    hashes = [inst.import_hash for inst in instances]
    existing = set(
        Transaction.objects.filter(import_hash__in=hashes).values_list('import_hash', flat=True)
    )
    Transaction.objects.bulk_create(instances, ignore_conflicts=True)
    return Response({
        'created': len(instances) - len(existing),
        'skipped': len(existing)
    })