from lux.constants import Modules
from lux.views import LuxBaseAPIView


class MangaBaseAPIView(LuxBaseAPIView):

    @property
    def module_name(self) -> str:
        """Module for Manga"""
        return Modules.Manga
