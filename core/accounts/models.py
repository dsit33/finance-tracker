from django.db import models
from django.conf import settings

class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    acc_type = models.CharField(choices=[('checking', 'Checking'), ('credit', 'Credit'), ('savings', 'Savings')], max_length=16)
    name = models.CharField(max_length=30)
    currency = models.CharField(default='USD', max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)