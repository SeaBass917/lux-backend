# Default to UTC if we can't find a system setting, or set a safe fallback:
import os
import zoneinfo
import pytz


def get_system_timezone() -> str:
    """Get the system timezone.

    Returns:
        str: Timezone string.
    """
    system_tz = 'UTC'

    # Attempt to find the timezone from the environment variables
    # On Linux/macOS, this might be available in the 'TZ' environment variable.
    if 'TZ' in os.environ:
        system_tz = os.environ['TZ']
    # Further logic might be needed for Windows systems or reading specific system files

    # Validate the timezone string
    if zoneinfo:
        try:
            zoneinfo.ZoneInfo(system_tz)
        except zoneinfo.ZoneInfoNotFoundError:
            print(
                f"Warning: System timezone '{system_tz}' not recognized. Falling back to UTC.")
            system_tz = 'UTC'
    elif pytz:
        if system_tz not in pytz.all_timezones:
            print(
                f"Warning: System timezone '{system_tz}' not recognized. Falling back to UTC.")
            system_tz = 'UTC'

    return system_tz
