from rest_framework import status
from rest_framework.request import Request

from lux.views.lux_base_api_view import LuxBaseAPIView, admin_required
from users.models.tokens import InviteToken


class InviteListView(LuxBaseAPIView):
    """Manage invites 
    (Note they are all admin-only, and controllable by all admins)
    So after auth, the I/O is simple."""
    
    @admin_required
    def get(self, request: Request):
        """Get a list of all invite tokens."""

        invites = InviteToken.objects.all()
        invite_data = [invite.serialize() for invite in invites]
        return self.respond(
            data=invite_data,
            status_code=status.HTTP_200_OK
        )

    @admin_required
    def delete(self, request: Request):
        """Delete an invite token.
        
        Request body:
        {
            "invite_token_ids": str[]
        }
        """
        invite_token_strs = request.data.get("invite_token_ids")
        if not invite_token_strs:
            return self.respond(
                message="'invite_tokens' is required in the request body",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        invite_tokens_ids = self.parse_url_list(invite_token_strs)
        invites = InviteToken.objects.filter(id__in=invite_tokens_ids)
        not_found_ids = set(invite_tokens_ids) - set(str(invite.id) for invite in invites)
        if not_found_ids:
            return self.respond(
                message=f"Invite tokens not found: {', '.join(not_found_ids)}",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        invites.delete()

        return self.respond(status_code=status.HTTP_204_NO_CONTENT)