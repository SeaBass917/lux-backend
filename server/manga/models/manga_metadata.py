from django.db import models

from metadata.models import (
    MetadataBase,
    Person,
    WebDataSource,
)
from manga.models import MangaTypes


class MangaMetadata(MetadataBase):
    """Manga metadata."""

    book_type = models.ForeignKey(
        MangaTypes,
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    author = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="mangametadata_author",
        null=True, blank=True
    )
    artist = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="mangametadata_artist",
        null=True, blank=True
    )
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    date_added = models.DateField(null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    magazine = models.CharField(max_length=255, null=True, blank=True)
    has_english_license = models.BooleanField(null=True, blank=True)
    num_volumes = models.IntegerField(null=True, blank=True)
    num_chapters = models.IntegerField(null=True, blank=True)
    visited_sources = models.ManyToManyField(WebDataSource)

    def filter_by_titles(self, titles: list[str]) -> models.QuerySet:
        """Filter manga metadata by titles.

        Args:
            titles (list[str]): The list of titles to filter by.

        Returns:
            models.QuerySet: The filtered manga metadata queryset.
        """
        if not titles:
            return self.all()

        query = models.Q()
        for title in titles:
            query |= models.Q(title__icontains=title)
            query |= models.Q(title_original__icontains=title)

        return self.filter(query)
