from django.db import models

from manga.constants.manga_types import MangaTypes
from manga.filters.manga_query_set import MangaQuerySet
from metadata.models import (
    MetadataBase,
    Person,
)


class Manga(MetadataBase):
    """Manga metadata. 
    NOTE: A lot of this can be null, because much of this is gathered piecemeal."""

    art_resource_path = models.CharField(max_length=4096, null=True, blank=True)
    """The path to the cover art for this manga. This is a relative path from the RESOURCE_BASE_URL. This can be null if we don't have cover art for this manga."""

    book_type = models.ForeignKey(MangaTypes, on_delete=models.PROTECT, null=True, blank=True)
    """The type of manga. This will change how the content is rendered."""

    author = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, blank=True)
    """The author of the manga. The one who wrote the story."""

    artist = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, blank=True)
    """The artist of the manga. The one who illustrated the story."""

    date_start = models.DateField(null=True, blank=True)
    """When did the first chapter publish? 
    If this is already marked in the Volumes/chapters below, then this is redundant.
    But if the info is not available at that granularity, then we indicate here at the root."""
    
    date_end = models.DateField(null=True, blank=True)
    """When did the last chapter publish? 
    If this is already marked in the Volumes/chapters below, then this is redundant.
    But if the info is not available at that granularity, then we indicate here at the root."""

    publisher = models.CharField(max_length=255, null=True, blank=True)
    """The publisher of the manga."""

    magazine = models.CharField(max_length=255, null=True, blank=True)
    """The magazine this manga was serialized in. This is usually only applicable for weekly/monthly serializations."""

    has_english_license = models.BooleanField(null=True, blank=True)
    """Whether this manga has an official English license. Or if it was fan-translated."""

    # This is where we inject custom filters for this table.
    objects: MangaQuerySet = MangaQuerySet.as_manager()
