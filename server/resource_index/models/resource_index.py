"""ResourceIndexBase model definition."""
from django.db import models

from lux.models import LuxBaseModel


class ResourceIndexBase(LuxBaseModel):
    """Base class for ResourceIndex models."""

    @property
    def resource_id(self):
        raise NotImplementedError(
            "Subclasses must define 'resource_id' as a ForeignKey.")

    resource_path = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True
