from transactions.hashing import compute_import_hash
from rest_framework import serializers
from transactions.models import Transaction
from django.db import IntegrityError

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'date', 'amount', 'merchant',
                  'raw_merchant', 'category', 'import_hash', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'import_hash': {'required': False}}

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {'import_hash': 'Transaction with this has already exists'}
            )

    def validate(self, attrs):
        if 'import_hash' not in attrs:
            attrs['import_hash'] = compute_import_hash(   
                attrs['account'].id,
                attrs['date'],
                attrs['amount'],
                attrs['raw_merchant']
            )

        return attrs

    def validate_account(self, account):
        if account.user.id != self.context['request'].user.id:
            raise serializers.ValidationError('Invalid account.')

        return account