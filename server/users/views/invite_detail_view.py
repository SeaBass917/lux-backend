from rest_framework import status
from rest_framework.request import Request

from lux.views.lux_base_api_view import LuxBaseAPIView, admin_required
from users.models.tokens import InviteToken


class InviteDetailView(LuxBaseAPIView):
    """Manage invites 
    (Note they are all admin-only, and controllable by all admins)
    So after auth, the I/O is simple."""
    
    @admin_required
    def get(self, request: Request, pk: str):
        """Get a specific invite token by ID."""

        try:
            invite = InviteToken.objects.get(id=pk)
        except InviteToken.DoesNotExist:
            return self.respond(
                message="Invite token not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        invite_data = invite.serialize_with_qr_code()
        return self.respond(
            data=invite_data,
            status_code=status.HTTP_200_OK
        )
