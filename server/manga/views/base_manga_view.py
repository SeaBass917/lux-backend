from rest_framework.permissions import IsAuthenticated

from lux.constants import Modules
from lux.views import LuxBaseAPIView


class MangaBaseAPIView(LuxBaseAPIView):
    permission_classes = [IsAuthenticated]
    __module = Modules.Manga
