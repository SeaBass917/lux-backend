"""Base Model Used in All Lux tables."""
from django.db import models

from lux.managers import LuxBaseModelManager


class LuxBaseModel(models.Model):
    """Base model for all models in the this database.
    """
    objects = LuxBaseModelManager()
    case_insensitive_fields = []
    untrimmed_fields = []

    def _trim_whitespace(self):
        """
            Trims leading and trailing whitespace from all CharField and TextField fields 
            in the model, except for fields listed in `untrimmed_fields`.

            This function iterates through all fields of the model, checking for instances 
            of `CharField` or `TextField`. If the field is not in the `untrimmed_fields` list, 
            it trims any extra whitespace from the beginning and end of the field's value.
        """
        # Iterate through all fields
        for field in self._meta.fields:
            field_name = field.name
            # Only trim CharFields and TextFields if not in untrimmed_fields
            if isinstance(field, (models.CharField, models.TextField)) and \
                    field_name not in self.untrimmed_fields:
                field_value = getattr(self, field_name)
                if isinstance(field_value, str):  # Make sure the value is a string
                    trimmed_value = field_value.strip()
                    setattr(self, field_name, trimmed_value)

    def _convert_case_insensitive_fields(self):
        """
        Converts the values of specified fields in `case_insensitive_fields` to uppercase.

        This function iterates through the list of fields specified in `case_insensitive_fields` 
        and converts their values to uppercase before saving the model. This ensures that all values 
        in these fields are stored in a consistent, case-insensitive format.
        """
        for field_name in self.case_insensitive_fields:
            field_value = getattr(self, field_name)
            if field_value:
                setattr(self, field_name, field_value.upper())

    class Meta:
        abstract = True
