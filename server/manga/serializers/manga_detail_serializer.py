from rest_framework.serializers import ModelSerializer

from manga.models import Manga
from manga.serializers.manga_chapter_serializer import MangaChapterSerializer
from manga.serializers.manga_volume_serializer import MangaVolumeSerializer


class MangaDetailSerializer(ModelSerializer):
    """Serialize for the detail view. Includes the chapters and volume info."""

    # Map the child relationships explicitly using your defined serializers
    # Note: 'many=True' creates the array, 'read_only=True' stops inbound writes
    chapters = MangaChapterSerializer(many=True, read_only=True, source='chapters')
    volumes = MangaVolumeSerializer(many=True, read_only=True, source='volumes')

    class Meta:
        model = Manga
        exclude = []
