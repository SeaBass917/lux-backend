from django.db import models

from metadata.models import (
    MetadataBase,
    WebDataSource,
)
from video.models import VideoTypes


class VideoMetadata(MetadataBase):
    """Video metadata."""

    video_type = models.ForeignKey(
        VideoTypes,
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    studio = models.CharField(max_length=255, null=True, blank=True)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    date_added = models.DateField(null=True, blank=True)
    has_english_license = models.BooleanField(null=True, blank=True)
    visited_sources = models.ManyToManyField(WebDataSource)
