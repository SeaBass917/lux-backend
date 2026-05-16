from django.db import models

from lux.constants.content_levels import ContentLevels
from lux.models import LuxBaseModel
from metadata.models import Tags


class MetadataBase(LuxBaseModel):
    """Base class for all content models' metadata.

    For things we want to enforce on all media, regardless of type.
    e.g. Everything should have a name, a content rating, etc.
    
    We can also enforce things we'd _like_ everything to have.
    e.g. A description, an original title, etc. 
    But these can be null, because we might not know them at the time of adding the content."""

    title = models.CharField(max_length=255)
    """What is the content called?"""

    title_original = models.CharField(max_length=255, null=True, blank=True)
    """If the content was translated, what was the original title? NULL => Not applicable or not known."""

    description = models.CharField(max_length=4096, null=True, blank=True)
    """A brief description of the content. NULL => Not applicable or not known."""

    tags = models.ManyToManyField(Tags)
    """Tags associated with this content."""

    content_level = models.IntegerField(ContentLevels, default=ContentLevels.PERVERTS)
    """The content level of this content. This will determine how the content is rendered and who can see it.
    Default to the highest. Assume the worst until we know otherwise."""

    date_added = models.DateField()
    """Required field: The date this content was added to the library."""
    
    visited_sources = models.JSONField(default=list)
    """List of keys associated with web data sources. This lets us flag places we already went to to gather metadata."""

    class Meta:
        abstract = True

    def __str__(self):
        return f"({self.id}) \"{self.title}\""
