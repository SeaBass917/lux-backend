from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed


def custom_exception_handler(exception: Exception, context):
    if isinstance(exception, ObjectDoesNotExist):
        return Response(
            {
                "result": "error",
                "message": "Object not found.",
                "data": {},
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    elif isinstance(exception, MultipleObjectsReturned):
        return Response(
            {
                "result": "error",
                "message": "Multiple objects found when one was expected.",
                "data": {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    elif isinstance(exception, AuthenticationFailed):
        return Response(
            {
                "result": "error",
                "message": "Authentication failed.",
                "data": {},
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Let DRF handle the rest
    response = exception_handler(exception, context)
    return response
