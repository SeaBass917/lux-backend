from django.db import models

from lux.models import LuxBaseModel


class Module(LuxBaseModel):
    """This table stores the each known Module.

    Name is case insensitive.

    Attributes:
        module_name (str): Name of the module.
    """
    module_name = models.CharField(max_length=100)

    def __str__(self):
        return self.module_name
