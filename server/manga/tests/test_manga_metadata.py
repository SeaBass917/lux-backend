"""Test suite: MangaMetadataList"""
from datetime import timezone
from rest_framework import status

from lux.utils.data_structures import sort_by_id
from manga.tests.manga_base_test import MangaBaseTest


class MangaMetadataListViewTest(MangaBaseTest):
    """
    Tests for the MangaMetadataList view.
    """

    def test_happy_path_list(self):
        """
        Happy path on the list endpoint.
        """
        self.set_up_user_with_role('Basic')

        metadata_list = self.create_manga_metadata_list(3)
        metadata_list.sort(key=sort_by_id)

        response = self.client.get("/api/v1/manga/metadata/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_list(self):
        """
        No-auth user wont get data.
        """
        response = self.client.get("/api/v1/manga/metadata/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
