import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken

from lux.views.lux_base_api_view import LuxBaseAPIView
from users.models import User
from users.models.tokens import RegistrationToken

logger = logging.getLogger()


class RegisterView(LuxBaseAPIView):
    """Handle user registration."""
    
    # "Public" endpoint. But they do need the token we sent them.
    permission_classes = [AllowAny]  
    
    def post(self, request: Request):
        """Create a new user account.
        
        Request header:
            X-Registration-Token: string
                The token the user was given after accepting an invite.

        Request body:
            {
                "username": "string",
                "password": "string",
            }
            
        Returns:
            {
                "result": "success",
                "message": "User created successfully",
                "data": {
                    "access": "jwt_access_token",
                    "refresh": "jwt_refresh_token",
                    "user": {
                        "id": "uuid",
                        "username": "string",
                        "role": int
                    }
                }
            }
        """
        # ==================================
        # Phase 1) Parse Args
        # ==================================
        username = request.data.get('username')
        password = request.data.get('password')
        registration_token = request.headers.get('X-Registration-Token')
        if not registration_token:
            return self.respond(
                message="Registration token required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        if not username or not password:
            return self.respond(
                message="Username and password are required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # ==================================
        # Phase 2) Validation 
        # ==================================
        # Validate the registration token
        try:
            reg_token = RegistrationToken.objects.get(
                token=registration_token,
                used=False,
                expires_at__gt=timezone.now()
            )
        except RegistrationToken.DoesNotExist:
            return self.respond(
                message="Invalid or expired registration token",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return self.respond(
                message="Username already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # ==================================
        # Phase 3) Creation 
        # ==================================
        user = User(username=username, role=reg_token.role)
        user.set_password(password)
        
        try:
            user.save()
        except Exception as e:
            return self.respond(
                message=f"Failed to create user: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reg_token.used = True
            reg_token.save()
        except Exception as e:
            logger.error(
                f"Failed to mark registration token as used: {str(e)}"
            )
        
        # Generate JWT tokens for auto-login
        refresh = RefreshToken.for_user(user)
        
        return self.respond(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "role": user.role
                }
            },
            status_code=status.HTTP_201_CREATED
        )
