from django.db import models

from lux.models import LuxBaseModel


class MangaTypes(LuxBaseModel):
    """Lookup table of types of books 
    (e.g. Manga, Manhwa, Web Comic)."""

    name = models.CharField(max_length=32)
