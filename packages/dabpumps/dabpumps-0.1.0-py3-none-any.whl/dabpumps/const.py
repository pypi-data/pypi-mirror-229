from typing import Final

API_BASE_URL: Final[str] = "https://dconnect.dabpumps.com"
API_GET_TOKEN: Final[str] = "auth/token"
API_GET_INSTALLATION_LIST: Final[str] = "getInstallationList"
API_GET_INSTALLATION: Final[str] = "getInstallation"
API_GET_DUMSTATE: Final[str] = "dumstate"
API_EXCEPTION_RETRY_TIME: Final[float] = 0.1
API_RETRY_ATTEMPTS: Final[int] = 10
