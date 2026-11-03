"""Select platform for the Anker Solix X1 Modbus integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .entity import async_write_registers, build_device_info
from .unique_ids import build_unique_id, uses_legacy_unique_ids

WORK_MODES = {
    0: "Self-consumption",
    1: "TOU",
    2: "Backup only",
    3: "3rd party control",
    4: "User-Defined",
    5: "Socket Aggregation"
}

LIMIT_MODES = {
    0: "Disable",
    1: "Percentage of rated power",
    2: "Fixed power"
}

SELECT_TYPES = [
    {
        "name": "Solix X1 Work Mode Control",
        "unique_id": "solix_x1_work_mode_control",
        "address": 10064,
        "options": WORK_MODES,
    },
    {
        "name": "Solix X1 Export Power Limit Mode Control",
        "unique_id": "solix_x1_export_power_limit_mode_control",
        "address": 10074,
        "options": LIMIT_MODES,
    },
    {
        "name": "Solix X1 Import Power Limit Mode Control",
        "unique_id": "solix_x1_import_power_limit_mode_control",
        "address": 10077,
        "options": LIMIT_MODES,
    },
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]
    legacy = uses_legacy_unique_ids(entry.data)
    entities = [
        AnkerSolixSelect(coordinator, client, config, entry.entry_id, legacy)
        for config in SELECT_TYPES
    ]
    async_add_entities(entities)

class AnkerSolixSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator, client, config, entry_id, legacy=True):
        super().__init__(coordinator)
        self.client = client
        self._entry_id = entry_id
        self._config = config
        self._attr_name = config["name"]
        self._attr_unique_id = build_unique_id(config["unique_id"], entry_id, legacy)
        self._attr_options = list(config["options"].values())
        self._address = config["address"]
        self._options_map = config["options"]
        self._reverse_map = {v: k for k, v in self._options_map.items()}

    @property
    def current_option(self) -> str | None:
        raw_data = self.coordinator.data
        if raw_data is None:
            return None
        # The sensor data has the original unique_id without "_control"
        sensor_unique_id = self._config["unique_id"].replace("_control", "")
        # Export/Import in sensor.py have slightly different names:
        if "export" in sensor_unique_id:
            sensor_unique_id = "solix_x1_export_power_limit_control_mode"
        elif "import" in sensor_unique_id:
            sensor_unique_id = "solix_x1_import_power_limit_control_mode"

        registers = raw_data.get(sensor_unique_id)
        if registers and len(registers) > 0:
            val = registers[0]
            return self._options_map.get(val)
        return None

    async def async_select_option(self, option: str) -> None:
        """Write the selected option to the inverter."""
        val = self._reverse_map.get(option)
        if val is None:
            raise HomeAssistantError(f"Unknown option {option!r}")
        await async_write_registers(
            self.client, self._address, [val], self._attr_name
        )
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        """Group the select under the inverter device."""
        return build_device_info(self._entry_id)
