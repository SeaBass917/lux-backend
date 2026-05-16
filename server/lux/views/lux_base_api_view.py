"""Base class View for all views in the project."""
from dataclasses import fields
import functools
import json
import logging
from urllib import parse as url_parse
from typing import Callable
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import JsonResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from lux.constants.roles import Roles

logger = logging.getLogger()


def admin_required(view: Callable):
    """Decorator to restrict view access to admin users only.
    
    Args:
        view: The view function to wrap.
        
    Returns:
        The wrapped view function.
    """
    @functools.wraps(view)
    def wrapper(self: "LuxBaseAPIView", request: Request, *args, **kwargs):
        if request.user.role != Roles.ADMIN:
            return Response(
                {"result": "error", "message": "Admin access required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return view(self, request=request, *args, **kwargs)
    
    return wrapper


def enforce_interface(dataclass_cls):
    """Decorator to enforce that the request body matches a given dataclass interface."""
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(view_instance, request, *args, **kwargs):
            # DRF has already parsed the JSON into request.data!
            payload = request.data or {}
            
            missing_fields = []
            validated_data = {}

            # Inspect the dataclass fields
            for field in fields(dataclass_cls):
                if field.name in payload:
                    validated_data[field.name] = payload[field.name]
                # If field is missing and has no default value, it is required
                elif field.default == field.default_factory:
                    missing_fields.append(field.name)

            if missing_fields:
                return Response(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Convert payload into the strict dataclass instance
            interface_instance = dataclass_cls(**validated_data)
            
            # Pass the dataclass instance into the view function
            return view_func(view_instance, request, interface_instance, *args, **kwargs)
        return _wrapped_view
    return decorator

class LuxBaseAPIView(APIView):
    """Base class for API views.
    
    Provides:
    - Exception handling for common Django model errors
    - Consistent response format via respond()
    - URL parsing utilities
    
    Authentication is handled by DRF + JWT (configured in settings.py).
    Use @admin_required decorator to restrict views to admins only.
    """

    _default_response_messages = {
        # Good messages don't need to explain themselves.
        status.HTTP_200_OK: "",
        status.HTTP_201_CREATED: "",
        status.HTTP_204_NO_CONTENT: "",
        status.HTTP_207_MULTI_STATUS: "",

        # Ideally our system has more specific error messages, 
        # but these can be here as a fall-back 
        # if nothing explicit can be said about what went wrong.
        status.HTTP_400_BAD_REQUEST: "Bad request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden",
        status.HTTP_404_NOT_FOUND: "Not found",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal server error",
    }

    def dispatch(self, request: Request, *args, **kwargs):
        """Override dispatch to catch common Django model exceptions.

        Args:
            request: The HTTP request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The HTTP response.
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        except ObjectDoesNotExist as e:
            logger.error("Object not found: %s, Path: %s, User: %s",
                         str(e), request.get_full_path(), request.user)
            response = self.respond(
                message=f"Object not found: {str(e)}",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except MultipleObjectsReturned as e:
            logger.error("Multiple objects found: %s, Path: %s, User: %s", 
                        str(e), request.get_full_path(), request.user)
            response = self.respond(
                message="Multiple objects found when one was expected.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error("Unhandled exception: %s, Path: %s, User: %s",
                         str(e), request.get_full_path(), request.user)
            response = self.respond(
                message="An unexpected error occurred.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return self.finalize_response(request, response, *args, **kwargs)

    def respond(self, status_code: status, data=None, message: str = None, message_internal: str = None) -> Response:
        """Utility function to create a consistent response format.

        Args:
            status_code (int): The HTTP status code.
            message (str): [OPTIONAL] The message describing the result, 
                            usually only overwritten to help describe an error to the caller.
                            If not provided, the message will be a pre-defined default from our table above.
            message_internal (str): [OPTIONAL] The internal message for the server logs.
            data (dict): [OPTIONAL] Data to include in the response.
                            If not provided, defaults to an empty dict.

        Returns:
            Response: The formatted response object.
        """
        if data is None:
            data = {}

        if message is None:
            # Default to empty string if status code not in table
            message = self._default_response_messages.get(status_code, "")

        # Don't even let anyone do anything weird.
        if status_code == status.HTTP_204_NO_CONTENT:
            data = {}
            message = ""

        # Log errors with internal message if provided, otherwise use the external message
        if 400 <= status_code:
            logger.error(
                "[API ERROR] Response: %s, Path: %s, User: %s",
                message_internal or message,
                self.request.get_full_path(),
                self.request.user,
            )

        return Response(
            {
                "message": message,
                "data": data,
            },
            status=status_code,
        )

    def parse_url_list(self, input_string: str) -> list[str] | None:
        """Parse a comma-separated URL parameter into a list of strings.
        
        Handles URL decoding of special characters.

        Args:
            input_string (str): The comma-separated string from URL params.
            
        Returns:
            list[str] | None: The parsed list, or None if input is empty.
        """
        return [url_parse.unquote(s) for s in input_string.split(',')] if input_string else None
