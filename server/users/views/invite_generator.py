from rest_framework import status
from rest_framework.request import Request
from django.utils import timezone

from lux.constants.roles import Roles
from lux.views.lux_base_api_view import LuxBaseAPIView, admin_required
from users.models.tokens import InviteToken
from users.models.user import User


class InviteGeneratorView(LuxBaseAPIView):
    """Handle user invitations."""
    
    @admin_required
    def get(self, request: Request):
        """Generate an invite QR code for a new user.
        
        It should include 
        {
            "server_address": "string",
            "invite_token": "string",
            "expires_at": "datetime"
            "role": Roles (int),
        }

        NOTE: we also return the data flat. So client doesn't need to pull the data out.
        We present it both ways.

        Request query parameters:
        - role: The role to assign to the new user as an enum (e.g., 0, 1).
        - (optional) max_uses: The maximum number of times this invite can be used. Default is 1 (single-use).
        - (optional) expires_in_hrs: The number of hours until the invite expires. Default is 7 days.
        """

        # ===================================
        # Phase 1) Parse Args
        # ===================================
        user: User = request.user
        role_str = request.query_params.get("role")
        max_uses_str = request.query_params.get("max_uses")
        expires_in_hrs_str = request.query_params.get("expires_in_hrs")
        if role_str is None:
            return self.respond(
                message="'role' query parameter is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            role = Roles.from_str(role_str)
            max_uses = int(max_uses_str) if max_uses_str is not None else 1
            expires_in_hrs = int(expires_in_hrs_str) if expires_in_hrs_str is not None else 7 * 24

            if max_uses <= 0:
                return self.respond(
                    message="'max_uses' must be a positive integer",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            if expires_in_hrs <= 0:
                return self.respond(
                    message="'expires_in_hrs' must be a positive integer",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        except Exception:
            return self.respond(
                message=f"Invalid role: {role_str}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # ===================================
        # Phase 2) The Token / Data
        # ===================================
        try:
            invite_token = InviteToken(
                created_by=user,
                role=role,
                max_uses=max_uses,
                expires_at=timezone.now() + timezone.timedelta(hours=expires_in_hrs)
            )
            invite_token.save()

            data = invite_token.serialize_with_qr_code()

        except Exception as e:
            return self.respond(
                message=f"Failed to create invite token",
                message_internal=f"Failed to create invite token: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return self.respond(
            data=data,
            status_code=status.HTTP_200_OK
        )


