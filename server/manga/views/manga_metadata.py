from django.http import HttpRequest
from rest_framework import status

from manga.models import MangaMetadata
from manga.serializers import MangaMetadataSerializer
from manga.views import MangaBaseAPIView
from lux.constants import Permissions
from lux.views import permission_required


class MangaMetadataList(MangaBaseAPIView):
    """Ix with the manga metadata."""

    @permission_required(permission=Permissions.Browsing)
    def get(self, request: HttpRequest):
        """Return a response to indicate the server is running.

        Args:
            request (HttpRequest): The HTTP request.
                title: Optional; Comma-separated list of manga titles to filter by.

        Returns:
            200 OK: A response indicating the server is running.
            Else: A response indicating the server is not running.
        """

        titles = self.parse_url_list(request.GET.get("titles", ""))

        metadata_list = MangaMetadata.filter_by_titles(titles)

        serializer = MangaMetadataSerializer(metadata_list, many=True)

        return self.respond(
            result="success",
            message="Manga metadata list retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )
