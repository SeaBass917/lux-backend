from django.db import models


class Roles(models.IntegerChoices):
    """The different roles a user can have.
    These restrict what level of profile they can access.
    And in the case of admin whether or not they can muck around in the admin settings.
    """

    ADMIN = 0, 'Admin'
    """A user who has access to all content."""

    PERVERT = 1, 'Pervert'
    """A user that has access to all possible content."""

    ADULT = 2, 'Adult'
    """A user that has access to almost all content. But anything explicit will be hidden."""

    CHILD = 3, 'Child'
    """A user that has configurable age restrictions set by a parent."""

    @classmethod
    def from_str(cls, role_str: str) -> int:
        """Convert a role string to a role integer.
        
        Args:
            role_str: The string representation of the role.
        
        Returns:
            The integer representation of the role.
        
        Raises:
            ValueError: If the role string is not valid.
        """
        for role in cls:
            if role.label.lower() == role_str.lower():
                return role.value
        raise ValueError(f"Invalid role string: {role_str}")