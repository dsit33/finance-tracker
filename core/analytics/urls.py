from django.urls import path

from analytics.views import recurring

urlpatterns = [
    path('accounts/<int:account_id>/recurring/', recurring, name='analytics-recurring'),
]