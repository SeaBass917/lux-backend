from django.db import models

class MangaWebDataSource(models.IntegerChoices):
    """Enumerated choices when gathering metadata from web sources.
    Specifically for manga."""

    WIKIPEDIA = 0, 'Wikipedia'
    MANGA_UPDATES = 1, 'MangaUpdates'
    MAL = 2, 'MAL'
