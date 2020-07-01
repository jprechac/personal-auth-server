from django.contrib.auth import authenticate
from rest_framework import serializers

# Create your serializers here.


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to authenticate with the given credentials")

