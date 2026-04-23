from django.db import models
from accounts.models import Account

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField(db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    merchant = models.CharField(max_length=100, db_index=True)
    raw_merchant = models.CharField(max_length=200)
    category = models.CharField(max_length=30, null=True, blank=True)
    import_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.date} ${self.merchant} ${self.amount}"

    class Meta:
        indexes = [models.Index(fields=['account', '-date'])]
        ordering = ['-date']