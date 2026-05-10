from django.db import models

from lux.constants.content_levels import ContentLevels
from lux.models import LuxBaseModel


class Profile(LuxBaseModel):
    """Profiles made by users of the system.
    Profiles are shared to anyone with sufficient permissions to view a profile at the content_level_access of the profile.
    Think: 
       - Family where everyone has their own profile. 
       - Kids can't get into parent profiles.
       - Parents can see kid profiles.
    """    
    name = models.CharField(max_length=64)
    """The name shown when selecting a profile. Not necessarily unique, and not used for logging in."""

    is_child_profile = models.BooleanField(default=False)
    """Whether this profile is a child profile. 
    Child Users will only have access to these profiles."""
    
    content_level_access = models.IntegerField(choices=ContentLevels.choices, default=ContentLevels.ADULTS)
    """The content level access of the user.
    This determines what content the user can see."""

    # More to come: 
    # - Profile picture
    # - Colors

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"
