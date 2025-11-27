"""Test suite: System"""
from django.utils import timezone
from lux.tests import LuxBaseTest
from lux import settings


class SystemsTest(LuxBaseTest):
    """
    Tests system level behaviours.
    """

    def test_timezone(self):
        """
        Test that the timezone is loaded in correctly from the environment.
        """

        # 1. Get the current time localized to the project's default timezone
        now_localized = timezone.localtime()

        # 2. Get the name of the timezone used by the localized object
        timestamp_tz_name = now_localized.tzinfo.tzname(now_localized)

        # 3. Get the name of the timezone from the Django settings
        settings_tz_name = settings.TIME_ZONE

        # Assert that the two names match
        self.assertEqual(
            timestamp_tz_name,
            settings_tz_name,
            f"Timestamp timezone '{timestamp_tz_name}' does not match settings TIME_ZONE '{settings_tz_name}'."
        )
