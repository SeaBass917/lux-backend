from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from lux.views.lux_base_api_view import LuxBaseAPIView
from users.models.tokens import InviteToken


class InviteAcceptView(LuxBaseAPIView):
    """Accepting an invite with a token."""
    
    permission_classes = [AllowAny]
    
    def post(self, request: Request):
        """Accept an invite using a token.
        
        Request header:
            X-Invite-Token: string
                The token the user was given after accepting an invite.

        Returns:
            {
                "data": {
                    "registration_token": "string"
                },
            }
        """

        invite_token = request.headers.get('X-Invite-Token')
        if not invite_token:
            return self.respond(
                message="Invite token required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate the invite token and create a registration token
        try:
            registration_token = InviteToken.validate_and_create_registration_token(invite_token)
        except ValueError as e:
            return self.respond(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return self.respond(
            data={"registration_token": registration_token.token},
            status_code=status.HTTP_200_OK
        )
