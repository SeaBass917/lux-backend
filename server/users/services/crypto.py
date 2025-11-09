"""This module contains services for the users app."""
from users.models.bearer_token import BearerToken
from users.models.user import User

from lux.services import generate_token


def create_bearer_token(user: User) -> BearerToken:
    """
    Creates a Bearer Token for the User.
    And adds it to the User's Bearer Token.

    Raises:
        IntegrityError: If something unexpected happens.
            And we fail to create the token.
    """
    token = generate_token()
    while BearerToken.objects.filter(token=token).exists():
        token = generate_token()

    return BearerToken.objects.create(user=user, token=token)
