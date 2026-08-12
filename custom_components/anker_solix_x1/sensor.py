
import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = [
    {"name": "Solix X1 Plant Status", "unique_id": "solix_x1_plant_status", "slave": 1, "address": 10000, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Battery Status", "unique_id": "solix_x1_battery_status", "slave": 1, "address": 10001, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 PV Power", "unique_id": "solix_x1_pv_power", "slave": 1, "address": 10002, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 3rd Party PV Power", "unique_id": "solix_x1_3rd_party_pv_power", "slave": 1, "address": 10004, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Active Power (PCS AC Side)", "unique_id": "solix_x1_active_power_pcs_ac_side", "slave": 1, "address": 10006, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Battery Power", "unique_id": "solix_x1_battery_power", "slave": 1, "address": 10008, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Load Power", "unique_id": "solix_x1_load_power", "slave": 1, "address": 10010, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Grid Power", "unique_id": "solix_x1_grid_power", "slave": 1, "address": 10012, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 SOC", "unique_id": "solix_x1_soc", "slave": 1, "address": 10014, "input_type": "input", "unit_of_measurement": "%", "data_type": "uint16", "scale": 1, "state_class": "measurement", "device_class": "battery"},
    {"name": "Solix X1 SOH", "unique_id": "solix_x1_soh", "slave": 1, "address": 10015, "input_type": "input", "unit_of_measurement": "%", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Daily PV Generation", "unique_id": "solix_x1_daily_pv_generation", "slave": 1, "address": 10016, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Total PV Generation", "unique_id": "solix_x1_total_pv_generation", "slave": 1, "address": 10018, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Daily Battery Charge Energy", "unique_id": "solix_x1_daily_battery_charge_energy", "slave": 1, "address": 10020, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Total Battery Charge Energy", "unique_id": "solix_x1_total_battery_charge_energy", "slave": 1, "address": 10022, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Daily Load Consumption Energy", "unique_id": "solix_x1_daily_load_consumption_energy", "slave": 1, "address": 10024, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Total Load Consumption Energy", "unique_id": "solix_x1_total_load_consumption_energy", "slave": 1, "address": 10026, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Daily Purchased Energy", "unique_id": "solix_x1_daily_purchased_energy", "slave": 1, "address": 10028, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Total Purchased Energy", "unique_id": "solix_x1_total_purchased_energy", "slave": 1, "address": 10030, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Daily Feed-in Energy", "unique_id": "solix_x1_daily_feed_in_energy", "slave": 1, "address": 10032, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Total Feed-in Energy", "unique_id": "solix_x1_total_feed_in_energy", "slave": 1, "address": 10034, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Rechargeable Power", "unique_id": "solix_x1_rechargeable_power", "slave": 1, "address": 10036, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Dischargeable Power", "unique_id": "solix_x1_dischargeable_power", "slave": 1, "address": 10038, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Number of PCS", "unique_id": "solix_x1_number_of_pcs", "slave": 1, "address": 10040, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Number of Available PCS", "unique_id": "solix_x1_number_of_available_pcs", "slave": 1, "address": 10041, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 System Alarm 1", "unique_id": "solix_x1_system_alarm_1", "slave": 1, "address": 10042, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 System Alarm 2", "unique_id": "solix_x1_system_alarm_2", "slave": 1, "address": 10043, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 System Alarm 3", "unique_id": "solix_x1_system_alarm_3", "slave": 1, "address": 10044, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 System Alarm 4", "unique_id": "solix_x1_system_alarm_4", "slave": 1, "address": 10045, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 System Alarm 5", "unique_id": "solix_x1_system_alarm_5", "slave": 1, "address": 10046, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 System Alarm 6", "unique_id": "solix_x1_system_alarm_6", "slave": 1, "address": 10047, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 System Alarm 7", "unique_id": "solix_x1_system_alarm_7", "slave": 1, "address": 10048, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 System Alarm 8", "unique_id": "solix_x1_system_alarm_8", "slave": 1, "address": 10049, "input_type": "input", "data_type": "uint16", "scale": 1, "# CLASSIFICATION 2": "SUMMARY - CONTROL (RW)"},
    {"name": "Solix X1 Work Mode", "unique_id": "solix_x1_work_mode", "slave": 1, "address": 10064, "input_type": "holding", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Active Power Control - Percentage", "unique_id": "solix_x1_active_power_control___percentage", "slave": 1, "address": 10069, "input_type": "holding", "unit_of_measurement": "%", "data_type": "int16", "scale": 1},
    {"name": "Solix X1 Reactive Power Control - Percentage", "unique_id": "solix_x1_reactive_power_control___percentage", "slave": 1, "address": 10070, "input_type": "holding", "unit_of_measurement": "%", "data_type": "int16", "scale": 1},
    {"name": "Solix X1 Battery Charge/Discharge Control", "unique_id": "solix_x1_battery_charge_discharge_control", "slave": 1, "address": 10071, "input_type": "holding", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1},
    {"name": "Solix X1 Switch On/Off Control", "unique_id": "solix_x1_switch_on_off_control", "slave": 1, "address": 10073, "input_type": "holding", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Export Power Limit Control Mode", "unique_id": "solix_x1_export_power_limit_control_mode", "slave": 1, "address": 10074, "input_type": "holding", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Export Power Limit Control Value", "unique_id": "solix_x1_export_power_limit_control_value", "slave": 1, "address": 10075, "input_type": "holding", "unit_of_measurement": "W", "data_type": "uint32", "swap": "word", "scale": 1},
    {"name": "Solix X1 Import Power Limit Control Mode", "unique_id": "solix_x1_import_power_limit_control_mode", "slave": 1, "address": 10077, "input_type": "holding", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Import Power Limit Control Value", "unique_id": "solix_x1_import_power_limit_control_value", "slave": 1, "address": 10078, "input_type": "holding", "unit_of_measurement": "W", "data_type": "uint32", "swap": "word", "scale": 1},
    {"name": "Solix X1 Com Disconnect Time with VPP", "unique_id": "solix_x1_com_disconnect_time_with_vpp", "slave": 1, "address": 10080, "input_type": "holding", "unit_of_measurement": "s", "data_type": "uint16", "scale": 1, "# CLASSIFICATION 3": "PCS - BASIC INFORMATION"},
    {"name": "Solix X1 Rated Power", "unique_id": "solix_x1_rated_power", "slave": 1, "address": 10124, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Maximum Active Power", "unique_id": "solix_x1_maximum_active_power", "slave": 1, "address": 10126, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Maximum Apparent Power", "unique_id": "solix_x1_maximum_apparent_power", "slave": 1, "address": 10128, "input_type": "input", "unit_of_measurement": "KVA", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Numbers of MPPT", "unique_id": "solix_x1_numbers_of_mppt", "slave": 1, "address": 10130, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Strings per MPPT", "unique_id": "solix_x1_strings_per_mppt", "slave": 1, "address": 10131, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Output Mode", "unique_id": "solix_x1_output_mode", "slave": 1, "address": 10132, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement", "# CLASSIFICATION 4": "PCS - STATUS & ALARM"},
    {"name": "Solix X1 Work Status", "unique_id": "solix_x1_work_status", "slave": 1, "address": 10143, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 PCS Alarm 1", "unique_id": "solix_x1_pcs_alarm_1", "slave": 1, "address": 10144, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 2", "unique_id": "solix_x1_pcs_alarm_2", "slave": 1, "address": 10145, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 3", "unique_id": "solix_x1_pcs_alarm_3", "slave": 1, "address": 10146, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 4", "unique_id": "solix_x1_pcs_alarm_4", "slave": 1, "address": 10147, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 5", "unique_id": "solix_x1_pcs_alarm_5", "slave": 1, "address": 10148, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 6", "unique_id": "solix_x1_pcs_alarm_6", "slave": 1, "address": 10149, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 7", "unique_id": "solix_x1_pcs_alarm_7", "slave": 1, "address": 10150, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 8", "unique_id": "solix_x1_pcs_alarm_8", "slave": 1, "address": 10151, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 9", "unique_id": "solix_x1_pcs_alarm_9", "slave": 1, "address": 10152, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 10", "unique_id": "solix_x1_pcs_alarm_10", "slave": 1, "address": 10153, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 11", "unique_id": "solix_x1_pcs_alarm_11", "slave": 1, "address": 10154, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 PCS Alarm 12", "unique_id": "solix_x1_pcs_alarm_12", "slave": 1, "address": 10155, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Internal Temperature", "unique_id": "solix_x1_internal_temperature", "slave": 1, "address": 10156, "input_type": "input", "unit_of_measurement": "\u00b0C", "data_type": "int16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "temperature", "# CLASSIFICATION 5": "PCS - PV INFORMATION"},
    {"name": "Solix X1 PV1 Voltage", "unique_id": "solix_x1_pv1_voltage", "slave": 1, "address": 10167, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 PV1 Current", "unique_id": "solix_x1_pv1_current", "slave": 1, "address": 10168, "input_type": "input", "unit_of_measurement": "A", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 PV2 Voltage", "unique_id": "solix_x1_pv2_voltage", "slave": 1, "address": 10169, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 PV2 Current", "unique_id": "solix_x1_pv2_current", "slave": 1, "address": 10170, "input_type": "input", "unit_of_measurement": "A", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 PV3 Voltage", "unique_id": "solix_x1_pv3_voltage", "slave": 1, "address": 10171, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 PV3 Current", "unique_id": "solix_x1_pv3_current", "slave": 1, "address": 10172, "input_type": "input", "unit_of_measurement": "A", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 PV4 Voltage", "unique_id": "solix_x1_pv4_voltage", "slave": 1, "address": 10173, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 PV4 Current", "unique_id": "solix_x1_pv4_current", "slave": 1, "address": 10174, "input_type": "input", "unit_of_measurement": "A", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 Total PV Power", "unique_id": "solix_x1_total_pv_power", "slave": 1, "address": 10183, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Daily PV Generation (PCS)", "unique_id": "solix_x1_daily_pv_generation_pcs", "slave": 1, "address": 10185, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Total PV Generation (PCS)", "unique_id": "solix_x1_total_pv_generation_pcs", "slave": 1, "address": 10187, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy", "# CLASSIFICATION 6": "PCS - GRID INFORMATION"},
    {"name": "Solix X1 Grid Voltage / Uab Voltage", "unique_id": "solix_x1_grid_voltage___uab_voltage", "slave": 1, "address": 10199, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Ubc Voltage", "unique_id": "solix_x1_ubc_voltage", "slave": 1, "address": 10200, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Uca Voltage", "unique_id": "solix_x1_uca_voltage", "slave": 1, "address": 10201, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Grid Phase A Voltage", "unique_id": "solix_x1_grid_phase_a_voltage", "slave": 1, "address": 10202, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Grid Phase B Voltage", "unique_id": "solix_x1_grid_phase_b_voltage", "slave": 1, "address": 10203, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Grid Phase C Voltage", "unique_id": "solix_x1_grid_phase_c_voltage", "slave": 1, "address": 10204, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Grid Current / Phase A Current", "unique_id": "solix_x1_grid_current___phase_a_current", "slave": 1, "address": 10205, "input_type": "input", "unit_of_measurement": "A", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 Grid Phase B Current", "unique_id": "solix_x1_grid_phase_b_current", "slave": 1, "address": 10206, "input_type": "input", "unit_of_measurement": "A", "data_type": "int16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 Grid Phase C Current", "unique_id": "solix_x1_grid_phase_c_current", "slave": 1, "address": 10207, "input_type": "input", "unit_of_measurement": "A", "data_type": "int16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 Grid Active Power", "unique_id": "solix_x1_grid_active_power", "slave": 1, "address": 10208, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Grid Reactive Power", "unique_id": "solix_x1_grid_reactive_power", "slave": 1, "address": 10210, "input_type": "input", "unit_of_measurement": "KVA", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Grid Power Factor", "unique_id": "solix_x1_grid_power_factor", "slave": 1, "address": 10212, "input_type": "input", "data_type": "int16", "scale": 0.001, "precision": 3, "state_class": "measurement"},
    {"name": "Solix X1 Grid Frequency", "unique_id": "solix_x1_grid_frequency", "slave": 1, "address": 10213, "input_type": "input", "unit_of_measurement": "Hz", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "# CLASSIFICATION 7": "PCS - BACKUP INFORMATION"},
    {"name": "Solix X1 Backup Voltage / Uab Voltage", "unique_id": "solix_x1_backup_voltage___uab_voltage", "slave": 1, "address": 10224, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Backup Ubc Voltage", "unique_id": "solix_x1_backup_ubc_voltage", "slave": 1, "address": 10225, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Backup Uca Voltage", "unique_id": "solix_x1_backup_uca_voltage", "slave": 1, "address": 10226, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Backup Phase A Voltage", "unique_id": "solix_x1_backup_phase_a_voltage", "slave": 1, "address": 10227, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Backup Phase B Voltage", "unique_id": "solix_x1_backup_phase_b_voltage", "slave": 1, "address": 10228, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Backup Phase C Voltage", "unique_id": "solix_x1_backup_phase_c_voltage", "slave": 1, "address": 10229, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Backup Current / Phase A Current", "unique_id": "solix_x1_backup_current___phase_a_current", "slave": 1, "address": 10230, "input_type": "input", "unit_of_measurement": "A", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 Backup Phase B Current", "unique_id": "solix_x1_backup_phase_b_current", "slave": 1, "address": 10231, "input_type": "input", "unit_of_measurement": "A", "data_type": "int16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 Backup Phase C Current", "unique_id": "solix_x1_backup_phase_c_current", "slave": 1, "address": 10232, "input_type": "input", "unit_of_measurement": "A", "data_type": "int16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 Backup Active Power", "unique_id": "solix_x1_backup_active_power", "slave": 1, "address": 10233, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Backup Reactive Power", "unique_id": "solix_x1_backup_reactive_power", "slave": 1, "address": 10235, "input_type": "input", "unit_of_measurement": "KVA", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Backup Power Factor", "unique_id": "solix_x1_backup_power_factor", "slave": 1, "address": 10237, "input_type": "input", "data_type": "int16", "scale": 0.001, "precision": 3, "state_class": "measurement"},
    {"name": "Solix X1 Backup Frequency", "unique_id": "solix_x1_backup_frequency", "slave": 1, "address": 10238, "input_type": "input", "unit_of_measurement": "Hz", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "# CLASSIFICATION 8": "BATTERY - BATTERY INFORMATION"},
    {"name": "Solix X1 Battery Number of Packs", "unique_id": "solix_x1_battery_number_of_packs", "slave": 1, "address": 10249, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Battery Rated Capacity", "unique_id": "solix_x1_battery_rated_capacity", "slave": 1, "address": 10250, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.1, "precision": 1, "state_class": "measurement"},
    {"name": "Solix X1 Battery Pack Status", "unique_id": "solix_x1_battery_pack_status", "slave": 1, "address": 10252, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Battery Voltage", "unique_id": "solix_x1_battery_voltage", "slave": 1, "address": 10253, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Battery Pack Power", "unique_id": "solix_x1_battery_pack_power", "slave": 1, "address": 10254, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Battery Pack SOC", "unique_id": "solix_x1_battery_pack_soc", "slave": 1, "address": 10256, "input_type": "input", "unit_of_measurement": "%", "data_type": "uint16", "scale": 1, "state_class": "measurement", "device_class": "battery"},
    {"name": "Solix X1 Battery Pack SOH", "unique_id": "solix_x1_battery_pack_soh", "slave": 1, "address": 10257, "input_type": "input", "unit_of_measurement": "%", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Battery Daily Charge Energy", "unique_id": "solix_x1_battery_daily_charge_energy", "slave": 1, "address": 10258, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Battery Daily Discharge Energy", "unique_id": "solix_x1_battery_daily_discharge_energy", "slave": 1, "address": 10260, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Battery Total Pack Charge Energy", "unique_id": "solix_x1_battery_total_pack_charge_energy", "slave": 1, "address": 10262, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Battery Total Pack Discharge Energy", "unique_id": "solix_x1_battery_total_pack_discharge_energy", "slave": 1, "address": 10264, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Battery Alarm 1", "unique_id": "solix_x1_battery_alarm_1", "slave": 1, "address": 10266, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Battery Alarm 2", "unique_id": "solix_x1_battery_alarm_2", "slave": 1, "address": 10267, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Battery Alarm 3", "unique_id": "solix_x1_battery_alarm_3", "slave": 1, "address": 10268, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Battery Alarm 4", "unique_id": "solix_x1_battery_alarm_4", "slave": 1, "address": 10269, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Battery Alarm 5", "unique_id": "solix_x1_battery_alarm_5", "slave": 1, "address": 10270, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Battery Alarm 6", "unique_id": "solix_x1_battery_alarm_6", "slave": 1, "address": 10271, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Battery Alarm 7", "unique_id": "solix_x1_battery_alarm_7", "slave": 1, "address": 10272, "input_type": "input", "data_type": "uint16", "scale": 1},
    {"name": "Solix X1 Battery Alarm 8", "unique_id": "solix_x1_battery_alarm_8", "slave": 1, "address": 10273, "input_type": "input", "data_type": "uint16", "scale": 1, "# CLASSIFICATION 9": "METER - METER INFORMATION"},
    {"name": "Solix X1 Meter Type", "unique_id": "solix_x1_meter_type", "slave": 1, "address": 10630, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Meter Status", "unique_id": "solix_x1_meter_status", "slave": 1, "address": 10631, "input_type": "input", "data_type": "uint16", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Meter Phase A Voltage", "unique_id": "solix_x1_meter_phase_a_voltage", "slave": 1, "address": 10632, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Meter Phase B Voltage", "unique_id": "solix_x1_meter_phase_b_voltage", "slave": 1, "address": 10633, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Meter Phase C Voltage", "unique_id": "solix_x1_meter_phase_c_voltage", "slave": 1, "address": 10634, "input_type": "input", "unit_of_measurement": "V", "data_type": "uint16", "scale": 0.1, "precision": 1, "state_class": "measurement", "device_class": "voltage"},
    {"name": "Solix X1 Meter Phase A Current", "unique_id": "solix_x1_meter_phase_a_current", "slave": 1, "address": 10635, "input_type": "input", "unit_of_measurement": "A", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 Meter Phase B Current", "unique_id": "solix_x1_meter_phase_b_current", "slave": 1, "address": 10636, "input_type": "input", "unit_of_measurement": "A", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 Meter Phase C Current", "unique_id": "solix_x1_meter_phase_c_current", "slave": 1, "address": 10637, "input_type": "input", "unit_of_measurement": "A", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement", "device_class": "current"},
    {"name": "Solix X1 Meter Phase A Active Power", "unique_id": "solix_x1_meter_phase_a_active_power", "slave": 1, "address": 10638, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Meter Phase B Active Power", "unique_id": "solix_x1_meter_phase_b_active_power", "slave": 1, "address": 10640, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Meter Phase C Active Power", "unique_id": "solix_x1_meter_phase_c_active_power", "slave": 1, "address": 10642, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Meter Total Active Power", "unique_id": "solix_x1_meter_total_active_power", "slave": 1, "address": 10644, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement", "device_class": "power"},
    {"name": "Solix X1 Meter Total Reactive Power", "unique_id": "solix_x1_meter_total_reactive_power", "slave": 1, "address": 10646, "input_type": "input", "unit_of_measurement": "W", "data_type": "int32", "swap": "word", "scale": 1, "state_class": "measurement"},
    {"name": "Solix X1 Meter Power Factor", "unique_id": "solix_x1_meter_power_factor", "slave": 1, "address": 10648, "input_type": "input", "data_type": "int16", "scale": 0.001, "precision": 3, "state_class": "measurement"},
    {"name": "Solix X1 Meter Grid Frequency", "unique_id": "solix_x1_meter_grid_frequency", "slave": 1, "address": 10649, "input_type": "input", "unit_of_measurement": "Hz", "data_type": "uint16", "scale": 0.01, "precision": 2, "state_class": "measurement"},
    {"name": "Solix X1 Meter Phase A Forward Active Energy", "unique_id": "solix_x1_meter_phase_a_forward_active_energy", "slave": 1, "address": 10650, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Meter Phase B Forward Active Energy", "unique_id": "solix_x1_meter_phase_b_forward_active_energy", "slave": 1, "address": 10652, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Meter Phase C Forward Active Energy", "unique_id": "solix_x1_meter_phase_c_forward_active_energy", "slave": 1, "address": 10654, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Meter Total Forward Active Energy", "unique_id": "solix_x1_meter_total_forward_active_energy", "slave": 1, "address": 10656, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Meter Phase A Reverse Active Energy", "unique_id": "solix_x1_meter_phase_a_reverse_active_energy", "slave": 1, "address": 10658, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Meter Phase B Reverse Active Energy", "unique_id": "solix_x1_meter_phase_b_reverse_active_energy", "slave": 1, "address": 10660, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Meter Phase C Reverse Active Energy", "unique_id": "solix_x1_meter_phase_c_reverse_active_energy", "slave": 1, "address": 10662, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
    {"name": "Solix X1 Meter Total Reverse Active Energy", "unique_id": "solix_x1_meter_total_reverse_active_energy", "slave": 1, "address": 10664, "input_type": "input", "unit_of_measurement": "kWh", "data_type": "uint32", "swap": "word", "scale": 0.01, "precision": 2, "state_class": "total_increasing", "device_class": "energy"},
]

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = []
    for s_conf in SENSOR_TYPES:
        entities.append(AnkerSolixSensor(coordinator, entry.data[CONF_NAME], s_conf))
        
    async_add_entities(entities)


class AnkerSolixSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_name, config):
        super().__init__(coordinator)
        self._config = config
        
        # Force exact match with previous YAML configuration
        self._attr_name = config['name']
        self._attr_unique_id = config['unique_id']
        
        # Map device classes
        dc = config.get("device_class")
        if dc:
            try:
                self._attr_device_class = SensorDeviceClass(dc)
            except ValueError:
                pass
                
        # Map state classes
        sc = config.get("state_class")
        if sc:
            try:
                self._attr_state_class = SensorStateClass(sc)
            except ValueError:
                pass
                
        self._attr_native_unit_of_measurement = config.get("unit_of_measurement")

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id.split("_")[0])},
            "name": self._attr_name.split(" ")[0],
            "manufacturer": "Anker",
            "model": "Solix X1",
        }

    @property
    def native_value(self):
        registers = self.coordinator.data.get(self._config["unique_id"])
        if not registers:
            return None
            
        # VERY basic processing for the scaffold - you would implement proper
        # word swapping, signed/unsigned int parsing, and scaling here.
        if len(registers) == 1:
            val = registers[0]
        else:
            val = (registers[0] << 16) + registers[1]
            
        scale = self._config.get("scale", 1)
        if scale != 1:
            val = val * float(scale)
            
        precision = self._config.get("precision")
        if precision is not None:
            return round(val, int(precision))
            
        return val
