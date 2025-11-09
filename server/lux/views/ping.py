from rest_framework import status
from rest_framework.response import Response

from lux.views.lux_base_api_view import LuxBaseAPIView


class PingAPIView(LuxBaseAPIView):
    """Ping the server to check if it is running."""

    def get(self, request):
        """Return a response to indicate the server is running.

        Returns:
            200 OK: A response indicating the server is running.
            Else: A response indicating the server is not running.
        """
        return Response({"info": "Hello world"}, status.HTTP_200_OK)
