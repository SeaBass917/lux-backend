"""
URL configuration for users project.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views.login import LoginView
from users.views.register import RegisterView
from users.views.invite_accept import InviteAcceptView
from users.views.invite_generator import InviteGeneratorView
from users.views.invite_detail_view import InviteDetailView
from users.views.invite_list_view import InviteListView


urlpatterns = [
    path('invite/<int:pk>/', InviteDetailView.as_view(), name='invite_detail'),
    path('invites/', InviteListView.as_view(), name='invite_list'),
    path('invite/generate/', InviteGeneratorView.as_view(), name='generate_invite'),
    path('invite/accept/', InviteAcceptView.as_view(), name='accept_invite'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
