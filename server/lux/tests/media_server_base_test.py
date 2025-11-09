"""This module contains the base test class for the APIs."""
from django.test import TestCase, Client
from faker import Faker

from users.models import (
    BearerToken,
    Role,
    User,
)
from users.services.crypto import create_bearer_token

faker = Faker()


class LuxBaseTest(TestCase):
    """Base class for all tests against this API."""

    fixtures = ['000_module.json', '001_permission.json',
                '001_roles.json', '002_roles_to_permissions.json']

    def create_user(self, bt: BearerToken = None, role: Role = None) -> User:
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
            role = self.create_role()

        user = User.objects.create(bearer_token=bt, role=role)
        return user

    def create_role(self, role_name: str = None):
        """Create a role object in the Roles table.

        Args:
            role_name: str
                Override for the name of the role. 
                If left blank a random one will be generated

        Returns:
            Role: The role object created.
        """
        if role_name is None:
            role_name = faker.pystr()

        role = Role.objects.create(role=role_name)
        return role

    def set_up_user_with_role(self, role: str) -> User:
        """Create a user that has a specific role.
        Set up the client to carry out subsequent calls as that user.

        Returns:
            User: The user object created.

        Raises:
            Role.DoesNotExist: If the specified role does not exist.
        """
        role_obj = Role.objects.get(role=role)
        user = self.create_user(role=role_obj)
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {user.bearer_token.token}'

    def setUp(self):
        self.client = Client()
