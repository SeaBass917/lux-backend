from django.http import HttpRequest
from rest_framework import status

from lux.views.lux_base_api_view import LuxBaseAPIView
from manga.models import Manga
from manga.serializers.manga_detail_serializer import MangaDetailSerializer


class MangaMetadataAPIView(LuxBaseAPIView):
    """Ix with single manga metadata."""

    def get(self, request: HttpRequest, id: str):
        """Return a response to indicate the server is running.

        Args:
            request (HttpRequest): The HTTP request.
                (Only used during auth in the wrapper)
            id (str): The ID of the manga metadata to retrieve.


        Returns:
            200 OK: A response indicating the server is running.
            Else: A response indicating the server is not running.
        """

        metadata = Manga.objects.prefetch_related('chapters', 'volumes').get(id=id)
        
        serializer = MangaDetailSerializer(metadata)

        return self.respond(
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )
