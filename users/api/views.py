from django.contrib.auth import authenticate
from rest_framework import authentication, generics, permissions, views

from users.api import serializers

# Create your views here.


class ApiLoginView(generics.GenericAPIView):
    authentication_classes = []
    serializer_class = serializers.LoginUserSerializer

    # POST api/users/login
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # perform the authentication, sends the user to serializer.validated_data

        user = serializer.validated_data

        



