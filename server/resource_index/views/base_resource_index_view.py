from lux.constants import Modules
from lux.views import LuxBaseAPIView


class ResourceIndexBaseAPIView(LuxBaseAPIView):

    @property
    def module_name(self) -> str:
        """Module for ResourceIndex"""
        return Modules.ResourceIndex
