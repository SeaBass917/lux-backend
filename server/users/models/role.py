import uuid
from django.db import models

from lux.models import LuxBaseModel


class Role(LuxBaseModel):
    """This table stores the each Role and its details.

    Attributes:
        role (str): Name of the role.
        public_id (UUID): Unique identifier for the role.
    """
    role = models.CharField(max_length=100)
    public_id = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.role
