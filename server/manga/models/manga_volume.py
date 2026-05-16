from django.db import models
from lux.models import LuxBaseModel
from manga.models.manga import Manga
from manga.models.manga_chapter import MangaChapter


class MangaVolume(LuxBaseModel):
    """A specific volume of a manga."""

    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='volumes')
    """The manga this volume belongs to."""

    volume_number = models.IntegerField()
    """The number of this volume in the series. Starts at 1."""

    name = models.CharField(max_length=255, null=True, blank=True)
    """The name of this volume. This can be null if we don't know or it was never given a name."""

    date_published = models.DateField(null=True, blank=True)
    """When was this volume published? This can be null if we don't know."""

    art_resource_path = models.CharField(max_length=4096, null=True, blank=True)
    """The path to the cover art for this volume. This is a relative path from the RESOURCE_BASE_URL. 
    This can be null if we don't have cover art for this volume.
    If none was made, we tend to use the first page of the first chapter as a fallback. So ideally this is never truly empty."""

    def __str__(self):
        name = self.name if self.name else f"Volume {self.volume_number}"
        return f"{self.manga.title} -- {name}"


