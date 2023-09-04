import json

from dabpumps.auth import Auth
from dabpumps.const import API_GET_INSTALLATION
from dabpumps.pump import Pump


class Installation:
    def __init__(self, auth: Auth, data):
        self._auth = auth
        self._installation_id = data["installation_id"]
        self._name = data["name"]
        self._description = data["description"]
        self._address = data["metadata"]["address"]
        self._status = data["status"]

    async def async_get_pumps(self) -> list[Pump]:
        json_dict = await self._auth.request("get", f"{API_GET_INSTALLATION}/{self._installation_id}")
        return [Pump(self._auth, data) for data in json.loads(json_dict["data"])["dumlist"]]

    @property
    def installation_id(self):
        return self._installation_id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def address(self):
        return self._address

    @property
    def status(self):
        return self._status
