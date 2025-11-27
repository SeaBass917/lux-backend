"""This module contains the base test class for the APIs."""
from typing import Any
from django.test import TestCase, Client
from faker import Faker
from json import dumps

from metadata.models.person import Person
from users.models import (
    BearerToken,
    Role,
    User,
)
from users.services.crypto import create_bearer_token


class LuxBaseTest(TestCase):
    """Base class for all tests against this API."""

    fixtures = ['000_module.json', '001_permission.json',
                '001_roles.json', '002_roles_to_permissions.json',
                '000_tags.json']

    faker = Faker()
    faker_jp = Faker('ja_JP')

    @staticmethod
    def create_user(bt: BearerToken = None, role: Role = None) -> User:
        """Create a user object in the Users table.
        All details of that user are randomly generated using the faker library.

        Args:
            password (str, optional): The password for the user. Defaults to None

        Returns:
            User: The user object created.
        """
        if bt is None:
            bt = create_bearer_token()

        if role is None:
            role = LuxBaseTest.create_role()

        user = User.objects.create(bearer_token=bt, role=role)
        return user

    @staticmethod
    def create_role(role_name: str = None):
        """Create a role object in the Roles table.

        Args:
            role_name: str
                Override for the name of the role. 
                If left blank a random one will be generated

        Returns:
            Role: The role object created.
        """
        if role_name is None:
            role_name = LuxBaseTest.faker.pystr()

        role = Role.objects.create(role=role_name)
        return role

    @staticmethod
    def create_person(name: str | None = None) -> Person:
        """Create a person.

        Returns:
            Person: The person.
        """
        return Person.objects.create(name=LuxBaseTest.faker.name() if name is None else name)

    @staticmethod
    def create_people(count: int = 3) -> list[Person]:
        """Create a list of people.

        Args:
            count (int, optional): Number of people to make. Defaults to 3.

        Returns:
            list[Person]: The people.
        """
        return Person.objects.bulk_create(
            [Person(name=LuxBaseTest.faker.name()) for _ in range(count)])

    def set_up_user_with_role(self, role: str) -> User:
        """Create a user that has a specific role.
        Set up the client to carry out subsequent calls as that user.

        Returns:
            User: The user object created.

        Raises:
            Role.DoesNotExist: If the specified role does not exist.
        """
        role_obj = Role.objects.get(role=role)
        user = LuxBaseTest.create_user(role=role_obj)
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {user.bearer_token.token}'

    def assertDictListsEqual(test_case_instance, list1: list[dict[str, Any]], list2: list[dict[str, Any]], key_to_sort_by: str = None):
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
