from django.db import models

from lux.models import LuxBaseModel
from users.models import Module


class Permission(LuxBaseModel):
    """This table stores the each Permission and its details.

    Attributes:
        permission_name (str):  Name of the permission. 
                                (e.g. users, create_invoice, etc.)
        action (str):   Action for the permission. 
                        (e.g. read, write, create, view, approve, etc.)
        module_ref (Module): Reference to the module.
    """
    module_ref = models.ForeignKey(Module, on_delete=models.PROTECT)
    permission_name = models.CharField(max_length=100)
    action = models.CharField(max_length=100)

    def __str__(self):
        return f"({self.module_ref},{self.permission_name},{self.action})"
