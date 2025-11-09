"""This module contains the base test class for the APIs."""
from rest_framework.test import APIClient, APIRequestFactory
from django.test import TestCase
from faker import Faker

from users.models import (
    BearerToken,
    Module,
    Permission,
    PermissionToRole,
    Role,
    User,
)
from users.services.crypto import create_bearer_token

faker = Faker()


class LuxBaseTest(TestCase):
    """Base class for all tests against this API."""

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

        user.save()
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

    def set_permission(self, role: Role, module: str, permission: str, action: str):
        """Set a specified permission for a given role.
        Permissions are specified for a given module, permission, and action.

        Args:
            role (Role): The role to set the permission for.
            module (str): The module name.
            permission (str): The permission name.
            action (str): The action name.

        Returns:
            PermissionToRole: The permission to role object created.
        """
        module_obj = Module.objects.get_or_create(module_name=module)[0]
        permission_obj = Permission.objects.get_or_create(
            permission_name=permission, action=action, module_ref=module_obj
        )[0]
        role_to_permission, _ = PermissionToRole.objects.get_or_create(
            role_ref=role, permission_ref=permission_obj
        )
        return role_to_permission

    def setUp(self):
        # Every test needs access to the request factory.
        self.user = self.create_user()
        self.role = self.create_role(self.app)
        self.factory = APIRequestFactory()
        self.client = APIClient()
