from rest_framework.permissions import IsAuthenticated

from lux.constants import Modules
from lux.views import LuxBaseAPIView


class VideoBaseAPIView(LuxBaseAPIView):

    @property
    def module_name(self) -> str:
        """Module for Video"""
        return Modules.Video
