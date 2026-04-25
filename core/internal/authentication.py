from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import hmac

class InternalServiceUser:
    is_authenticated = True
    is_anonymous = False

class InternalAPIKeyAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        return 'X-Internal-Key'
    
    def authenticate(self, request):
        request_key = request.META.get('HTTP_X_INTERNAL_KEY')

        if request_key is None:
            return None
        if not hmac.compare_digest(request_key, settings.INTERNAL_API_KEY):
            raise AuthenticationFailed('Internal API key did not match.')
        
        return (InternalServiceUser(), None)
