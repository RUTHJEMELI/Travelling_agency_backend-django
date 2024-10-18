from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # First try to get the token from the Authorization header
        header = self.get_header(request)
        if header is None:
            # If no header is present, try to get the token from cookies
            raw_token = request.COOKIES.get('access_token')
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        # Validate and return the user
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
