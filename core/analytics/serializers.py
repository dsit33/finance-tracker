from rest_framework import serializers

class RecurringTransactionSerializer(serializers.Serializer):
    merchant = serializers.CharField()
    cadence = serializers.CharField()
    confidence = serializers.FloatField()
    median_gap_days = serializers.IntegerField()
    amount = serializers.FloatField()
    next_expected_date = serializers.DateField()