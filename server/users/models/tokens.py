import base64
import io
import secrets
import qrcode
from django.db import models
from django.utils import timezone

from lux.constants.roles import Roles
from lux.models.lux_base_model import LuxBaseModel
from lux.settings import SITE_URL
from users.models.user import User

def _generate_token():
    """Generate a random token string and assign it to the token field."""
    return secrets.token_urlsafe(32)  # Generates a 43-character URL-safe token


class TokenModel(LuxBaseModel):
    """Basic idea for tokens that hang out in a DB table, with some common fields."""

    token: str = models.CharField(max_length=64, unique=True, default=_generate_token)
    """The token itself. Should be a random string of sufficient length to be unguessable."""
    
    expires_at = models.DateTimeField()
    """The expiration date and time of the token."""

    role: int = models.IntegerField(choices=Roles.choices)
    """The role associated with the token. 
    Needed in all of our use cases where we are creating tokens.

    e.g. This is an invite for X kind of role. 
    It creates a registration token that makes a user with that role."""
    
    class Meta:
        abstract = True

class InviteToken(TokenModel):
    """Admin-created invite tokens"""
    
    created_by: User = models.ForeignKey(User, on_delete=models.CASCADE)
    """ Who made this token."""

    use_count: int = models.IntegerField(default=0)
    """How many times this token has been used."""

    max_uses: int = models.IntegerField(default=1)
    """How many times this token can be used before it becomes invalid. Default is 1, meaning single-use tokens."""

    @staticmethod
    def validate_and_create_registration_token(invite_token: str) -> 'RegistrationToken':
        """Validate an invite token string and create a registration token if valid.
        
        Raises:
            ValueError: If the invite token is invalid, expired, or has exceeded its max uses.
        """
        try:
            invite = InviteToken.objects.get(token=invite_token)
        except InviteToken.DoesNotExist:
            raise ValueError("Invalid invite token")

        if invite.expires_at < timezone.now():
            raise ValueError("Invite token has expired")

        if invite.max_uses <= invite.use_count:
            raise ValueError("Invite token has exceeded its maximum uses")

        # If valid, increment the use count and create a registration token
        invite.use_count += 1
        invite.save()

        registration_token = RegistrationToken(
            invite_token=invite,
            # If the user has not finished registration in 30 minutes then we time them out.
            expires_at=timezone.now() + timezone.timedelta(minutes=30),
            role=invite.role
        )
        registration_token.save()
        return registration_token

    def serialize(self) -> dict:
        """Basic serializer for this class."""
        return {
            "id" : self.id,
            "server_address": SITE_URL,
            "created_by": self.created_by.username,
            "use_count": self.use_count,
            "max_uses": self.max_uses,
            "expires_at": self.expires_at.isoformat(),
            "role": self.role,
            "invite_token": self.token,
        }

    def serialize_with_qr_code(self) -> dict:
        """Common serialize pattern for this object."""
        data = self.serialize()
        return {
            **data,
            "qr_code": self.get_qr_code_base64()
        }

    def get_qr_code_base64(self) -> str:
        """Generate a QR code for this invite token and return it as a base64 string.
        
        Raises:
            TODO: idk what exceptions this can raise.
        """
        data = self.serialize()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        
        # Save the image to a bytes buffer and encode it as base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        return img_str

class RegistrationToken(TokenModel):
    """Short-lived tokens for completing registration"""
    
    invite_token: InviteToken = models.ForeignKey(InviteToken, on_delete=models.CASCADE)
    """Reference to the invite that created us."""
    
    used: bool = models.BooleanField(default=False)
    """Whether this token has been used to complete registration."""