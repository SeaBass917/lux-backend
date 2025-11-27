from django.db import models
from django.utils import timezone

from lux.models import LuxBaseModel


class BearerToken(LuxBaseModel):
    """
    Typically used for User Auth.

    Attributes:
        token (str): The unique token string.
        created_at (datetime): The timestamp when the Bearer Token was created.
        expires_at (datetime): The timestamp when the Bearer Token expires.
    """
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        """
        Checks if the Bearer Token is valid.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def __str__(self):
        """
        Returns a string representation of the Bearer Token.

        Returns:
            str: A string representation of the Bearer Token.
        """
        return "It's a BearerToken. Go away."
