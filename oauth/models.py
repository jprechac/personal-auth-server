from __future__ import absolute_import

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from oauthlib import common

import datetime
import re
import uuid

from oauth import managers
from oauth import settings as app_settings


# Create your models here.


def generate_token():
    token_limit = app_settings.TOKEN_LENGTH
    return common.generate_token(length=token_limit)

def access_token_expiration_time():
    now = timezone.now()
    return now + datetime.timedelta(hours=app_settings.ACCESS_TOKEN_EXPIRATION_HOURS)

def refresh_token_expiration_time():
    now = timezone.now()
    return now + datetime.timedelta(hours=app_settings.REFRESH_TOKEN_EXPIRATION_DAYS)



class Application(models.Model):
    REDACTION_STRING_FORMAT = "{}**********"

    # ID -> AutoField, primary key

    name = models.CharField(
        max_length=100,
        null=False, blank=False,
        verbose_name=_("Application Name")
        # help_text=_("")
    )

    client_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False, unique=True,
        verbose_name=_("Client ID")
    )

    client_secret = models.UUIDField(
        default=uuid.uuid4,
        editable=False, unique=True,
        verbose_name=_("Client Secret")
    )

    CLIENT = 'client'
    SERVICE = 'service'
    _type_choices = (
        (CLIENT, 'Client App'),
        (SERVICE, 'Web Service'),
    )
    type = models.CharField( # the kind of application this is... client app, web service, others...?
        max_length=16,
        choices=_type_choices,
        null=False, blank=False,
        verbose_name=_("Type"),
        help_text=_("The type of application this is")
    )

    active = models.BooleanField(
        null=False, blank=False, default=True,
        verbose_name=_("Active")
    )
    created_date = models.DateTimeField(
        auto_now_add=True
    )
    updated_date = models.DateTimeField(
        auto_now=True
    )

    @property
    def client_id_redacted(self):
        return self.REDACTION_STRING_FORMAT.format(str(self.client_id)[:3])
    @property
    def client_secret_redacted(self):
        return self.REDACTION_STRING_FORMAT.format(str(self.client_secret)[:3])
    @property
    def should_redact_fields(self):
        now = timezone.now()
        five_minutes_ago = now - datetime.timedelta(minutes=5)
        return self.created_date < five_minutes_ago


    @property
    def resource_id(self):
        """
        Show the unique identification string for this Application.
        The identification string is defined in the settings as OAUTH_RESOURCE_STRING
        """
        return f"rid:{self.client_id}:{self.client_secret}"

    @classmethod
    def is_valid(cls, resource_id=None, client_id=None, client_secret=None):
        """
        Validate the Application with the client ID and secret.

        Steps:
        0. Validation
        1. Must find an application with this ID and Secret
        2. Application must be active
        """
        # Validate arguments
        if (resource_id is None) and (client_id is None and client_secret is None):
            return TypeError("Can't have all the arguments null")

        # Get client info from the resource ID, if it's provided.
        if resource_id is not None: # convert the resource ID into the client ID and secret
            resources = cls.extract_resource_id(resource_id)
            client_id = resources['client_id']
            client_secret = resources['client_secret']

        # Step 1.
        apps = cls.objects.filter(client_id=client_id, client_secret=client_secret)
        if not apps.exists(): return False
        if apps.count() > 1: return False # This should be impossible, but doesn't hurt to check

        app = apps.first() # Get the actual application instance.

        # Step 2.
        if not app.active: return False

        return True

    @staticmethod
    def extract_resource_id(resource_id):
        if not isinstance(resource_id, str): raise TypeError("Parameter 'resource_id' must be a string")

        match_string = re.match(app_settings.RESOURCE_STRING, resource_id)
        return match_string.groupdict()


    # The Django stuff...
    objects = managers.ApplicationManager()

    def __str__(self):
        return self.name


class RefreshToken(models.Model):
    """
    user, expiration, application,
    token,
    created_date, updated_date
    """

    # ID -> AutoField, primary key

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="refresh_tokens",
        null=False, blank=False,
        verbose_name=_("User")
    )

    application = models.ForeignKey(
        to='Application',
        on_delete=models.CASCADE,
        related_name='refresh_tokens',
        null=False, blank=False,
        verbose_name=_("Application")
    )

    token = models.CharField(
        max_length=255,
        null=False, blank=False,
        default=generate_token,
        verbose_name=_("Token")
    )

    expiration = models.DateTimeField(
        null=False, blank=False,
        default=refresh_token_expiration_time,
        verbose_name=_("Expiration")
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )
    updated_date = models.DateTimeField(
        auto_now=True
    )

    objects = managers.RefreshTokenManager()


class AccessToken(models.Model):
    """
    user, expiration date, application, 
    refresh_token (1:1),
    token,
    created_date, updated_date, 
    """
    
    # ID -> AutoField, primary key

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="access_tokens",
        null=False, blank=False,
        verbose_name=_("User")
    )

    refresh_token = models.ForeignKey(
        to='RefreshToken',
        on_delete=models.CASCADE,
        related_name='access_tokens',
        null=True, blank=True, # if null, then this access token cannot be updated
        verbose_name=_("Refresh Token")
    )

    application = models.ForeignKey(
        to='Application',
        on_delete=models.CASCADE,
        related_name="access_tokens",
        null=False, blank=False,
        verbose_name=_("Application")
    )

    token = models.CharField(
        max_length=255,
        null=False, blank=False,
        default=generate_token,
        verbose_name=_("Token")
    )

    expiration = models.DateTimeField(
        null=False, blank=False,
        default=access_token_expiration_time,
        verbose_name=_("Expiration")
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )
    updated_date = models.DateTimeField(
        auto_now=True
    )

    objects = managers.AccessTokenManager()

    def is_valid(self):
        # validation is:
        #   1. the token is not expired
        #   2. the token's application is still active

        # 1. 
        token_is_expired = self.expiration > timezone.now()
        if token_is_expired: return False

        # 2. 
        if not self.application.active: return False

        # if the token passes all checks, return True
        return True

    # def register_token






