# tests_ping.py
'''Making test for ping to make sure anyone can hit it'''
from rest_framework import status
from lux.tests import LuxBaseTest


class PingViewTest(LuxBaseTest):
    """
    Tests for the ping view.
    """

    def test_ping_view(self):
        """
        Test the ping view returns a 200 OK response.
        """
        response = self.client.get("/api/v1/healthy/")
        self.assert_equal(response.status_code, status.HTTP_200_OK)
        self.assert_equal(response.json(), {'info': 'Hello world'})

    def test_ping_view_no_auth_required(self):
        """
        Test the ping view does not require authentication.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/healthy/")
        self.assert_equal(response.status_code, status.HTTP_200_OK)
        self.assert_equal(response.json(), {'info': 'Hello world'})

    def test_ping_view_with_auth(self):
        """
        Test the ping view returns a 200 OK response with authentication.
        """
        user = self.create_user()
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/v1/healthy/")
        self.assert_equal(response.status_code, status.HTTP_200_OK)
        self.assert_equal(response.json(), {'info': 'Hello world'})
