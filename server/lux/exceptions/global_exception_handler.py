from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def global_exception_handler(exc, context):
    """
    Centralized error handler. Normalizes all API exceptions into a 
    consistent corporate JSON format across the entire application.
    """
    error_message = "An unexpected error occurred."
    error_status = status.HTTP_500_INTERNAL_SERVER_ERROR  # Default to 500 unless we identify a more specific case

    # 1. Let DRF handle its native errors first (like Permissions, Method Not Allowed, or Serializer validation)
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(exc, DRFValidationError):
            # Extract detailed dictionary messages provided by the serializer
            error_message = response.data 
            error_status = status.HTTP_400_BAD_REQUEST
        else:
            error_message = response.data.get("detail", str(exc))
            error_status = response.status_code
        
        response.data = {"message": error_message}
        logger.error("DRF Exception: %s, Path: %s, User: %s",
                     error_message, context['request'].get_full_path(), context['request'].user)
        return response

    # Standard template for our custom API responses

    # 2. Case: Database record not found (ObjectDoesNotExist)
    if isinstance(exc, ObjectDoesNotExist):
        error_message = "The requested database record does not exist."
        error_status = status.HTTP_404_NOT_FOUND

    # 3. Case: Native Django model/field constraint validation failure
    if isinstance(exc, DjangoValidationError):
        error_message = getattr(exc, "message_dict", exc.messages)
        error_status = status.HTTP_400_BAD_REQUEST

    # 5. Case: Unhandled Python crashes (500 Internal Server Errors)
    # Log the full stack trace securely for debugging
    logger.error(f"Unhandled Exception: {str(exc)}, Path: {context['request'].get_full_path()}, User: {context['request'].user}", exc_info=exc)
    return Response({"message": error_message}, status=error_status)
