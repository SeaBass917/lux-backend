from django.db import models


class ContentLevels(models.IntegerChoices):
    """Each piece of content will be rated with one of these content levels, which determines who can see it.
    """

    EVERYONE = 0, 'Everyone'
    """Content that is appropriate for everyone. This is the default content level."""

    TEENS = 1, 'Teens'
    """Content that is appropriate for teens. 
    This content level is for content that may be inappropriate for children, 
    but is not explicit enough to be considered adult content."""

    ADULTS = 2, 'Adults'
    """Content that is appropriate for adults. 
    This content level is for content that may be inappropriate for teens, 
    but is not explicit enough to be considered pervert content."""

    PERVERTS = 3, 'Perverts'
    """Content that is appropriate for perverts. 
    This content level is for content that is explicit enough to be considered pervert content, 
    and should only be shown to users with the pervert role."""