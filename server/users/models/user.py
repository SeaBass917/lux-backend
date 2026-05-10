import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from lux.constants.roles import Roles


class UserManager(BaseUserManager):
    """Custom manager for User model.
    
    Provides get_by_natural_key() for Django's authentication backend.
    """
    
    def get_by_natural_key(self, username):
        """Retrieve a user by their username (natural key)."""
        return self.get(**{self.model.USERNAME_FIELD: username})


class User(AbstractBaseUser):
    """Users of the system.
    They log in, and they have a role that determines their access.

    Uses the built in Django authentication system, giving us:
        - Password hashing
        - Authentication backends
        - User management commands (createsuperuser, etc)

    Attributes:
        id: GUID
        username: The username of the user, used for logging in.
        role: The role of the user, which determines their access.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=64, unique=True)
    role = models.IntegerField(choices=Roles.choices, default=Roles.ADULT)

    objects = UserManager()
    
    USERNAME_FIELD = 'username'

    def save(self, *args, **kwargs):
        """Override the save method to ensure that the model is validated before saving."""
        self.full_clean()  
        super().save(*args, *kwargs)

    def __str__(self) -> str:
        return f"{self.username} ({self.id})"
