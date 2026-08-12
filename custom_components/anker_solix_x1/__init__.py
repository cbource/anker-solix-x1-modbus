"""Anker Solix X1 Modbus Integration."""

import logging
from datetime import timedelta

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Anker Solix X1 from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, 30)

    client = AsyncModbusTcpClient(host, port=port)

    try:
        await client.connect()
        if not client.connected:
            raise ConfigEntryNotReady(f"Unable to connect to {host}:{port}")
    except ConfigEntryNotReady:
        raise
    except Exception as ex:
        raise ConfigEntryNotReady(
            f"Exception connecting to {host}:{port}: {ex}"
        ) from ex

    from .sensor import SENSOR_TYPES  # noqa: PLC0415

    async def async_update_data():
        """Fetch data from the inverter."""
        if not client.connected:
            await client.connect()
            if not client.connected:
                raise UpdateFailed("Modbus client is not connected")

        data = {}
        try:
            for s in SENSOR_TYPES:
                address = s["address"]
                slave = s.get("slave", 1)
                data_type = s["data_type"]

                count = 1
                if data_type in ("int32", "uint32"):
                    count = 2

                if s.get("input_type") == "holding":
                    result = await client.read_holding_registers(
                        address, count, slave=slave
                    )
                else:
                    result = await client.read_input_registers(
                        address, count, slave=slave
                    )

                if not result.isError():
                    data[s["unique_id"]] = result.registers
                else:
                    _LOGGER.warning("Failed to read register %s", address)
        except ModbusException as e:
            _LOGGER.error("Modbus error during update: %s", e)
            raise UpdateFailed(f"Modbus error: {e}") from e
        except Exception as e:
            _LOGGER.error("Unexpected error during update: %s", e)
            raise UpdateFailed(f"Unexpected error: {e}") from e

        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        client = data["client"]
        client.close()
    return unload_ok
