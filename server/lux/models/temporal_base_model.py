"""Base Model Used in All Lux tables."""
from django.db import models

from lux.models import LuxBaseModel


class TemporalBaseModel(LuxBaseModel):
    """Base model for all models in the this database.

    Attributes:
        created_at (DateTimeField): The date and time the entry was created.
        updated_at (DateTimeField): The date and time the entry was last updated.
        added_by_user (ForeignKey): The user that added the entry (if applicable).
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added_by_user = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    def save(
        self, *args, audit_user=None, **kwargs
    ):
        self._convert_case_insensitive_fields()
        self._trim_whitespace()
        updated_values = {}
        old_values = {}
        creating = self._state.adding is True
        original_values = {f.name: getattr(
            self, f.name) for f in self._meta.local_fields}

        if creating:
            fields = [
                field.name for field in self._meta.fields if getattr(self, field.name)
            ]
        else:
            fields = [
                field.name
                for field in self._meta.fields
                if getattr(self, field.name) != original_values.get(field.name)
            ]
        for field in fields:
            if not creating:
                old_values[field] = original_values.get(field)
            updated_values[field] = getattr(self, field)
        self.added_by_user = audit_user
        super().save(*args, **kwargs)

    def delete(
        self, *args, audit_user=None, **kwargs
    ):
        old_values = {}
        original_values = {f.name: getattr(
            self, f.name) for f in self._meta.local_fields}
        fields = [
            field.name
            for field in self._meta.fields
            if getattr(self, field.name) != original_values.get(field.name)
        ]
        for field in fields:
            old_values[field] = original_values.get(field)
        if audit_user:
            self.added_by_user = audit_user
        super().delete(*args, **kwargs)

    class Meta:
        abstract = True
        get_latest_by = ['created_at']
