from django.db import models
from manga.models.manga import Manga
from users.models.in_progress import InProgress


class MangaInProgress(InProgress):
    """Keep track of what manga a user has in progress."""
    
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name="in_progress")
    """The manga this in progress entry belongs to."""