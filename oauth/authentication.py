from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import re

from oauth.models import AccessToken


class OauthBaseAuthentication(BaseAuthentication):
    def get_auth_token_from_header(self, request):
        headers = self.extract_headers(request)

        # if there is no Auth header, return None
        if 'Authentication' not in headers: return None

        auth_header = headers.get("Authentication")
        auth_header_match = re.match(r"Bearer (?P<token>\w+)", auth_header)
        token = auth_header_match.groupdict().get('token')
        return token

    def extract_headers(self, request):
        headers = request.META.copy()
        if "HTTP_AUTHENTICATION" in headers: # Bearer token authentication
            headers["Authentication"] = headers["HTTP_AUTHENTICATION"]

        return headers


class BearerTokenAuthentication(OauthBaseAuthentication):
    def authenticate(self, request):
        # get the token from the request
        token = self.get_auth_token_from_header(request)
        if token is None: raise AuthenticationFailed("Cannot identify an access token")

        invalid_token_exception = AuthenticationFailed("Token is not valid")

        # try to get the access token
        try:
            access_token = AccessToken.objects.get(token=token)
        except AccessToken.DoesNotExist:
            raise invalid_token_exception

        # validate the token
        if not token.is_valid(): raise invalid_token_exception

        return access_token.user, access_token.token



