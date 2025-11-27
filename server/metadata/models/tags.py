from django.db import models

from lux.models import LuxBaseModel


class Tags(LuxBaseModel):
    """Lookup table of tags used on media."""

    name = models.CharField(max_length=32)
