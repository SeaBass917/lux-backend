"""Test cases for the user invite and registration flow."""
from datetime import timedelta
from django.test import Client
from django.utils import timezone
from rest_framework import status

from lux.constants.roles import Roles
from lux.tests.media_server_base_test import LuxBaseTest
from users.models import User
from users.models.tokens import InviteToken, RegistrationToken


class UserInviteFlowTest(LuxBaseTest):
    """Test the complete user invite and registration flow."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.client = Client()
        
        # Create an admin user for testing admin endpoints
        self.admin_user = User(
            username="admin_user",
            role=Roles.ADMIN
        )
        self.admin_user.set_password("admin_password")
        self.admin_user.save()
        
        # Create a non-admin user for testing permission restrictions
        self.regular_user = User(
            username="regular_user",
            role=Roles.ADULT
        )
        self.regular_user.set_password("regular_password")
        self.regular_user.save()
        
    def _get_admin_token(self):
        """Helper to get JWT token for admin user."""
        response = self.client.post('/api/v1/users/login/', {
            'username': 'admin_user',
            'password': 'admin_password'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                        f"Admin login failed: {response.json()}")
        return response.json()['data']['access']
    
    def _get_regular_user_token(self):
        """Helper to get JWT token for regular user."""
        response = self.client.post('/api/v1/users/login/', {
            'username': 'regular_user',
            'password': 'regular_password'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                        f"Regular user login failed: {response.json()}")
        return response.json()['data']['access']


class AdminProtectionTest(UserInviteFlowTest):
    """Test that admin-only endpoints are properly protected."""
    
    def test_invite_generator_requires_admin(self):
        """Non-admin users cannot generate invites."""
        token = self._get_regular_user_token()
        response = self.client.get(
            '/api/v1/users/invite/generate/?role=adult',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                        f"Non-admin should be forbidden from generating invites: {response.json()}")
        self.assertIn('admin', response.json()['message'].lower(),
                     "Error message should mention admin requirement")
    
    def test_invite_generator_requires_authentication(self):
        """Unauthenticated requests cannot generate invites."""
        response = self.client.get('/api/v1/users/invite/generate/?role=adult')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                        f"Unauthenticated request should be unauthorized: {response.json()}")
    
    def test_invite_list_requires_admin(self):
        """Non-admin users cannot list invites."""
        token = self._get_regular_user_token()
        response = self.client.get(
            '/api/v1/users/invites/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                        f"Non-admin should be forbidden from listing invites: {response.json()}")


class InviteCreationTest(UserInviteFlowTest):
    """Test invite token creation by admins."""
    
    def test_admin_can_create_invite(self):
        """Admin can successfully create an invite token."""
        token = self._get_admin_token()
        response = self.client.get(
            '/api/v1/users/invite/generate/?role=adult',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                        f"Admin should successfully create invite: {response.json()}")
        data = response.json()['data']
        
        # Verify response contains required fields
        self.assertIn('invite_token', data, "Response should include invite_token")
        self.assertIn('qr_code', data, "Response should include QR code")
        self.assertIn('expires_at', data, "Response should include expiration")
        self.assertIn('role', data, "Response should include role")
        self.assertEqual(data['role'], Roles.ADULT,
                        f"Invite role should be ADULT, got {data['role']}")
    
    def test_invite_creation_with_different_roles(self):
        """Invite tokens can be created for different roles."""
        token = self._get_admin_token()
        
        for role_name, role_value in [('admin', Roles.ADMIN), ('pervert', Roles.PERVERT), 
                                       ('adult', Roles.ADULT), ('child', Roles.CHILD)]:
            response = self.client.get(
                f'/api/v1/users/invite/generate/?role={role_name}',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                            f"Failed to create invite for role {role_name}: {response.json()}")
            data = response.json()['data']
            self.assertEqual(data['role'], role_value,
                            f"Invite should have role {role_value}, got {data['role']}")
    
    def test_invite_creation_persists_to_database(self):
        """Created invite tokens are stored in the database."""
        initial_count = InviteToken.objects.count()
        
        token = self._get_admin_token()
        response = self.client.get(
            '/api/v1/users/invite/generate/?role=adult',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                        f"Failed to create invite: {response.json()}")
        self.assertEqual(InviteToken.objects.count(), initial_count + 1,
                        "Database should have one more invite token")
        
        invite_token = response.json()['data']['invite_token']
        invite = InviteToken.objects.get(token=invite_token)
        
        self.assertEqual(invite.role, Roles.ADULT,
                        f"Invite role should be ADULT, got {invite.role}")
        self.assertEqual(invite.created_by, self.admin_user,
                        "Invite should be created by admin user")
        self.assertEqual(invite.use_count, 0,
                        "New invite should have use_count of 0")
        self.assertEqual(invite.max_uses, 1,
                        "Default max_uses should be 1")
    
    def test_invite_creation_requires_role_parameter(self):
        """Invite creation fails without role parameter."""
        token = self._get_admin_token()
        response = self.client.get(
            '/api/v1/users/invite/generate/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Missing role parameter should return 400: {response.json()}")
        self.assertIn('role', response.json()['message'].lower(),
                     "Error message should mention missing role parameter")
    
    def test_invite_creation_rejects_invalid_role(self):
        """Invite creation fails with invalid role."""
        token = self._get_admin_token()
        response = self.client.get(
            '/api/v1/users/invite/generate/?role=invalid_role',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Invalid role should return 400: {response.json()}")


class InviteAcceptanceTest(UserInviteFlowTest):
    """Test invite acceptance and registration token creation."""
    
    def test_valid_invite_creates_registration_token(self):
        """Valid invite token creates a registration token."""
        # Create an invite
        invite = InviteToken(
            created_by=self.admin_user,
            role=Roles.ADULT,
            expires_at=timezone.now() + timedelta(days=7)
        )
        invite.save()
        
        # Accept the invite
        response = self.client.post(
            '/api/v1/users/invite/accept/',
            {},
            HTTP_X_INVITE_TOKEN=invite.token
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                        f"Valid invite should be accepted: {response.json()}")
        data = response.json()['data']
        
        self.assertIn('registration_token', data, "Response should include registration_token")
        
        # Verify registration token was created
        reg_token = RegistrationToken.objects.get(token=data['registration_token'])
        self.assertEqual(reg_token.role, Roles.ADULT,
                        "Database registration token should have ADULT role")
        self.assertFalse(reg_token.used,
                        "New registration token should not be marked as used")
        self.assertEqual(reg_token.invite_token, invite,
                        "Registration token should reference the invite token")
    
    def test_expired_invite_rejected(self):
        """Expired invite tokens cannot be accepted."""
        # Create an expired invite
        invite = InviteToken(
            created_by=self.admin_user,
            role=Roles.ADULT,
            expires_at=timezone.now() - timedelta(hours=1)
        )
        invite.save()
        
        response = self.client.post(
            '/api/v1/users/invite/accept/',
            {},
            HTTP_X_INVITE_TOKEN=invite.token
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Expired invite should be rejected: {response.json()}")
        self.assertIn('expired', response.json()['message'].lower(),
                     "Error message should mention expiration")
    
    def test_invite_max_uses_enforced(self):
        """Invite cannot be used more than max_uses times."""
        # Create an invite with max_uses=2
        invite = InviteToken(
            created_by=self.admin_user,
            role=Roles.ADULT,
            expires_at=timezone.now() + timedelta(days=7),
            max_uses=2
        )
        invite.save()
        
        # Use it twice (should work)
        for i in range(2):
            response = self.client.post(
                '/api/v1/users/invite/accept/',
                {},
                HTTP_X_INVITE_TOKEN=invite.token
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK, 
                           f"Use {i+1} should succeed")
        
        # Verify use_count was incremented
        invite.refresh_from_db()
        self.assertEqual(invite.use_count, 2,
                        f"Invite use_count should be 2, got {invite.use_count}")
        
        # Third attempt should fail
        response = self.client.post(
            '/api/v1/users/invite/accept/',
            {},
            HTTP_X_INVITE_TOKEN=invite.token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Third use should exceed max_uses and fail: {response.json()}")
        self.assertIn('maximum', response.json()['message'].lower(),
                     "Error message should mention maximum uses")
    
    def test_invalid_invite_token_rejected(self):
        """Invalid invite tokens are rejected."""
        response = self.client.post(
            '/api/v1/users/invite/accept/',
            {},
            HTTP_X_INVITE_TOKEN='invalid_token_12345'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Invalid token should be rejected: {response.json()}")
        self.assertIn('invalid', response.json()['message'].lower(),
                     "Error message should mention invalid token")
    
    def test_missing_invite_token_rejected(self):
        """Request without invite token is rejected."""
        response = self.client.post('/api/v1/users/invite/accept/', {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Missing invite_token should return 400: {response.json()}")


class UserRegistrationTest(UserInviteFlowTest):
    """Test user registration with registration tokens."""
    
    def test_valid_registration_token_creates_user(self):
        """Valid registration token allows user creation."""
        # Create invite and get registration token
        invite = InviteToken(
            created_by=self.admin_user,
            role=Roles.PERVERT,
            expires_at=timezone.now() + timedelta(days=7)
        )
        invite.save()
        
        accept_response = self.client.post(
            '/api/v1/users/invite/accept/',
            {},
            HTTP_X_INVITE_TOKEN=invite.token
        )
        reg_token = accept_response.json()['data']['registration_token']
        
        # Register user
        response = self.client.post(
            '/api/v1/users/register/',
            {
                'username': 'new_user',
                'password': 'SecurePassword123'
            },
            HTTP_X_REGISTRATION_TOKEN=reg_token
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                        f"Valid registration should succeed: {response.json()}")
        data = response.json()['data']
        
        # Verify JWT tokens returned
        self.assertIn('access', data, "Response should include access token")
        self.assertIn('refresh', data, "Response should include refresh token")
        self.assertIn('user', data, "Response should include user data")
        self.assertEqual(data['user']['username'], 'new_user',
                        f"Username should be 'new_user', got {data['user']['username']}")
        self.assertEqual(data['user']['role'], Roles.PERVERT,
                        f"User role should be PERVERT, got {data['user']['role']}")
        
        # Verify user created in database
        user = User.objects.get(username='new_user')
        self.assertEqual(user.role, Roles.PERVERT,
                        f"Database user role should be PERVERT, got {user.role}")
        
        # Verify registration token marked as used
        reg_token_obj = RegistrationToken.objects.get(token=reg_token)
        self.assertTrue(reg_token_obj.used,
                       "Registration token should be marked as used")
    
    def test_registration_token_single_use(self):
        """Registration token can only be used once."""
        # Create and accept invite
        invite = InviteToken(
            created_by=self.admin_user,
            role=Roles.ADULT,
            expires_at=timezone.now() + timedelta(days=7)
        )
        invite.save()
        
        accept_response = self.client.post(
            '/api/v1/users/invite/accept/',
            {},
            HTTP_X_INVITE_TOKEN=invite.token
        )
        reg_token = accept_response.json()['data']['registration_token']
        
        # First registration succeeds
        response = self.client.post(
            '/api/v1/users/register/',
            {
                'username': 'user_one',
                'password': 'Password123'
            },
            HTTP_X_REGISTRATION_TOKEN=reg_token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                        f"First registration should succeed: {response.json()}")
        
        # Second registration with same token fails
        response = self.client.post(
            '/api/v1/users/register/',
            {
                'username': 'user_two',
                'password': 'Password456'
            },
            HTTP_X_REGISTRATION_TOKEN=reg_token
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                        f"Second use of token should fail: {response.json()}")
        self.assertIn('invalid', response.json()['message'].lower(),
                     "Error message should mention invalid token")
    
    def test_expired_registration_token_rejected(self):
        """Expired registration token cannot be used."""
        # Create a registration token that's already expired
        invite = InviteToken(
            created_by=self.admin_user,
            role=Roles.ADULT,
            expires_at=timezone.now() + timedelta(days=7)
        )
        invite.save()
        
        reg_token = RegistrationToken(
            invite_token=invite,
            role=Roles.ADULT,
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        reg_token.save()

        response = self.client.post(
            '/api/v1/users/register/',
            {
                'username': 'test_user',
                'password': 'Password123'
            },
            HTTP_X_REGISTRATION_TOKEN=reg_token.token
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                        f"Expired registration token should be rejected: {response.json()}")
        self.assertIn('expired', response.json()['message'].lower(),
                     "Error message should mention expiration")
    
    def test_registration_without_token_rejected(self):
        """Registration without registration token is rejected."""
        response = self.client.post('/api/v1/users/register/', {
            'username': 'test_user',
            'password': 'Password123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                        f"Registration without token should be rejected: {response.json()}")
        self.assertIn('token', response.json()['message'].lower(),
                     "Error message should mention missing token")
    
    def test_registration_with_invalid_token_rejected(self):
        """Registration with invalid token is rejected."""
        response = self.client.post(
            '/api/v1/users/register/',
            {
                'username': 'test_user',
                'password': 'Password123'
            },
            HTTP_X_REGISTRATION_TOKEN='invalid_token_xyz'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                        f"Invalid token should be rejected: {response.json()}")
    
    def test_registration_duplicate_username_rejected(self):
        """Registration with existing username is rejected."""
        # Create invite and get registration token
        invite = InviteToken(
            created_by=self.admin_user,
            role=Roles.ADULT,
            expires_at=timezone.now() + timedelta(days=7)
        )
        invite.save()
        
        accept_response = self.client.post(
            '/api/v1/users/invite/accept/',
            {},
            HTTP_X_INVITE_TOKEN=invite.token
        )
        reg_token = accept_response.json()['data']['registration_token']
        
        # Try to register with existing username
        response = self.client.post(
            '/api/v1/users/register/',
            {
                'username': 'admin_user',  # Already exists
                'password': 'Password123'
            },
            HTTP_X_REGISTRATION_TOKEN=reg_token
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Duplicate username should be rejected: {response.json()}")
        self.assertIn('username', response.json()['message'].lower(),
                     "Error message should mention username conflict")
    
    def test_registration_missing_fields_rejected(self):
        """Registration without required fields is rejected."""
        invite = InviteToken(
            created_by=self.admin_user,
            role=Roles.ADULT,
            expires_at=timezone.now() + timedelta(days=7)
        )
        invite.save()
        
        accept_response = self.client.post(
            '/api/v1/users/invite/accept/',
            {},
            HTTP_X_INVITE_TOKEN=invite.token
        )
        reg_token = accept_response.json()['data']['registration_token']
        
        # Missing password
        response = self.client.post(
            '/api/v1/users/register/',
            {'username': 'test_user'},
            HTTP_X_REGISTRATION_TOKEN=reg_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Missing password should return 400: {response.json()}")
        
        # Missing username
        response = self.client.post(
            '/api/v1/users/register/',
            {'password': 'Password123'},
            HTTP_X_REGISTRATION_TOKEN=reg_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Missing username should return 400: {response.json()}")


class UserLoginTest(UserInviteFlowTest):
    """Test user login functionality."""
    
    def test_valid_credentials_return_jwt_tokens(self):
        """Valid credentials return JWT access and refresh tokens."""
        response = self.client.post('/api/v1/users/login/', {
            'username': 'admin_user',
            'password': 'admin_password'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                        f"Valid login should succeed: {response.json()}")
        data = response.json()['data']
        
        self.assertIn('access', data, "Response should include access token")
        self.assertIn('refresh', data, "Response should include refresh token")
        self.assertIn('user', data, "Response should include user data")
        self.assertEqual(data['user']['username'], 'admin_user',
                        f"Username should be 'admin_user', got {data['user']['username']}")
        self.assertEqual(data['user']['role'], Roles.ADMIN,
                        f"User role should be ADMIN, got {data['user']['role']}")
    
    def test_invalid_password_rejected(self):
        """Invalid password is rejected."""
        response = self.client.post('/api/v1/users/login/', {
            'username': 'admin_user',
            'password': 'wrong_password'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                        f"Invalid password should be rejected: {response.json()}")
        self.assertIn('invalid', response.json()['message'].lower(),
                     "Error message should mention invalid credentials")
    
    def test_nonexistent_user_rejected(self):
        """Nonexistent username is rejected."""
        response = self.client.post('/api/v1/users/login/', {
            'username': 'nonexistent_user',
            'password': 'some_password'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                        f"Nonexistent user should be rejected: {response.json()}")
    
    def test_missing_credentials_rejected(self):
        """Login without credentials is rejected."""
        # Missing password
        response = self.client.post('/api/v1/users/login/', {
            'username': 'admin_user'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Missing password should return 400: {response.json()}")
        
        # Missing username
        response = self.client.post('/api/v1/users/login/', {
            'password': 'admin_password'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        f"Missing username should return 400: {response.json()}")
    
    def test_jwt_token_grants_access(self):
        """JWT token allows access to authenticated endpoints."""
        # Login
        login_response = self.client.post('/api/v1/users/login/', {
            'username': 'admin_user',
            'password': 'admin_password'
        })
        token = login_response.json()['data']['access']
        
        # Use token to access protected endpoint
        response = self.client.get(
            '/api/v1/users/invites/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        # Should succeed (not 401)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                           f"JWT token should grant access to authenticated endpoint: {response.json()}")


class CompleteFlowIntegrationTest(UserInviteFlowTest):
    """Test the complete end-to-end flow."""
    
    def test_complete_user_onboarding_flow(self):
        """Test the entire flow from invite creation to login."""
        # Step 1: Admin creates invite
        admin_token = self._get_admin_token()
        invite_response = self.client.get(
            '/api/v1/users/invite/generate/?role=pervert',
            HTTP_AUTHORIZATION=f'Bearer {admin_token}'
        )
        self.assertEqual(invite_response.status_code, status.HTTP_200_OK,
                        f"Step 1: Admin should create invite successfully: {invite_response.json()}")
        invite_token = invite_response.json()['data']['invite_token']
        
        # Step 2: User accepts invite
        accept_response = self.client.post(
            '/api/v1/users/invite/accept/',
            {},
            HTTP_X_INVITE_TOKEN=invite_token
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK,
                        f"Step 2: User should accept invite successfully: {accept_response.json()}")
        reg_token = accept_response.json()['data']['registration_token']
        
        # Step 3: User registers
        register_response = self.client.post(
            '/api/v1/users/register/',
            {
                'username': 'complete_flow_user',
                'password': 'MySecurePass123'
            },
            HTTP_X_REGISTRATION_TOKEN=reg_token
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED,
                        f"Step 3: User should register successfully: {register_response.json()}")
        
        # Step 4: User logs in
        login_response = self.client.post('/api/v1/users/login/', {
            'username': 'complete_flow_user',
            'password': 'MySecurePass123'
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK,
                        f"Step 4: User should login successfully: {login_response.json()}")
        
        # Step 5: Verify user has correct role
        user_data = login_response.json()['data']['user']
        self.assertEqual(user_data['role'], Roles.PERVERT,
                        f"Step 5: User role should be PERVERT, got {user_data['role']}")
        
        # Step 6: Verify user can access authenticated endpoints
        new_user_token = login_response.json()['data']['access']
        protected_response = self.client.get(
            '/api/v1/users/invites/',
            HTTP_AUTHORIZATION=f'Bearer {new_user_token}'
        )
        # Should be forbidden (not admin), not unauthorized
        self.assertEqual(protected_response.status_code, status.HTTP_403_FORBIDDEN,
                        f"Step 6: Non-admin should be forbidden (not unauthorized): {protected_response.json()}")
