from django.db import models

from manga.models.manga_metadata import MangaMetadata
from resource_index.models.resource_index import ResourceIndexBase


class MangaResourceIndex(ResourceIndexBase):
    """Links a manga metadata entry to a resource index entry."""

    resource_id = models.ForeignKey(MangaMetadata, on_delete=models.CASCADE)
