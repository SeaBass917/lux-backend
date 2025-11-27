from django.db import models

from lux.models import LuxBaseModel


class VideoTypes(LuxBaseModel):
    """Lookup table of types of video media 
    (e.g. TV, Movie, uh... anything else)."""

    name = models.CharField(max_length=32)
