from django.db import models

from resource_index.models.resource_index import ResourceIndexBase
from video.models.video_metadata import VideoMetadata


class VideoResourceIndex(ResourceIndexBase):
    """Links a video metadata entry to a resource index entry."""

    resource_id = models.ForeignKey(VideoMetadata, on_delete=models.CASCADE)
