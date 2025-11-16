from django.db import models

from lux.models import LuxBaseModel
from users.models import (
    BearerToken,
    Role,
)


class User(LuxBaseModel):
    """Users are just for auth. 
    They don't have names or anything else really.

    Attributes:
        id: UserId
        bearer_token: BearerToken
    """
    bearer_token = models.OneToOneField(
        BearerToken, on_delete=models.PROTECT, related_name='user')
    role = models.OneToOneField(
        Role, on_delete=models.PROTECT, related_name='user')

    def __str__(self) -> str:
        return f"({self.id})"
