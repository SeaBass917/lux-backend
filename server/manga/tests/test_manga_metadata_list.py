"""Test suite: MangaMetadataList"""
from datetime import timezone
from rest_framework import status

from lux.utils.data_structures import sort_by_id
from manga.models.manga import Manga
from manga.serializers.manga_detail_serializer import MangaMetadataSerializer
from manga.tests.manga_base_test import MangaBaseTest


class MangaMetadataListViewTest(MangaBaseTest):
    """
    Tests for the MangaMetadataList view.
    """

    def test_happy_path_list(self):
        """
        Happy path on the list endpoint. No filters.
        """
        self.set_up_user_with_role('Basic')

        metadata_list = self.create_manga_metadata_list(3)
        serializer = MangaMetadataSerializer(metadata_list, many=True)
        metadata_list = serializer.data
        metadata_list.sort(key=sort_by_id)

        response = self.client.get("/api/v1/manga/metadata/")
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.content)

        data: list[Manga] = response.json()['data']
        data.sort(key=sort_by_id)
        self.assert_dict_lists_equal(metadata_list, data)

    def test_auth_list(self):
        """
        No-auth user wont get data.
        """
        response = self.client.get("/api/v1/manga/metadata/")
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED, response.content)
