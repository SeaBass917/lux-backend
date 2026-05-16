from rest_framework import serializers

from manga.models.manga_chapter import MangaChapter

class MangaChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MangaChapter
        exclude = ['manga']