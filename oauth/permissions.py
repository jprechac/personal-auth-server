from rest_framework.permissions import BasePermission

import re

from oauth.models import Application

# Write Permissions here

class OauthBasePermission(BasePermission):

    def extract_headers(self, request):
        headers = request.META.copy()
        if "HTTP_AUTHORIZATION" in headers: # Bearer token authentication
            headers["Authorization"] = headers["HTTP_AUTHORIZATION"]
        if "HTTP_RESOURCE_ID" in headers:
            headers['ResourceId'] = headers["HTTP_RESOURCE_ID"]

        return headers

class ApplicationRegisteredPermission(OauthBasePermission):
    """
    Used for checking the client's Application credentials,
    to ensure that the client is allowed to make a request to this server.

    Looks for an HTTP Header, 'Resource-ID' (or 'HTTP_RESOURCE_ID' in Django's world),
    and uses the values in it to validate the Application state. 
    See the documentation on client applications for Resource ID contruction.
    """

    def has_permission(self, request, view):
        # Get the Resource header
        # If there isn't one, return False
        headers = self.extract_headers(request)
        resource_header = headers.get('ResourceId', None)
        if resource_header == None: return False

        return Application.is_valid(resource_header)

