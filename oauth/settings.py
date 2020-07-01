from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Configure app settings
# import this config with 
#   from oauth import settings as app_settings

NAMESPACE = "OAUTH"
def _get_setting(name, default, output_type=str, namespace=NAMESPACE, raise_exception=True):
    raw_setting = getattr(settings, '_'.join([NAMESPACE, name]), default)

    try:
        return output_type(raw_setting)
    except ValueError:
        if raise_exception:
            raise ImproperlyConfigured(f"Setting '{name}' must be type '{output_type}'")
        return default


RESOURCE_STRING = _get_setting('RESOURCE_STRING', r"rid:(?P<client_id>\w+):(?P<client_secret>\w+)")
ACCESS_TOKEN_EXPIRATION_HOURS = _get_setting('ACCESS_TOKEN_EXPIRATION_HOURS', 5, output_type=int)
REFRESH_TOKEN_EXPIRATION_DAYS = _get_setting('REFRESH_TOKEN_EXPIRATION_DAYS', 2, output_type=int)
TOKEN_LENGTH = _get_setting('TOKEN_LENGTH', 200, output_type=int)
USE_REFRESH_TOKEN_EXPIRATION = _get_setting('USE_REFRESH_TOKEN_EXPIRATION', True, output_type=bool)

