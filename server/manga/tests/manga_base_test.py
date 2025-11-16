"""Base class for all the tests in the Manga scope."""

from datetime import datetime
from django.utils import timezone
from faker import Faker
from lux.tests import LuxBaseTest
from manga.models.manga_metadata import MangaMetadata
from manga.models.manga_types import MangaTypes
from metadata.models.person import Person
from metadata.models.web_data_source import WebDataSource

faker = Faker()


class MangaBaseTest(LuxBaseTest):
    """Shared class for all the tests in the Manga scope."""

    fixtures = LuxBaseTest.fixtures + \
        ['000_web_data_sources.json', '000_manga_types.json']

    @staticmethod
    def create_manga_metadata(book_type: MangaTypes | None = None,
                              author: Person | None = None,
                              artist: Person | None = None,
                              date_start: datetime | None = None,
                              date_end: datetime | None = None,
                              date_added: datetime | None = None,
                              publisher: str | None = None,
                              magazine: str | None = None,
                              has_english_license: bool | None = None,
                              num_volumes: int | None = None,
                              num_chapters: int | None = None,
                              visited_sources: list[WebDataSource] | None = None) -> list[MangaMetadata]:
        """Create a single manga metadata.

        Args:
            ... fields of MangaMetadata ...

        Returns:
            MangaMetadata: The metadata.
        """
        metadata = MangaMetadata.objects.create(
            book_type=faker.random_choices(MangaTypes.objects.all(), 1)[
                0] if book_type is None else book_type,
            author=LuxBaseTest.create_person() if author is None else author,
            artist=LuxBaseTest.create_person() if artist is None else artist,
            date_start=faker.past_date() if date_start is None else date_start,
            date_end=faker.date_between_dates(
                date_end=date_start) if date_end is None else date_end,
            date_added=timezone.now() if date_added is None else date_added,
            publisher=faker.company_name_word() if publisher is None else publisher,
            magazine=faker.company_name_word() if magazine is None else magazine,
            has_english_license=faker.boolean(
            ) if has_english_license is None else has_english_license,
            num_volumes=faker.random_int(
                1, 45) if num_volumes is None else num_volumes,
            num_chapters=faker.random_int(
                1, 45) if num_chapters is None else num_chapters,
        )

        visited_sources = [WebDataSource.objects.get(
            id=1)] if visited_sources is None else visited_sources
        if visited_sources:
            metadata.visited_sources.add(visited_sources)

        return metadata

    @staticmethod
    def create_manga_metadata_list(count: int = 3) -> list[MangaMetadata]:
        """Create a list of manga metadata.

        Args:
            count (int, optional): The number of records to make. Defaults to 3.

        Returns:
            list[MangaMetadata]: The metadata.
        """
        metadata_list: list[MangaMetadata] = []
        for _ in range(count):
            [author, artist] = LuxBaseTest.create_people(2)
            start_date = faker.past_date()
            now = timezone.now()
            b_type = faker.random_choices(
                MangaTypes.objects.all(), 1)[0]
            metadata_list.append(MangaMetadata(
                book_type=b_type,
                author=author,
                artist=artist,
                date_start=start_date,
                date_end=faker.date_between_dates(date_start=start_date),
                date_added=now,
                publisher=faker.company(),
                magazine=faker.company(),
                has_english_license=faker.boolean(),
                num_volumes=faker.random_int(1, 45),
                num_chapters=faker.random_int(1, 45)))

        MangaMetadata.objects.bulk_create(metadata_list)

        datasources = WebDataSource.objects.all()
        for metadata in metadata_list:
            metadata.visited_sources.add(*faker.random_choices(datasources, 2))
            metadata.save()  # technically not the most effiecient but eh..

        return metadata_list
