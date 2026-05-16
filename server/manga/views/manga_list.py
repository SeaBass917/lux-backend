from rest_framework import status
from rest_framework.request import Request

from lux.views.lux_base_api_view import LuxBaseAPIView, enforce_interface
from manga.interfaces.manga_list_filter_request import MangaListFilterRequest
from manga.models import Manga
from manga.serializers.manga_list_serializer import MangaListSerializer


class MangaListView(LuxBaseAPIView):
    """Ix with the manga metadata."""

    @enforce_interface(MangaListFilterRequest)
    def post(self, request: Request, data: MangaListFilterRequest):
        """List view of the manga metadata.

        Args:
            request (Request): The HTTP request object.
            data (MangaListFilterRequest): The dataclass instance containing the list of filters to apply.

        Returns:
            200 OK: A response indicating the server is running.
            Else: A response indicating the server is not running.
        """

        querysets = [Manga.objects.custom_filter(f) for f in data.filters]
        
        res_data = [MangaListSerializer(metadata_list, many=True).data for metadata_list in querysets]

        return self.respond(
            data=res_data,
            status_code=status.HTTP_200_OK,
        )
