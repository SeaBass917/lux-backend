from os import getenv
from os.path import exists
from celery.schedules import crontab
from json import load as json_load

from lux.utils.settings.timezone import get_system_timezone


def get_celery_settings() -> list[str]:
    """Get the settings for celery

    Returns:
        list[str]: [
            CELERY_BROKER_URL, 
            CELERY_RESULT_BACKEND, 
            CELERY_ACCEPT_CONTENT,
            CELERY_TASK_SERIALIZER,
            CELERY_RESULT_SERIALIZER,
            CELERY_BEAT_SCHEDULE,
            CELERY_TIMEZONE,
        ]
    """

    # Redis settings
    # NOTE: celery wants the internal redis IP
    __redis_host = getenv("REDIS_HOST", "redis")
    __redis_port = getenv("REDIS_PORT_IN", "6479")

    # Set transport and password based on local or server deployment
    __redis_ssl = getenv("REDIS_SSL", None)

    __redis_transport = "redis"  # pylint: disable=invalid-name
    __redis_params = ""  # pylint: disable=invalid-name

    if __redis_ssl is not None and __redis_ssl.lower() == "true":
        __redis_transport = "rediss"  # pylint: disable=invalid-name
        __redis_params = "?ssl_cert_reqs=required"  # pylint: disable=invalid-name

    __redis_password = getenv("REDIS_PASSWORD", None)
    if __redis_password is not None:
        CELERY_BROKER_URL = f"{__redis_transport}://default:{__redis_password}@{__redis_host}:{__redis_port}{__redis_params}"  # noqa # pylint: disable=line-too-long
    else:
        CELERY_BROKER_URL = f"{
            __redis_transport}: // {__redis_host}: {__redis_port}{__redis_params}"

    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
    CELERY_ACCEPT_CONTENT = ["application/json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"

    # Read in the schedule from a file if it exists
    # NOTE: THe file stores the hour, minute, etc as strings
    __celery_beat_schedule_filepath = getenv("CELERY_BEAT_SCHEDULE_FILEPATH")
    CELERY_BEAT_SCHEDULE = {}
    with open("text.txt", "w") as fp:
        fp.write("imtryin ")
        fp.write(str(__celery_beat_schedule_filepath) + " ")
        fp.write(str(getenv("CELERY_BEAT_SCHEDULE_FILEPATH")))
    if __celery_beat_schedule_filepath and \
            exists(__celery_beat_schedule_filepath):

        with open("text2.txt", "w") as fp:
            fp.write("__celery_beat_schedule_filepath")
        schedule_data = {}
        with open(__celery_beat_schedule_filepath, "r", encoding="utf-8") as fp_in:
            schedule_data = json_load(fp_in)
            for key, value in schedule_data.items():
                value["schedule"] = crontab(**value["schedule"])
                CELERY_BEAT_SCHEDULE[key] = value

    CELERY_TIMEZONE = get_system_timezone()

    return [
        CELERY_BROKER_URL,
        CELERY_RESULT_BACKEND,
        CELERY_ACCEPT_CONTENT,
        CELERY_TASK_SERIALIZER,
        CELERY_RESULT_SERIALIZER,
        CELERY_BEAT_SCHEDULE,
        CELERY_TIMEZONE,
    ]
