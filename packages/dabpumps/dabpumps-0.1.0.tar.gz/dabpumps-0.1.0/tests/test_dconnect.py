import os
from datetime import UTC, datetime

import aiounittest
from aiohttp import ClientSession
from aioresponses import aioresponses

from dabpumps.auth import Auth
from dabpumps.const import (
    API_BASE_URL,
    API_GET_DUMSTATE,
    API_GET_INSTALLATION,
    API_GET_INSTALLATION_LIST,
    API_GET_TOKEN,
)
from dabpumps.dconnect import DConnect
from dabpumps.exceptions import ForbiddenError, WrongCredentialError
from dabpumps.pump import MeasureSystem, PumpStatus, SystemStatus

ACCESS_TOKEN = "access-token"
INSTALLATION_ID = "installation-id"
PUMP_SERIAL = "pump-serial"


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as file:
        return file.read()


class TestDConnect(aiounittest.AsyncTestCase):
    def setUp(self):
        """Setup things to be run when tests are started."""

    @aioresponses()
    async def test_authenticate_ok(self, mock):
        mock.post(
            f"{API_BASE_URL}/{API_GET_TOKEN}",
            body=load_fixture("get_token_ok.json"),
        )

        auth = Auth(ClientSession(), "email", "password")
        await auth.authenticate()

        self.assertEqual(ACCESS_TOKEN, auth.access_token)
        self.assertGreaterEqual((auth.access_token_expires - datetime.now(UTC)).days, 364)

    @aioresponses()
    async def test_authenticate_wrong_credential(self, mock):
        mock.post(
            f"{API_BASE_URL}/{API_GET_TOKEN}",
            body=load_fixture("get_token_wrong_credential.json"),
        )

        auth = Auth(ClientSession(), "email", "password")
        with self.assertRaises(WrongCredentialError):
            await auth.authenticate()

    @aioresponses()
    async def test_get_installations_ok(self, mock):
        mock.post(
            f"{API_BASE_URL}/{API_GET_TOKEN}",
            body=load_fixture("get_token_ok.json"),
        )
        mock.get(
            f"{API_BASE_URL}/{API_GET_INSTALLATION_LIST}",
            body=load_fixture("get_installations_ok.json"),
        )

        dconnect = DConnect(Auth(ClientSession(), "email", "password"))
        installations = await dconnect.async_get_installations()
        self.assertEqual(1, len(installations))

        installation = installations[0]
        self.assertEqual("installation-id", installation.installation_id)
        self.assertEqual("installation-name", installation.name)
        self.assertEqual("installation-description", installation.description)
        self.assertEqual("installation-address", installation.address)
        self.assertEqual("OK", installation.status)

    @aioresponses()
    async def test_get_installations_forbidden(self, mock):
        mock.post(f"{API_BASE_URL}/{API_GET_TOKEN}", body=load_fixture("get_token_ok.json"), repeat=True)
        mock.get(
            f"{API_BASE_URL}/{API_GET_INSTALLATION_LIST}",
            body=load_fixture("get_installations_forbidden.json"),
            repeat=True,
        )

        dconnect = DConnect(Auth(ClientSession(), "email", "password"))
        with self.assertRaises(ForbiddenError):
            await dconnect.async_get_installations()

    @aioresponses()
    async def test_get_pumps(self, mock):
        mock.post(
            f"{API_BASE_URL}/{API_GET_TOKEN}",
            body=load_fixture("get_token_ok.json"),
        )
        mock.get(
            f"{API_BASE_URL}/{API_GET_INSTALLATION_LIST}",
            body=load_fixture("get_installations_ok.json"),
        )
        mock.get(
            f"{API_BASE_URL}/{API_GET_INSTALLATION}/{INSTALLATION_ID}",
            body=load_fixture("get_installation.json"),
        )

        dconnect = DConnect(Auth(ClientSession(), "email", "password"))
        installations = await dconnect.async_get_installations()
        self.assertEqual(1, len(installations))
        pumps = await installations[0].async_get_pumps()
        self.assertEqual(1, len(pumps))

        pump = pumps[0]
        self.assertEqual("pump-name", pump.name)
        self.assertEqual(PUMP_SERIAL, pump.serial)
        self.assertEqual("OK", pump.status)
        self.assertEqual("E.sybox Mini", pump.product_name)

    @aioresponses()
    async def test_get_pump_state_international_standby(self, mock):
        state = await self._async_get_pump_state(mock, "get_dumstate_international_standby.json")

        self.assertEqual(datetime.fromisoformat("2023-07-11T13:17:31.173+00:00"), state.timestamp)
        self.assertEqual(20, state.sample_rate)
        self.assertEqual("mac-wlan", state.mac_wlan)
        self.assertEqual("essid", state.essid)
        self.assertEqual(2.7, state.setpoint_pressure_bar)
        self.assertEqual(None, state.setpoint_pressure_psi)
        self.assertEqual(0.3, state.restart_pressure_bar)
        self.assertEqual(None, state.restart_pressure_psi)
        self.assertEqual(PumpStatus.STANDBY, state.pump_status)
        self.assertEqual(MeasureSystem.INTERNATIONAL, state.measure_system)
        self.assertEqual(0, state.rotating_speed_rpm)
        self.assertEqual(2.5, state.pressure_bar)
        self.assertEqual(None, state.pressure_psi)
        self.assertEqual(5, len(state.errors))
        self.assertEqual(SystemStatus.LOW_VOLTAGE_VSL, state.errors[0].status)
        self.assertEqual(datetime.fromisoformat("2023-05-28 07:59:15+00:00"), state.errors[0].time)

    @aioresponses()
    async def test_get_pump_state_anglo_american_standby(self, mock):
        state = await self._async_get_pump_state(mock, "get_dumstate_anglo_american_standby.json")

        self.assertEqual(datetime.fromisoformat("2023-07-31T06:17:15.241+00:00"), state.timestamp)
        self.assertEqual(None, state.setpoint_pressure_bar)
        self.assertEqual(39.2, state.setpoint_pressure_psi)
        self.assertEqual(None, state.restart_pressure_bar)
        self.assertEqual(4.4, state.restart_pressure_psi)
        self.assertEqual(MeasureSystem.ANGLO_AMERICAN, state.measure_system)
        self.assertEqual(None, state.pressure_bar)
        self.assertEqual(38.5, state.pressure_psi)

    @aioresponses()
    async def test_get_pump_state_anglo_american_go(self, mock):
        state = await self._async_get_pump_state(mock, "get_dumstate_anglo_american_go.json")

        self.assertEqual(PumpStatus.GO, state.pump_status)
        self.assertEqual(2577, state.rotating_speed_rpm)

    async def _async_get_pump_state(self, mock, fixture):
        mock.post(
            f"{API_BASE_URL}/{API_GET_TOKEN}",
            body=load_fixture("get_token_ok.json"),
        )
        mock.get(
            f"{API_BASE_URL}/{API_GET_INSTALLATION_LIST}",
            body=load_fixture("get_installations_ok.json"),
        )
        mock.get(
            f"{API_BASE_URL}/{API_GET_INSTALLATION}/{INSTALLATION_ID}",
            body=load_fixture("get_installation.json"),
        )
        mock.get(
            f"{API_BASE_URL}/{API_GET_DUMSTATE}/{PUMP_SERIAL}",
            body=load_fixture(fixture),
        )

        dconnect = DConnect(Auth(ClientSession(), "email", "password"))
        installations = await dconnect.async_get_installations()
        self.assertEqual(1, len(installations))
        pumps = await installations[0].async_get_pumps()
        self.assertEqual(1, len(pumps))
        pump = pumps[0]
        await pump.async_update_state()
        return pump.state
