from django.shortcuts import render
from accounts.models import Account
from accounts.serializers import AccountSerializer
from rest_framework import viewsets

class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)