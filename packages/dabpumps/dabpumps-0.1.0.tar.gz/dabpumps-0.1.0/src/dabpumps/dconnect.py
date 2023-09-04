from dabpumps.auth import Auth
from dabpumps.const import API_GET_INSTALLATION_LIST
from dabpumps.installation import Installation


class DConnect:
    """API for interacting with the DAB Pumps DConnect service."""

    def __init__(self, auth: Auth) -> None:
        self._auth = auth

    async def async_get_installations(self) -> list[Installation]:
        json_dict = await self._auth.request("get", API_GET_INSTALLATION_LIST)
        return [Installation(self._auth, data) for data in json_dict["rows"]]
