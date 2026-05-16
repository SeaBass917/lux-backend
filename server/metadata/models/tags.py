from django.db import models

from lux.models import LuxBaseModel


class Tags(LuxBaseModel):
    """Lookup table of tags used on media.
    Seeded with a basic fixture... just in case we want to enforce some standard tags. But can be added to as needed."""

    name = models.CharField(max_length=32)
