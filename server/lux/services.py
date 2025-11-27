"""Utilities used in all applications across this project."""
import re
from django.utils.crypto import get_random_string


def generate_token(length=255):
    """Generate a random string token.

    Args:
        length (int): The length of the token.

    Returns:
        str: The generated token.
    """
    token = get_random_string(length=length)
    return token


def is_uuid_form(uuid_string: str) -> bool:
    """Check if the given string is in UUID format."""
    uuid4hex = re.compile(
        "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I
    )
    match = uuid4hex.match(str(uuid_string))
    return bool(match)
