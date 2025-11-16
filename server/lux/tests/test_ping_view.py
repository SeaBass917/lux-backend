"""Test suite: PingView"""
from rest_framework import status
from lux.tests import LuxBaseTest


class PingViewTest(LuxBaseTest):
    """
    Tests for the ping view.
    """

    def test_ping_view_no_auth_required(self):
        """
        Test the ping view returns a 200 OK response.
        """
        response = self.client.get("/api/v1/healthy/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'info': 'Hello world'})

    def test_ping_view_with_auth(self):
        """
        Test the ping view returns a 200 OK response with authentication.
        """
        self.set_up_user_with_role('Basic')
        response = self.client.get("/api/v1/healthy/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'info': 'Hello world'})
