"""Top level validators used across many models."""
from django.core.validators import RegexValidator

numeric_validator = RegexValidator(
    regex=r'^\d+$',
    message='Number must be numeric')


def numeric_validator_of_length(length: int):
    """Generates a numeric validator of a given length."""
    return RegexValidator(
        regex=rf'^\d{{{length}}}$',
        message=f'Number must be {length} digits long')
