"""Number platform for the Anker Solix X1 Modbus integration."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .entity import async_write_registers, build_device_info
from .unique_ids import build_unique_id, uses_legacy_unique_ids

NUMBER_TYPES = [
    {
        "name": "Solix X1 Active Power Control Percentage",
        "unique_id": "solix_x1_active_power_control_percentage_control",
        "address": 10069,
        "unit_of_measurement": "%",
        "min": 0,
        "max": 100,
        "sensor_id": "solix_x1_active_power_control___percentage"
    },
    {
        "name": "Solix X1 Reactive Power Control Percentage",
        "unique_id": "solix_x1_reactive_power_control_percentage_control",
        "address": 10070,
        "unit_of_measurement": "%",
        "min": 0,
        "max": 100,
        "sensor_id": "solix_x1_reactive_power_control___percentage"
    },
    {
        "name": "Solix X1 Battery Charge/Discharge Control",
        "unique_id": "solix_x1_battery_charge_discharge_control_control",
        "address": 10071,
        "unit_of_measurement": "W",
        "min": -20000,
        "max": 20000,
        "sensor_id": "solix_x1_battery_charge_discharge_control",
        "is_32bit": True
    },
    {
        "name": "Solix X1 Export Power Limit Control Value",
        "unique_id": "solix_x1_export_power_limit_control_value_control",
        "address": 10075,
        "unit_of_measurement": "W",
        "min": 0,
        "max": 50000,
        "sensor_id": "solix_x1_export_power_limit_control_value",
        "is_32bit": True
    },
    {
        "name": "Solix X1 Import Power Limit Control Value",
        "unique_id": "solix_x1_import_power_limit_control_value_control",
        "address": 10078,
        "unit_of_measurement": "W",
        "min": 0,
        "max": 50000,
        "sensor_id": "solix_x1_import_power_limit_control_value",
        "is_32bit": True
    },
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]
    legacy = uses_legacy_unique_ids(entry.data)
    entities = [
        AnkerSolixNumber(coordinator, client, config, entry.entry_id, legacy)
        for config in NUMBER_TYPES
    ]
    async_add_entities(entities)

class AnkerSolixNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, client, config, entry_id, legacy=True):
        super().__init__(coordinator)
        self.client = client
        self._entry_id = entry_id
        self._config = config
        self._attr_name = config["name"]
        self._attr_unique_id = build_unique_id(config["unique_id"], entry_id, legacy)
        self._attr_native_unit_of_measurement = config.get("unit_of_measurement")
        self._attr_native_min_value = config["min"]
        self._attr_native_max_value = config["max"]
        self._address = config["address"]
        self._is_32bit = config.get("is_32bit", False)
        self._sensor_id = config["sensor_id"]

    @property
    def native_value(self) -> float | None:
        raw_data = self.coordinator.data
        if raw_data is None:
            return None
        registers = raw_data.get(self._sensor_id)
        if registers and len(registers) > 0:
            if self._is_32bit and len(registers) >= 2:
                # The X1 stores 32-bit values low word first (same as the
                # swap="word" decoding of these registers in sensor.py).
                val = (registers[1] << 16) + registers[0]
                # Handle signed 32-bit if needed (charge/discharge is signed)
                if self._sensor_id == "solix_x1_battery_charge_discharge_control":
                    if val > 2147483647:
                        val -= 4294967296
                return val
            else:
                val = registers[0]
                if self._sensor_id in ["solix_x1_active_power_control___percentage", "solix_x1_reactive_power_control___percentage"]:
                    if val > 32767:
                        val -= 65536
                return val
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Write the value to the inverter."""
        int_val = int(value)
        if self._is_32bit:
            if int_val < 0:
                int_val += 4294967296
            # Low word first, matching how the X1 stores 32-bit values.
            registers = [int_val & 0xFFFF, (int_val >> 16) & 0xFFFF]
        else:
            if int_val < 0:
                int_val += 65536
            registers = [int_val]

        await async_write_registers(
            self.client, self._address, registers, self._attr_name
        )
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        """Group the number under the inverter device."""
        return build_device_info(self._entry_id)
