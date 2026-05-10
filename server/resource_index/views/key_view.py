from django.http import HttpRequest

from lux.views.lux_base_api_view import LuxBaseAPIView


class ResourceIndexSessionKeyAPIView(LuxBaseAPIView):
    """Used to retrieve/generate user session keys."""

    def get(self, request: HttpRequest):
        """Create a new session key for the user, 
        set up the public file access with this key,
        and return the key to the user.

        Args:
            request (HttpRequest): The HTTP request.
                (Only used during auth in the wrapper)

        Returns:
            200 OK: The newly created session key.
            401 Unauthorized: If the user does not have file access permission.
        """

        raise NotImplementedError(
            "ResourceIndexSessionKeyAPIView GET method is not implemented yet.")
