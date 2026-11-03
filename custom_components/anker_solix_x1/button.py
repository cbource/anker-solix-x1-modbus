"""Button platform for the Anker Solix X1 Modbus integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import async_write_registers, build_device_info
from .unique_ids import build_unique_id, uses_legacy_unique_ids

BUTTON_TYPES = [
    {
        "name": "Solix X1 Switch On",
        "unique_id": "solix_x1_switch_on",
        "address": 10073,
        "payload": 1,
        "icon": "mdi:power-on",
    },
    {
        "name": "Solix X1 Switch Off",
        "unique_id": "solix_x1_switch_off",
        "address": 10073,
        "payload": 2,
        "icon": "mdi:power-off",
    },
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up button entities from a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    async_add_entities(
        AnkerSolixButton(
            client, config, entry.entry_id, uses_legacy_unique_ids(entry.data)
        )
        for config in BUTTON_TYPES
    )


class AnkerSolixButton(ButtonEntity):
    """Button that writes a command value to the inverter."""

    def __init__(self, client, config: dict, entry_id: str, legacy: bool) -> None:
        self.client = client
        self._entry_id = entry_id
        self._attr_name = config["name"]
        self._attr_unique_id = build_unique_id(config["unique_id"], entry_id, legacy)
        self._attr_icon = config["icon"]
        self._address = config["address"]
        self._payload = config["payload"]

    async def async_press(self) -> None:
        """Send the command to the inverter."""
        await async_write_registers(
            self.client, self._address, [self._payload], self._attr_name
        )

    @property
    def device_info(self):
        """Group the button under the inverter device."""
        return build_device_info(self._entry_id)
