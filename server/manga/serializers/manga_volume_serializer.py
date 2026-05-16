from rest_framework import serializers

from manga.models.manga_volume import MangaVolume

class MangaVolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MangaVolume
        exclude = ['manga']