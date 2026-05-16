from django.db import models
from lux.models import LuxBaseModel
from manga.models.manga import Manga
from manga.models.manga_volume import MangaVolume


class MangaChapter(LuxBaseModel):
    """A specific chapter of a manga."""

    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='chapters')
    """The manga this chapter belongs to. Never null. All children need a home."""

    volume = models.ForeignKey(MangaVolume, on_delete=models.CASCADE, null=True, blank=True)
    """The volume this chapter belongs to. This can be null if volume does not apply."""

    chapter_number = models.IntegerField()
    """The number of this chapter in the series. Starts at 1."""

    page_count = models.IntegerField()
    """The number of pages in this chapter."""

    name = models.CharField(max_length=255, null=True, blank=True)
    """The name of this chapter. This can be null if we don't know or it was never given a name."""

    date_published = models.DateField(null=True, blank=True)
    """When was this chapter published? This can be null if we don't know, 
    or if the chapter was published as part of a volume, in which case that data will come first.
    This is only for content that comes out a chapter at a time (e.g. weekly/monthly serializations)."""

    resource_path = models.CharField(max_length=4096)
    """The path to the content. This is a relative path from the RESOURCE_BASE_URL."""


    def __str__(self):
        name = self.name if self.name else f"Chapter {self.chapter_number}"
        return f"{self.manga.title} -- {name}"


