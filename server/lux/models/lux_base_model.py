"""Base Model Used in All Lux tables."""
import uuid

from django.db import models


class LuxBaseModel(models.Model):
    """Base model for all models in this database.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    _untrimmed_fields = []
    """Fields that should not have their whitespace trimmed 
    by our automatic trimming system."""

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
                    field_name not in self._untrimmed_fields:
                field_value = getattr(self, field_name)
                if isinstance(field_value, str):  # Make sure the value is a string
                    trimmed_value = field_value.strip()
                    setattr(self, field_name, trimmed_value)

    def save(self, *args, **kwargs):
        """Override save to enforce validation on every save."""
        self._trim_whitespace()
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
