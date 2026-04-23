from rest_framework.routers import DefaultRouter
from accounts.views import AccountViewSet

router = DefaultRouter()
router.register(r"", AccountViewSet, basename="account")

urlpatterns = router.urls