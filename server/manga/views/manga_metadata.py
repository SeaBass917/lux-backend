from django.http import HttpRequest
from rest_framework import status

from lux.views.lux_base_api_view import LuxBaseAPIView
from manga.models import MangaMetadata
from manga.serializers import MangaMetadataSerializer


class MangaMetadataAPIView(LuxBaseAPIView):
    """Ix with single manga metadata."""

    def get(self, request: HttpRequest, id: int):
        """Return a response to indicate the server is running.

        Args:
            request (HttpRequest): The HTTP request.
                (Only used during auth in the wrapper)
            id (int): The ID of the manga metadata to retrieve.


        Returns:
            200 OK: A response indicating the server is running.
            Else: A response indicating the server is not running.
        """

        metadata = MangaMetadata.objects.get(id=id)
        serializer = MangaMetadataSerializer(metadata)

        return self.respond(
            result="success",
            message="Manga metadata retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def put(self, request: HttpRequest, id: int):
        """Update manga metadata.

        Args:
            request (HttpRequest): The HTTP request.
                (Only used during auth in the wrapper)
            id (int): The ID of the manga metadata to update.

        Returns:
            200 OK: A response indicating the server is running.
            Else: A response indicating the server is not running.
        """

        metadata = MangaMetadata.objects.get(id=id)
        serializer = MangaMetadataSerializer(
            metadata, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return self.respond(
                result="success",
                message="Manga metadata updated successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        else:
            return self.respond(
                result="error",
                message="Invalid data provided.",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request: HttpRequest, id: int):
        """Delete manga metadata.

        Args:
            request (HttpRequest): The HTTP request.
                (Only used during auth in the wrapper)
            id (int): The ID of the manga metadata to delete.

        Returns:
            200 OK: A response indicating the server is running.
            Else: A response indicating the server is not running.
        """

        metadata = MangaMetadata.objects.get(id=id)
        metadata.delete()

        return self.respond(
            result="success",
            message="Manga metadata deleted successfully.",
            status_code=status.HTTP_200_OK,
        )
