"""Test suite: MangaMetadataList"""
from datetime import timezone
from rest_framework import status

from lux.utils.data_structures import sort_by_id
from manga.models.manga_metadata import MangaMetadata
from manga.serializers.manga_metadata_serializer import MangaMetadataSerializer
from manga.tests.manga_base_test import MangaBaseTest


class MangaMetadataViewTest(MangaBaseTest):
    """
    Tests for the MangaMetadataAPIView.
    """

    def test_happy_path_get(self):
        """Happy path on the getter endpoint. It exists."""
        self.set_up_user_with_role('Basic')

        metadata = self.create_manga_metadata()

        serializer = MangaMetadataSerializer(metadata)
        metadata_data = serializer.data

        response = self.client.get(f"/api/v1/manga/metadata/{metadata.id}/")
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.content)

        data: MangaMetadata = response.json()['data']
        self.assertDictEqual(metadata_data, data)

    def test_auth_get(self):
        """No-auth user wont get data."""
        metadata = self.create_manga_metadata()
        response = self.client.get(f"/api/v1/manga/metadata/{metadata.id}/")
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED, response.content)

    def test_missing_get(self):
        """Getting a non-existent metadata returns 404."""
        self.set_up_user_with_role('Basic')

        response = self.client.get(f"/api/v1/manga/metadata/9999/")
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND, response.content)
