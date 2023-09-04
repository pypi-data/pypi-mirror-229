import json
from datetime import UTC, datetime
from enum import Enum, unique

from dabpumps.auth import Auth
from dabpumps.const import API_GET_DUMSTATE


class Pump:
    def __init__(self, auth: Auth, data):
        self._auth = auth
        self._name = data["name"]
        self._serial = data["serial"]
        self._status = data["dum_state"]
        metadata = json.loads(data["configuration"]["metadata"])
        self._product_name = metadata["ProductName"]
        timestamp = datetime.fromisoformat(data["statusts"].replace("Z", "+00:00"))
        self._state = PumpState(timestamp, json.loads(data["status"]))

    async def async_update_state(self):
        json_dict = await self._auth.request("get", f"{API_GET_DUMSTATE}/{self._serial}")
        timestamp = datetime.fromisoformat(json_dict["statusts"].replace("Z", "+00:00"))
        self._state = PumpState(timestamp, json.loads(json_dict["status"]))

    @property
    def name(self):
        return self._name

    @property
    def serial(self):
        return self._serial

    @property
    def status(self):
        return self._status

    @property
    def product_name(self):
        return self._product_name

    @property
    def state(self):
        return self._state


@unique
class PlantType(Enum):
    RIGID = 1
    ELASTIC = 2


@unique
class MeasureSystem(Enum):
    INTERNATIONAL = 0
    ANGLO_AMERICAN = 1


@unique
class PumpStatus(Enum):
    STANDBY = 0
    GO = 1
    FAULT = 2
    MANUAL_DISABLE = 3
    TEST_MODE_GO = 4
    TEST_MODE_STANDBY = 5
    WARNING = 6
    NOT_CONFIGURATED = 7
    FUNCTION_F1 = 8
    FUNCTION_F3 = 9
    FUNCTION_F4 = 10
    NO_STATE = 11


@unique
class SystemStatus(Enum):
    SYSTEM_OK = 0
    INTERNAL_ERROR_E0_0 = 1
    INTERNAL_ERROR_E0_1 = 2
    INTERNAL_ERROR_E0_2 = 3
    INTERNAL_ERROR_E0_3 = 4
    INTERNAL_ERROR_E0_4 = 5
    INTERNAL_ERROR_E0_5 = 6
    INTERNAL_ERROR_E0_6 = 7
    INTERNAL_ERROR_E0_7 = 8
    INTERNAL_ERROR_E1_0 = 9
    INTERNAL_ERROR_E1_1 = 10
    INTERNAL_ERROR_E1_2 = 11
    INTERNAL_ERROR_E2 = 12
    INTERNAL_ERROR_E3 = 13
    INTERNAL_ERROR_E4 = 14
    INTERNAL_ERROR_E5 = 15
    INTERNAL_ERROR_E6 = 16
    INTERNAL_ERROR_E7 = 17
    INTERNAL_ERROR_E8 = 18
    INTERNAL_ERROR_E9 = 19
    INTERNAL_ERROR_E10 = 20
    INTERNAL_ERROR_E11 = 21
    INTERNAL_ERROR_E12 = 22
    INTERNAL_ERROR_E14 = 23
    INTERNAL_ERROR_E15 = 24
    INTERNAL_ERROR_E16 = 25
    INTERNAL_ERROR_E13 = 26
    SHORT_CIRCUIT_SC = 27
    SHORT_CIRCUIT_ESC = 28
    MOTOR_TRIP = 29
    INTERNAL_ERROR_E17 = 30
    INTERNAL_ERROR_E18 = 31
    INTERNAL_ERROR_E19 = 32
    INTERNAL_ERROR_E20 = 33
    INTERNAL_ERROR_E21 = 34
    INTERNAL_ERROR_E22 = 35
    INTERNAL_ERROR_E23 = 36
    INTERNAL_ERROR_PFC = 37
    OVERCURRENT_DCC = 38
    VOLTAGE_ERROR_VSH = 39
    INTERNAL_ERROR_PD = 40
    VOLTAGE_ERROR_V0 = 41
    VOLTAGE_ERROR_V5 = 42
    VOLTAGE_ERROR_V3 = 43
    VOLTAGE_ERROR_V5P = 44
    VOLTAGE_ERROR_V5F = 45
    OVER_TEMPERATURE_OT = 46
    OVER_TEMPERATURE_OBL = 47
    OVER_TEMPERATURE_OBH = 48
    LOW_VOLTAGE_VSL = 49
    LOW_VOLTAGE_LP = 50
    HIGH_VOLTAGE_HP = 51
    PUMP_POSITION_PP = 53
    HOT_PUMP_PH = 54
    FLUID_HOT_HL = 55
    DRY_RUN_BL = 58
    PRESSURE_SENSOR_BP1 = 59
    PRESSURE_SENSOR_BP2 = 60
    PRESSURE_SENSOR_BP3 = 61
    NOT_CONNECTED_PUMP = 62
    OVER_PRESSURE_OP = 63
    LOSS_LK = 64
    ANTICYCLING_EY = 65
    MAXIMUM_TIME_TW = 66
    CURRENT_LIMIT_HVL = 67


@unique
class Language(Enum):
    ITALIAN = 0
    ENGLISH = 1
    GERMAN = 2
    SPANISH = 3
    DUTCH = 4
    SWEDISH = 5
    TURKISH = 6
    ROMANIAN = 7
    CZECH = 8
    POLISH = 9
    RUSSIAN = 10
    PORTUGUESE = 11
    THAI = 12
    FRENCH = 13
    SLOVENIAN = 14
    CHINESE = 15


@unique
class LowPressureMode(Enum):
    DISABLED = 0
    ENABLED_WITH_AUTOMATIC_RESET = 1
    ENABLED_WITH_MANUAL_RESET = 2


@unique
class AntiCyclingMode(Enum):
    DISABLED = 0
    ENABLED = 1
    SMART = 2


class PumpError:
    def __init__(self, error_code, error_time):
        self.status = SystemStatus(error_code)
        self.time = datetime.fromtimestamp(error_time, UTC)


class PumpState:
    def __init__(self, timestamp, data):
        self._timestamp = timestamp
        # FirmwareStatus: 1
        # UpdateFirmware: 0
        # UpdateProgress: h
        self._sample_rate = int(data["SampleRate"])
        # MemFree: 84288
        # BootTime: 552918
        self._mac_wlan = data["MacWlan"]
        self._essid = data["ESSID"]
        self._signal_level_percent = int(data["SignLevel"])
        self._ip_external = data["IpExt"]
        # CheckUpdates: 0
        # UpdateResult: 0
        self._version_dplus = data["DPlusVersion"]
        # WSstatus: 7
        self._setpoint_pressure_bar = (
            float(data["SP_SetpointPressureBar"]) / 10 if data["SP_SetpointPressureBar"] != "h" else None
        )
        self._setpoint_pressure_psi = (
            float(data["SP_SetpointPressurePsi"]) / 10 if data["SP_SetpointPressurePsi"] != "h" else None
        )
        self._restart_pressure_bar = (
            float(data["RP_PressureFallToRestartBar"]) / 10 if data["RP_PressureFallToRestartBar"] != "h" else None
        )
        self._restart_pressure_psi = (
            float(data["RP_PressureFallToRestartPsi"]) / 10 if data["RP_PressureFallToRestartPsi"] != "h" else None
        )
        self._low_pressure_mode = (
            LowPressureMode(int(data["EK_LowPressEnable"])) if data["EK_LowPressEnable"] != "h" else None
        )
        self._low_pressure_threshold_bar = (
            float(data["PK_LowPressureThresholdBar"]) / 10 if data["PK_LowPressureThresholdBar"] != "h" else None
        )
        self._low_pressure_threshold_psi = (
            float(data["PK_LowPressureThresholdPsi"]) / 10 if data["PK_LowPressureThresholdPsi"] != "h" else None
        )
        self._plant_type = PlantType(int(data["OD_PlantType"]))
        self._measure_system = MeasureSystem(int(data["MS_MeasureSystem"]))
        self._language = Language(int(data["LA_Language"]))
        self._dry_run_detect_time_seconds = (
            int(data["TB_DryRunDetectTime"]) if data["TB_DryRunDetectTime"] != "h" else None
        )
        self._low_pressure_delay_seconds = (
            int(data["T1_LowPressureDelay"]) if data["T1_LowPressureDelay"] != "h" else None
        )
        self._switch_off_delay_seconds = int(data["T2_SwitchOffDelay"]) if data["T2_SwitchOffDelay"] != "h" else None
        self._proportional_gain_rigid_plant = (
            float(data["GP_ProportionalGainRigidPlant"]) / 10 if data["GP_ProportionalGainRigidPlant"] != "h" else None
        )
        self._integral_gain_rigid_plant = (
            float(data["GI_IntegralGainRigidPlant"]) / 10 if data["GI_IntegralGainRigidPlant"] != "h" else None
        )
        self._proportional_gain_elastic_plant = (
            float(data["GP_ProportionalGainElasticPlant"]) / 10
            if data["GP_ProportionalGainElasticPlant"] != "h"
            else None
        )
        self._integral_gain_elastic_plant = (
            float(data["GI_IntegralGainElasticPlant"]) / 10 if data["GI_IntegralGainElasticPlant"] != "h" else None
        )
        self._maximum_speed_rpm = int(data["RM_MaximumSpeed"]) if data["RM_MaximumSpeed"] != "h" else None
        self._anti_lock_enabled = int(data["AE_AntiLock"]) == 1
        self._anit_freeze_enabled = int(data["AF_AntiFreeze"]) == 1
        self._anti_cycling_mode = AntiCyclingMode(int(data["AY_AntiCycling"]))
        self._modify_password = int(data["PW_ModifyPassword"])
        self._power_on_hours = int(data["HO_PowerOnHours"]) if data["HO_PowerOnHours"] != "h" else None
        self._pump_run_hours = int(data["HO_PumpRunHours"]) if data["HO_PumpRunHours"] != "h" else None
        self._rotating_speed_rpm = int(data["RS_RotatingSpeed"]) if data["RS_RotatingSpeed"] != "h" else None
        self._pressure_bar = float(data["VP_PressureBar"]) / 10 if data["VP_PressureBar"] != "h" else None
        self._pressure_psi = float(data["VP_PressurePsi"]) / 10 if data["VP_PressurePsi"] != "h" else None
        self._pump_phase_current_amperes = (
            float(data["C1_PumpPhaseCurrent"]) / 10 if data["C1_PumpPhaseCurrent"] != "h" else None
        )
        self._output_power_watts = int(data["PO_OutputPower"]) if data["PO_OutputPower"] != "h" else None
        self._flow_liters_per_minute = float(data["VF_FlowLiter"]) / 10 if data["VF_FlowLiter"] != "h" else None
        self._flow_gallons_per_minute = float(data["VF_FlowGall"]) / 10 if data["VF_FlowGall"] != "h" else None
        self._total_delivered_flow_liters = (
            int(data["FCt_Total_Delivered_Flow_mc"]) if data["FCt_Total_Delivered_Flow_mc"] != "h" else None
        )
        self._total_delivered_flow_gallons = (
            int(data["FCt_Total_Delivered_Flow_Gall"]) if data["FCt_Total_Delivered_Flow_Gall"] != "h" else None
        )
        self._partial_delivered_flow_liters = (
            int(data["FCp_Partial_Delivered_Flow_mc"]) if data["FCp_Partial_Delivered_Flow_mc"] != "h" else None
        )
        self._partial_delivered_flow_gallons = (
            int(data["FCp_Partial_Delivered_Flow_Gall"]) if data["FCp_Partial_Delivered_Flow_Gall"] != "h" else None
        )
        self._heatsink_temperature_c = (
            float(data["TE_HeatsinkTemperatureC"]) / 10 if data["TE_HeatsinkTemperatureC"] != "h" else None
        )
        self._heatsink_temperature_f = (
            float(data["TE_HeatsinkTemperatureF"]) / 10 if data["TE_HeatsinkTemperatureF"] != "h" else None
        )
        self._suction_pressure_bar = (
            float(data["PKm_SuctionPressureBar"]) / 10 if data["PKm_SuctionPressureBar"] != "h" else None
        )
        self._suction_pressure_psi = (
            float(data["PKm_SuctionPressurePsi"]) / 10 if data["PKm_SuctionPressurePsi"] != "h" else None
        )
        try:
            self._pump_status = PumpStatus(int(data["PumpStatus"]))
        except ValueError:
            self._pump_status = None
        try:
            self._system_status = PumpStatus(int(data["SystemStatus"]))
        except ValueError:
            self._system_status = None
        self._number_of_starts = int(data["StartNumber"])
        # RamUsed: 296080
        # RamUsedMax: 303336
        # RF_EraseHistoricalFault: 0
        # PumpDisable: 0
        # ResetActualFault: 0
        # ErasePartialFlowCounter: 0
        # FactoryDefault: 0
        # IdentifyDevice: 0
        # PowerShowerCommand: 0
        self._power_shower_boost_percent = int(data["PowerShowerBoost"]) if data["PowerShowerBoost"] != "h" else None
        self._power_shower_countdown_seconds = (
            int(data["PowerShowerCountdown"]) if data["PowerShowerCountdown"] != "h" else None
        )
        self._power_shower_pressure_bar = (
            float(data["PowerShowerPressureBar"]) / 10 if data["PowerShowerPressureBar"] != "h" else None
        )
        self._power_shower_pressure_psi = (
            float(data["PowerShowerPressurePsi"]) / 10 if data["PowerShowerPressurePsi"] != "h" else None
        )
        self._power_shower_duration_seconds = (
            int(data["PowerShowerDuration"]) if data["PowerShowerDuration"] != "h" else None
        )
        self._sleep_mode_enabled = int(data["SleepModeEnable"]) == 1
        self._sleep_mode_reduction_percent = (
            int(data["SleepModeReduction"]) if data["SleepModeReduction"] != "h" else None
        )
        self._sleep_mode_pressure_bar = (
            float(data["SleepModePressureBar"]) / 10 if data["SleepModePressureBar"] != "h" else None
        )
        self._sleep_mode_pressure_psi = (
            float(data["SleepModePressurePsi"]) / 10 if data["SleepModePressurePsi"] != "h" else None
        )
        self._sleep_mode_start_time_seconds = (
            int(data["SleepModeStartTime"]) if data["SleepModeStartTime"] != "h" else None
        )
        self._sleep_mode_duration_seconds = int(data["SleepModeDuration"]) if data["SleepModeDuration"] != "h" else None
        self._sleep_mode_countdown_seconds = (
            int(data["SleepModeCountdown"]) if data["SleepModeCountdown"] != "h" else None
        )
        self._supply_voltage = int(data["SV_SupplyVoltage"]) if data["SV_SupplyVoltage"] != "h" else None
        self._current_month_water_consumption_liters = (
            int(data["Actual_Period_Flow_Counter"]) if data["Actual_Period_Flow_Counter"] != "h" else None
        )
        self._last_month_water_consumption_liters = (
            int(data["Last_Period_Flow_Counter"]) if data["Last_Period_Flow_Counter"] != "h" else None
        )
        self._last_month_energy_consumption_kilowatt_hours = (
            float(data["Last_Period_Energy_Counter"]) / 10 if data["Last_Period_Energy_Counter"] != "h" else None
        )
        self._current_month_energy_consumption_kilowatt_hours = (
            float(data["Actual_Period_Energy_Counter"]) / 10 if data["Actual_Period_Energy_Counter"] != "h" else None
        )
        self._saving_percent = int(data["Saving"]) if data["Saving"] != "h" else None
        self._total_energy_consumption_kilowatt_hours = (
            float(data["TotalEnergy"]) / 10 if data["TotalEnergy"] != "h" else None
        )
        self._partial_energy_consumption_kilowatt_hours = (
            float(data["PartialEnergy"]) / 10 if data["PartialEnergy"] != "h" else None
        )
        self._current_month_water_consumption_gallons = (
            int(data["Actual_Period_Flow_Counter_Gall"]) if data["Actual_Period_Flow_Counter_Gall"] != "h" else None
        )
        self._last_month_water_consumption_gallons = (
            int(data["Last_Period_Flow_Counter_Gall"]) if data["Last_Period_Flow_Counter_Gall"] != "h" else None
        )
        self._version_lv = data["LvVersion"]
        self._version_hv = data["HvVersion"]
        self._product_serial_number = data["ProductSerialNumber"]
        self._power_on_seconds = int(data["SO_PowerOnSeconds"]) if data["SO_PowerOnSeconds"] != "h" else None
        self._pump_run_seconds = int(data["SO_PumpRunSeconds"]) if data["SO_PumpRunSeconds"] != "h" else None
        # ErasePartialEnergyCounter: 0
        self._errors = []
        for i in range(1, 9):
            error_code = int(data[f"Error{i}"])
            error_time = int(data[f"ErrorTime{i}"])
            if error_code > 0 and error_time > 0:
                self._errors.append(PumpError(error_code, error_time))

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def mac_wlan(self) -> str:
        return self._mac_wlan

    @property
    def essid(self) -> str:
        return self._essid

    @property
    def signal_level_percent(self) -> int:
        return self._signal_level_percent

    @property
    def ip_external(self) -> str:
        return self._ip_external

    @property
    def version_dplus(self) -> str:
        return self._version_dplus

    @property
    def setpoint_pressure_bar(self) -> float:
        return self._setpoint_pressure_bar

    @property
    def setpoint_pressure_psi(self) -> float:
        return self._setpoint_pressure_psi

    @property
    def restart_pressure_bar(self) -> float:
        return self._restart_pressure_bar

    @property
    def restart_pressure_psi(self) -> float:
        return self._restart_pressure_psi

    @property
    def low_pressure_mode(self) -> LowPressureMode:
        return self._low_pressure_mode

    @property
    def low_pressure_threshold_bar(self) -> float:
        return self._low_pressure_threshold_bar

    @property
    def low_pressure_threshold_psi(self) -> float:
        return self._low_pressure_threshold_psi

    @property
    def plant_type(self) -> PlantType:
        return self._plant_type

    @property
    def measure_system(self) -> MeasureSystem:
        return self._measure_system

    @property
    def dry_run_detect_time_seconds(self) -> int:
        return self._dry_run_detect_time_seconds

    @property
    def low_pressure_delay_seconds(self) -> int:
        return self._low_pressure_delay_seconds

    @property
    def switch_off_delay_seconds(self) -> int:
        return self._switch_off_delay_seconds

    @property
    def proportional_gain_rigid_plant(self) -> float:
        return self._proportional_gain_rigid_plant

    @property
    def integral_gain_rigid_plant(self) -> float:
        return self._integral_gain_rigid_plant

    @property
    def proportional_gain_elastic_plant(self) -> float:
        return self._proportional_gain_elastic_plant

    @property
    def integral_gain_elastic_plant(self) -> float:
        return self._integral_gain_elastic_plant

    @property
    def maximum_speed_rpm(self) -> int:
        return self._maximum_speed_rpm

    @property
    def anti_lock_enabled(self) -> bool:
        return self._anti_lock_enabled

    @property
    def anit_freeze_enabled(self) -> bool:
        return self._anit_freeze_enabled

    @property
    def anti_cycling_mode(self) -> AntiCyclingMode:
        return self._anti_cycling_mode

    @property
    def modify_password(self) -> int:
        return self._modify_password

    @property
    def power_on_hours(self) -> int:
        return self._power_on_hours

    @property
    def pump_run_hours(self) -> int:
        return self._pump_run_hours

    @property
    def rotating_speed_rpm(self) -> int:
        return self._rotating_speed_rpm

    @property
    def pressure_bar(self) -> float:
        return self._pressure_bar

    @property
    def pressure_psi(self) -> float:
        return self._pressure_psi

    @property
    def pump_phase_current_amperes(self) -> float:
        return self._pump_phase_current_amperes

    @property
    def output_power_watts(self) -> int:
        return self._output_power_watts

    @property
    def flow_liters_per_minute(self) -> float:
        return self._flow_liters_per_minute

    @property
    def flow_gallons_per_minute(self) -> float:
        return self._flow_gallons_per_minute

    @property
    def total_delivered_flow_liters(self) -> int:
        return self._total_delivered_flow_liters

    @property
    def total_delivered_flow_gallons(self) -> int:
        return self._total_delivered_flow_gallons

    @property
    def partial_delivered_flow_liters(self) -> int:
        return self._partial_delivered_flow_liters

    @property
    def partial_delivered_flow_gallons(self) -> int:
        return self._partial_delivered_flow_gallons

    @property
    def heatsink_temperature_c(self) -> float:
        return self._heatsink_temperature_c

    @property
    def heatsink_temperature_f(self) -> float:
        return self._heatsink_temperature_f

    @property
    def suction_pressure_bar(self) -> float:
        return self._suction_pressure_bar

    @property
    def suction_pressure_psi(self) -> float:
        return self._suction_pressure_psi

    @property
    def pump_status(self) -> PumpStatus:
        return self._pump_status

    @property
    def system_status(self) -> SystemStatus:
        return self._system_status

    @property
    def number_of_starts(self) -> int:
        return self._number_of_starts

    @property
    def power_shower_boost_percent(self) -> int:
        return self._power_shower_boost_percent

    @property
    def power_shower_countdown_seconds(self) -> int:
        return self._power_shower_countdown_seconds

    @property
    def power_shower_pressure_bar(self) -> float:
        return self._power_shower_pressure_bar

    @property
    def power_shower_pressure_psi(self) -> float:
        return self._power_shower_pressure_psi

    @property
    def power_shower_duration_seconds(self) -> int:
        return self._power_shower_duration_seconds

    @property
    def sleep_mode_enabled(self) -> bool:
        return self._sleep_mode_enabled

    @property
    def sleep_mode_reduction_percent(self) -> int:
        return self._sleep_mode_reduction_percent

    @property
    def sleep_mode_pressure_bar(self) -> float:
        return self._sleep_mode_pressure_bar

    @property
    def sleep_mode_pressure_psi(self) -> float:
        return self._sleep_mode_pressure_psi

    @property
    def sleep_mode_start_time_seconds(self) -> int:
        return self._sleep_mode_start_time_seconds

    @property
    def sleep_mode_duration_seconds(self) -> int:
        return self._sleep_mode_duration_seconds

    @property
    def sleep_mode_countdown_seconds(self) -> int:
        return self._sleep_mode_countdown_seconds

    @property
    def supply_voltage(self) -> float:
        return self._supply_voltage

    @property
    def current_month_water_consumption_liters(self) -> int:
        return self._current_month_water_consumption_liters

    @property
    def last_month_water_consumption_liters(self) -> int:
        return self._last_month_water_consumption_liters

    @property
    def last_month_energy_consumption_kilowatt_hours(self) -> float:
        return self._last_month_energy_consumption_kilowatt_hours

    @property
    def current_month_energy_consumption_kilowatt_hours(self) -> float:
        return self._current_month_energy_consumption_kilowatt_hours

    @property
    def total_energy_consumption_kilowatt_hours(self) -> float:
        return self._total_energy_consumption_kilowatt_hours

    @property
    def partial_energy_consumption_kilowatt_hours(self) -> float:
        return self._partial_energy_consumption_kilowatt_hours

    @property
    def saving_percent(self) -> int:
        return self._saving_percent

    @property
    def current_month_water_consumption_gallons(self) -> int:
        return self._current_month_water_consumption_gallons

    @property
    def last_month_water_consumption_gallons(self) -> int:
        return self._last_month_water_consumption_gallons

    @property
    def version_lv(self) -> str:
        return self._version_lv

    @property
    def version_hv(self) -> str:
        return self._version_hv

    @property
    def product_serial_number(self) -> str:
        return self._product_serial_number

    @property
    def power_on_seconds(self) -> int:
        return self._power_on_seconds

    @property
    def pump_run_seconds(self) -> int:
        return self._pump_run_seconds

    @property
    def errors(self) -> list[PumpError]:
        return self._errors
