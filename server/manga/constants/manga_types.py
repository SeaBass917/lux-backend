from django.db import models

class MangaTypes(models.IntegerChoices):
    """Type of manga. This will change how the content is rendered."""

    MANGA = 0, 'Manga'
    """Read Right → Left"""

    WEB_COMIC = 1, 'Web Comic'
    """Reads scrolling infinitely down"""
    
    AMERICAN_COMIC = 2, 'American Comic'
    """Reads Left → Right"""
    
