from django.db import models

from lux.models import LuxBaseModel
from users.models.user import User


class InProgress(LuxBaseModel):
    """Keep track of what a user has in progress. Base Class. """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    """The user this in progress entry belongs to."""

    date_last_viewed = models.DateTimeField(auto_now=True)
    """When did the user last view this content?."""

    class Meta:
        abstract = True
    
    
