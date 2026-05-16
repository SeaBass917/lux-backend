from django.db import models

from lux.models import LuxBaseModel


class Person(LuxBaseModel):
    """Rough draft of an idea. Authors and Artists and 
    others involved in a project are People.
    
    TODO: Give everyone a little bio page some day."""

    name = models.CharField(max_length=64)
