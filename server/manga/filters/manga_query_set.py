from django.db import models

from manga.interfaces.manga_list_filter_request import MangaListFilter

class MangaQuerySet(models.QuerySet):
    """Encapsulates all reusable query logic for the Manga table."""
    
    def custom_filter(self, filter_obj: MangaListFilter):
        """Apply custom filters to the manga queryset.
        TODO: Be more creative... this name sucks.

        Args:
            filter_obj (MangaListFilter): The dataclass instance containing the list of filters to apply.

        Returns:
            models.QuerySet: The filtered manga queryset.
        """
        queryset = self

        if filter_obj.title:
            title = filter_obj.title
            title_query = models.Q(title__icontains=title) | models.Q(title_original__icontains=title)
            queryset = queryset.filter(title_query)

        if filter_obj.added_date_start:
            queryset = queryset.filter(date_added__gte=filter_obj.added_date_start)

        if filter_obj.added_date_end:
            queryset = queryset.filter(date_added__lte=filter_obj.added_date_end)

        if filter_obj.in_progress_for_user_id:
            user_id = filter_obj.in_progress_for_user_id
            queryset = queryset.filter(in_progress__user=user_id)

        return queryset