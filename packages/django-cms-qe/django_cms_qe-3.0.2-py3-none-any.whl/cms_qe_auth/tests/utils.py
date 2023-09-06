import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.urls import clear_url_caches


class TestAuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return


def reset_urls():
    """Reset Django site urls."""
    del sys.modules[settings.ROOT_URLCONF]
    clear_url_caches()
