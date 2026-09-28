import logging
from pymodbus.exceptions import ModbusException
from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

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
    entities = [AnkerSolixSelect(coordinator, client, config) for config in SELECT_TYPES]
    async_add_entities(entities)

class AnkerSolixSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator, client, config):
        super().__init__(coordinator)
        self.client = client
        self._config = config
        self._attr_name = config["name"]
        self._attr_unique_id = config["unique_id"]
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
        val = self._reverse_map.get(option)
        if val is not None:
            try:
                if not self.client.connected:
                    await self.client.connect()
                result = await self.client.write_register(self._address, val, device_id=1)
                if result.isError():
                    _LOGGER.error("Failed to write select %s at %s", self._attr_name, self._address)
                else:
                    await self.coordinator.async_request_refresh()
            except ModbusException as e:
                _LOGGER.error("Modbus error writing %s: %s", self._attr_name, e)

    @property
    def device_info(self):
        from homeassistant.helpers.device_registry import DeviceInfo
        from .const import DOMAIN
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id if hasattr(self, 'coordinator') else self._entry_id)},
            name="Anker Solix X1",
            manufacturer="Anker",
        )
