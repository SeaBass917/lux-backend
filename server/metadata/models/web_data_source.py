from django.db import models

from lux.models import LuxBaseModel


class WebDataSource(LuxBaseModel):
    """Lookup table of known data sources that we scrape from."""

    name = models.CharField(max_length=32)
