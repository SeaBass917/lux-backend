
from dataclasses import dataclass
from typing import Optional

from users.models.user import User

@dataclass
class MangaListFilter:
    """Individual filter on the various components of a manga."""

    title: Optional[str] = None
    """Filter by title. This is a case-insensitive substring match on both the title and the original title."""

    added_date_start: Optional[str] = None
    """Filter by added date. This is a date string in the format YYYY-MM-DD.
    This will filter for manga that were added to the library on or after this date."""

    added_date_end: Optional[str] = None
    """Filter by added date. This is a date string in the format YYYY-MM-DD.
    This will filter for manga that were added to the library on or before this date."""

    in_progress_for_user_id: Optional[int] = None
    """Filter by in-progress status. This will filter for manga that are currently in progress for the given user."""

@dataclass
class MangaListFilterRequest:
    """Request object for filtering manga list."""

    filters: list[MangaListFilter]
    """Required: List of filters to apply."""
