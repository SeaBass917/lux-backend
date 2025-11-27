"""URL configuration for the Manga in the project."""
from django.urls import path

from manga.views.manga_metadata_list import MangaMetadataListAPIView
from manga.views.manga_metadata import MangaMetadataAPIView

urlpatterns = [
    path("metadata/", MangaMetadataListAPIView.as_view()),
    path("metadata/<int:id>/", MangaMetadataAPIView.as_view()),
]
