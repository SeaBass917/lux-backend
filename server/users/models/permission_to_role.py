from django.db import models

from lux.models import LuxBaseModel
from users.models import (
    Permission,
    Role,
)


class PermissionToRole(LuxBaseModel):
    """This table stores the each Permission to Role mapping.

    Attributes:
        role_ref (Role): Reference to the role.
        permission_ref (Permission): Reference to the permission.
    """
    permission_ref = models.ForeignKey(Permission, on_delete=models.PROTECT)
    role_ref = models.ForeignKey(Role, on_delete=models.PROTECT)
