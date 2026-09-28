import logging
from pymodbus.exceptions import ModbusException
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

BUTTON_TYPES = [
    {
        "name": "Solix X1 Switch On",
        "unique_id": "solix_x1_switch_on",
        "address": 10073,
        "payload": 1,
        "icon": "mdi:power-on"
    },
    {
        "name": "Solix X1 Switch Off",
        "unique_id": "solix_x1_switch_off",
        "address": 10073,
        "payload": 2,
        "icon": "mdi:power-off"
    },
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    entities = [AnkerSolixButton(client, config, entry.entry_id) for config in BUTTON_TYPES]
    async_add_entities(entities)

class AnkerSolixButton(ButtonEntity):
    def __init__(self, client, config, entry_id):
        self._entry_id = entry_id
        self.client = client
        self._attr_name = config["name"]
        self._attr_unique_id = config["unique_id"]
        self._attr_icon = config["icon"]
        self._address = config["address"]
        self._payload = config["payload"]
        self._entry_id = client._entry_id if hasattr(client, '_entry_id') else 'solix_x1_device'

    async def async_press(self) -> None:
        try:
            if not self.client.connected:
                await self.client.connect()
            result = await self.client.write_register(self._address, self._payload, device_id=1)
            if result.isError():
                _LOGGER.error("Failed to write button %s at %s", self._attr_name, self._address)
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
