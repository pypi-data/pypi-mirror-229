import asyncio
import logging
from datetime import UTC, datetime, timedelta

from aiohttp import (
    ClientConnectionError,
    ClientOSError,
    ClientResponseError,
    ClientSession,
    ClientSSLError,
    ServerDisconnectedError,
)

from dabpumps.const import (
    API_BASE_URL,
    API_EXCEPTION_RETRY_TIME,
    API_GET_TOKEN,
    API_RETRY_ATTEMPTS,
)
from dabpumps.exceptions import CannotConnectError, DConnectError, ForbiddenError, WrongCredentialError

_LOGGER = logging.getLogger(__name__)


class Auth:
    """Authentication support for the DAB Pumps DConnect cloud service."""

    def __init__(self, aiohttp_session: ClientSession, email: str, password: str):
        """Initialize the auth."""
        self.aiohttp_session = aiohttp_session
        self.email = email
        self.password = password
        self.access_token: str | None = None
        self.access_token_expires: datetime | None = None

    async def authenticate(self) -> None:
        """Get an access token."""
        json_dict = await self.request("post", API_GET_TOKEN, json={"email": self.email, "password": self.password})
        self.access_token = json_dict["access_token"]
        self.access_token_expires = datetime.now(UTC) + timedelta(seconds=float(json_dict["expires_in"]))

    async def request(self, method: str, path: str, **kwargs):
        """Make a request."""
        authorization_required = path != API_GET_TOKEN
        authenticated = (
            self.access_token
            and self.access_token_expires
            and self.access_token_expires > datetime.now(UTC) + timedelta(days=1)
        )
        if authorization_required and not authenticated:
            await self.authenticate()

        url = f"{API_BASE_URL}/{path}"
        payload = kwargs.get("params") or kwargs.get("json")
        headers = kwargs.get("headers")

        if headers is None:
            headers = _api_headers()
        else:
            headers = dict(headers)

        if authorization_required and self.access_token:
            headers["authorization"] = f"Bearer {self.access_token}"

        debug_enabled = _LOGGER.isEnabledFor(logging.DEBUG)
        if debug_enabled:
            _LOGGER.debug(
                f"About to call {url} with headers={headers} and payload={_obscure_payload(payload)}",
            )

        attempts = 0
        while attempts < API_RETRY_ATTEMPTS:
            attempts += 1
            try:
                response = await self.aiohttp_session.request(
                    method,
                    url,
                    **kwargs,
                    headers=headers,
                )
            except (
                ClientOSError,
                ClientSSLError,
                ServerDisconnectedError,
                ClientConnectionError,
            ) as ex:
                if attempts == API_RETRY_ATTEMPTS:
                    msg = f"Failed to connect to API: {ex}"
                    raise CannotConnectError(msg) from ex
                await asyncio.sleep(API_EXCEPTION_RETRY_TIME)
                continue

            if debug_enabled:
                _LOGGER.debug(
                    f"Received API response from url: {url!r}, "
                    f"code: {response.status}, "
                    f"headers: {response.headers!r}, "
                    f"content: {await response.read()!r}"
                )

            try:
                response.raise_for_status()
            except ClientResponseError as err:
                msg = f"The operation failed with error code {err.status}: {err.message}."
                raise DConnectError(msg) from err

            json_dict = await response.json()

            if json_dict["res"] == "ERROR":
                error_code = json_dict["code"]
                error_message = json_dict["msg"]
                msg = f"The operation failed with error code {error_code}: {error_message}."
                if error_code == "FORBIDDEN":
                    if attempts == API_RETRY_ATTEMPTS:
                        raise ForbiddenError(msg)
                    await asyncio.sleep(API_EXCEPTION_RETRY_TIME)
                    await self.authenticate()
                    continue
                if error_code == "wrongcredential":
                    raise WrongCredentialError(msg)
                raise DConnectError(msg)

            return json_dict


def _api_headers():
    return {
        "host": "dconnect.dabpumps.com",
        "accept": "application/json, text/plain, */*",
        "connection": "keep-alive",
        "user-agent": "DabAppFreemium/1 CFNetwork/1406.0.4 Darwin/22.4.0",
        "accept-language": "en-GB,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }


def _obscure_payload(payload):
    """Obscure the payload for logging."""
    if payload is None:
        return None
    if "password" in payload:
        payload = payload.copy()
        payload["password"] = "****"  # nosec
    return payload
