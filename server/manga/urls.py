"""URL configuration for the Manga in the project."""
from django.urls import path

from manga.views.manga_metadata import MangaMetadataList

urlpatterns = [
    path("metadata/", MangaMetadataList.as_view()),
]
