from django.db import models

from lux.models import LuxBaseModel
from metadata.models import Tags


class MetadataBase(LuxBaseModel):
    """Base class for metadata models."""

    title = models.CharField(max_length=255)
    title_original = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=4096)
    tags = models.ManyToManyField(Tags)
    nsfw = models.BooleanField(
        default=True  # Assume the worst!
    )

    def __str__(self):
        return f"({self.id}) \"{self.title}\""
