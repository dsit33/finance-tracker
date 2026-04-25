from django.urls import path
from internal.views import recent, bulk

urlpatterns = [
    path('accounts/<int:account_id>/transactions/recent', recent, name='internal-recent'),
    path('transactions/bulk/', bulk, name='internal-bulk'),
]