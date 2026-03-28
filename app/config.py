from datetime import timedelta, timezone

VERSION_FILE_NAME = "version.json"
APPLICATION_NAME = "invio-backend"
APPLICATION_VERSION = "0.1.0"
APPLICATION_TIMEZONE = timezone(timedelta(hours=5, minutes=30), name="IST")


class ApplicationEnvironmentConig:
    DEVELOPMENT = 0
    PRODUCTION = 1
    TESTING = 2
