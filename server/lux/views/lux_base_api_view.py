"""Base class View for all views in the project."""
import abc
import functools
import logging
from urllib import parse as url_parse
from typing import Callable
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpRequest
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from lux.constants import Actions

from users.models import (
    BearerToken,
    PermissionToRole,
    User,
)

logger = logging.getLogger()


def permission_required(permission: str):
    """Function factory to create a decorator for checking permissions.
    See `check_permission` for more details.
    Returns 404 NOT FOUND: If the permission does not exist.

    Args:
        permission (str): The permission name.

    Returns:
        function: The decorator function.
    """

    def decorator(view: Callable):
        @functools.wraps(view)
        def wrapper(self: LuxBaseAPIView, request: HttpRequest, *args, **kwargs):
            action = Actions.lookup(view.__name__)
            if self.check_permission(
                request, permission=permission, module=self.module_name, action=action
            ):
                return view(self, request=request, *args, **kwargs)

            return Response(
                {"result": "error", "message": "Permission Denied"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return wrapper

    return decorator


class LuxBaseAPIView(APIView):
    """Base class for API views."""

    permission_classes = [AllowAny]

    @property
    @abc.abstractmethod
    def module_name(self) -> str:
        """Subclasses must provide a 'module_name' string value."""
        pass

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        """Override dispatch to catch common Django model exceptions.

        Args:
            request: The HTTP request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The HTTP response.
        """
        self.headers = {}
        path = None
        user = None
        try:
            path = request.get_full_path()
            user = self.__get_user(request)
            return super().dispatch(request, *args, **kwargs)
        except ObjectDoesNotExist as e:
            logger.error("Object not found: %s, Path: %s, User: %s",
                         str(e), path, user)
            response = self.respond(
                result="error",
                message=f"Object not found: {str(e)}",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except MultipleObjectsReturned as e:
            logger.error(
                "Multiple objects found: %s, Path: %s, User: %s", str(e), path, user)
            response = self.respond(
                result="error",
                message="Multiple objects found when one was expected.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except AuthenticationFailed as e:
            logger.error("Authentication failed: %s, Path: %s", str(e), path)
            response = self.respond(
                result="error",
                message="Authentication failed.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            logger.error("Unhandled exception: %s, Path: %s, User: %s",
                         str(e), path, user)
            response = self.respond(
                result="error",
                message="An unexpected error occurred.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return self.finalize_response(request, response, *args, **kwargs)

    def respond(self, result: str, message: str, data=None, status_code=None) -> Response:
        """Utility function to create a response object.

        Args:
            result (str): The result of the response.
            message (str): The message of the response.
            data (dict): The data to be included in the response.
            status_code (int): The status code of the response.

        Returns:
            Response: The response object.
        """
        if data is None:
            data = {}

        return Response(
            {
                "result": result,
                "message": message,
                "data": data,
            },
            status=status_code,
        )

    def check_permission(self, request: HttpRequest, module: str = None, permission: str = None, action: str = None) -> bool:
        """Check if the user has the required permission.
        Intended to be used as a decorator.
        e.g. @check_permission('module', 'permission', 'action')

        Args:
            request (Request): The request object.
            permission (str): The permission name.
            module (str): The module name.
            action (str): The action name.

        Returns:
            bool: True if the user has the permission, else False.
        """
        user = self.__get_user(request)

        if not user:
            logger.warning("Null user sending requests.")
            return

        # Validate permission
        role_has_permission = PermissionToRole.objects.filter(
            permission_ref__module_ref__module_name=module,
            permission_ref__action=action,
            permission_ref__permission_name=permission,
            role_ref=user.role
        ).exists()

        if role_has_permission:
            logger.info("Access granted for user %s to %s %s with permission %s",
                        user, action, module, permission)
            return True
        else:
            logger.warning(
                "User %s does not have permission (%s, %s, %s)",
                user, module, permission, action)
            return False

    def parse_url_list(self, input_string: str) -> list[str] | None:
        """Utility that splits a comma-separated string into a list of strings.
        translates URL-encoded characters.

        Args:
            input_string (str): The comma-separated string.
        Returns:
            list[str]: The list of strings.
        """
        return [url_parse.unquote(s) for s in input_string.split(',')] if input_string else None

    def __get_user(self, request: HttpRequest) -> User:
        """Get the user for the request.
        Args:
            request (Request): The request object.
        Returns:
            User: The user object.
        """
        return self.__authenticate(request)

    def __authenticate(self, request: HttpRequest) -> User:
        """
        Just supports BearerToken

        Args:
            request (Request): The request object.

        Returns:
            tuple: A tuple containing the authenticated user and token.
        """

        # Look for the token in the cookies
        auth_component = request.headers.get('Authorization')
        if auth_component is None:
            raise AuthenticationFailed('Invalid token type')

        try:
            scheme, token = auth_component.split(' ')
            if scheme.lower() != 'bearer':
                raise Exception("Invalid bearer token.")
            user = getattr(BearerToken.objects.get(token=token), 'user')

        except BearerToken.DoesNotExist as e:
            raise AuthenticationFailed('Token not found.') from e

        except Exception as e:
            # Log error and raise authentication failure
            logger.error("Error during authentication: %s", str(e))
            raise AuthenticationFailed(
                'Invalid token or user not found') from e

        return user
