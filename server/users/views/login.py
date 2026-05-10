from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken

from lux.views.lux_base_api_view import LuxBaseAPIView
from users.models.user import User


class LoginView(LuxBaseAPIView):
    """Handle user login and JWT token generation."""
    
    # Public endpoint, because this is the door to come in.
    permission_classes = [AllowAny]  
    
    def post(self, request: Request):
        """Authenticate user and return JWT tokens.
        
        Request body:
            {
                "username": "string",
                "password": "string"
            }
            
        Returns:
            {
                "result": "success",
                "message": "Login successful",
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
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            message = ""
            if not username:
                message += "Username"
            if not password:
                if message:
                    message += " and "
                message += "Password"

            return self.respond(
                message=f"{message} required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Authenticate user credentials and return the user object if valid
        user : User | None = authenticate(username=username, password=password)
        if user is None:
            return self.respond(
                message="Invalid credentials",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
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
            status_code=status.HTTP_200_OK
        )