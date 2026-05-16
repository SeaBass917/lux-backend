from rest_framework.serializers import ModelSerializer

from manga.models import Manga


class MangaListSerializer(ModelSerializer):
    """Serializer for the list view."""

    class Meta:
        model = Manga
        include = [
            'id',
            'title',
            'author',
            'artist',
            'art_resource_path'
            ]
