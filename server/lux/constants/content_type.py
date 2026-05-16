from django.db import models


class ContentType(models.IntegerChoices):
    """Enumerate each type of content. e.g. Manga, Video, etc...
    """

    MANGA = 0, 'Manga'
    """Manga, web comics, manhwa, manhua, etc..."""

    VIDEO = 1, 'Video'
    """Videos, movies, TV shows, etc..."""

    MUSIC = 2, 'Music'
    """Songs, sounds we like, etc..."""

    

