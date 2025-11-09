from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from lux.views.lux_base_api_view import LuxBaseAPIView


@authentication_classes([])
@permission_classes([AllowAny])
class PingAPIView(LuxBaseAPIView):
    """Ping the server to check if it is running."""

    @authentication_classes(SessionAuthentication)
    @permission_classes([AllowAny])
    def get(self, request):
        """Return a response to indicate the server is running.

        Returns:
            200 OK: A response indicating the server is running.
            Else: A response indicating the server is not running.
        """
        return Response({"info": "Hello world"}, status.HTTP_200_OK)
