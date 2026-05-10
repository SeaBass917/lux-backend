"""This module contains the base test class for the APIs."""
from typing import Any
from django.test import TestCase, Client
from faker import Faker
from json import dumps

from lux.constants.roles import Roles
from metadata.models.person import Person
from users.models import User


class LuxBaseTest(TestCase):
    """Base class for all tests against this API."""

    fixtures = []

    faker = Faker()
    faker_jp = Faker('ja_JP')

    @staticmethod
    def create_user(username: str = None, role: Roles = Roles.ADULT) -> User:
        """Create a user object in the Users table.
        All details of that user are randomly generated using the faker library,
        unless otherwise specified.

        Raises:
            ValidationError: If the fields are not valid.
        """
        if username is None:
            username = LuxBaseTest.faker.user_name()

        user = User.objects.create(username=username, role=role)
        return user

    @staticmethod
    def create_person(name: str | None = None) -> Person:
        """Create a person.

        Raises:
            ValidationError: If the fields are not valid.
        """
        if name is None:
            name = LuxBaseTest.faker.name()

        return Person.objects.create(name=name)

    @staticmethod
    def create_people(count: int = 3) -> list[Person]:
        """Create a list of people.

        Args:
            count (int, optional): Number of people to make. Defaults to 3.

        Returns:
            list[Person]: The people.

        Raises:
            ValidationError: If the fields are not valid.
        """
        return Person.objects.bulk_create(
            [Person(name=LuxBaseTest.faker.name()) for _ in range(count)])

    def assert_dict_lists_equal(test_case_instance, list1: list[dict[str, Any]], list2: list[dict[str, Any]], key_to_sort_by: str = None):
        """
        Compares two lists of dictionaries for equality, providing a detailed error message 
        if differences are found. Optionally sorts lists by a key before comparison.
        """

        # Optional: Sort lists if order doesn't matter, which helps prevent false failures
        if key_to_sort_by:
            list1_sorted = sorted(list1, key=lambda x: x.get(key_to_sort_by))
            list2_sorted = sorted(list2, key=lambda x: x.get(key_to_sort_by))
        else:
            list1_sorted = list1
            list2_sorted = list2

        # First, check if the lengths are the same
        test_case_instance.assertEqual(len(list1_sorted), len(list2_sorted),
                                       f"List lengths differ: {len(list1_sorted)} vs {len(list2_sorted)}")

        # Iterate through both lists and compare dictionaries individually
        for i, (dict1, dict2) in enumerate(zip(list1_sorted, list2_sorted)):
            try:
                test_case_instance.assertDictEqual(dict1, dict2)
            except AssertionError as e:
                # Re-raise the assertion error with a more specific message
                diff_msg = f"\n\nDictionary at index {i} differs.\n"
                diff_msg += f"Expected:\n{dumps(dict1, indent=2)}\n"
                diff_msg += f"Actual:\n{dumps(dict2, indent=2)}\n"

                # Append the original assertDictEqual message
                diff_msg += f"\nOriginal Error: {e}"

                raise AssertionError(diff_msg)

    def setUp(self):
        self.client = Client()
