from rest_framework.serializers import (
    ModelSerializer,
)

from manga.models import MangaMetadata


class MangaMetadataSerializer(ModelSerializer):
    """MangaMetadata serializer class."""

    class Meta:
        model = MangaMetadata
        exclude = []
