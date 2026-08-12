"""Anker Solix X1 Modbus Integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .sensor import SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

REGISTER_BLOCKS = [
    (10000, 50, "input"),
    (10124, 33, "input"),
    (10167, 47, "input"),
    (10224, 15, "input"),
    (10249, 25, "input"),
    (10630, 35, "input"),
    (10064, 17, "holding"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Anker Solix X1 from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    # use options if available, else data
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, 30)
    )

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

    async def async_update_data() -> dict[str, list[int]]:
        """Fetch data from the inverter."""
        if not client.connected:
            await client.connect()
            if not client.connected:
                raise UpdateFailed("Modbus client is not connected")

        raw: dict[tuple[str, int], int] = {}
        try:
            for start_addr, count, reg_type in REGISTER_BLOCKS:
                if reg_type == "holding":
                    result = await client.read_holding_registers(start_addr, count, slave=1)
                else:
                    result = await client.read_input_registers(start_addr, count, slave=1)

                if result.isError():
                    _LOGGER.warning("Failed to read %s block at %s", reg_type, start_addr)
                    continue

                for i, val in enumerate(result.registers):
                    raw[(reg_type, start_addr + i)] = val
        except ModbusException as e:
            _LOGGER.error("Modbus error during update: %s", e)
            raise UpdateFailed(f"Modbus error: {e}") from e
        except Exception as e:
            _LOGGER.error("Unexpected error during update: %s", e)
            raise UpdateFailed(f"Unexpected error: {e}") from e

        data: dict[str, list[int]] = {}
        for s in SENSOR_TYPES:
            unique_id = s["unique_id"]
            address = s["address"]
            input_type = s["input_type"]
            data_type = s["data_type"]
            
            reg_count = 2 if data_type in ("int32", "uint32") else 1
            
            try:
                registers = [raw[(input_type, address + i)] for i in range(reg_count)]
                data[unique_id] = registers
            except KeyError:
                _LOGGER.debug("Missing registers for sensor %s at %s", unique_id, address)
                continue
                
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

    # Add update listener for options
    entry.async_on_unload(entry.add_update_listener(async_options_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        client = data["client"]
        client.close()
    return unload_ok
