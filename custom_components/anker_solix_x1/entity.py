"""Shared helpers for the Anker Solix X1 Modbus integration."""

from __future__ import annotations

from collections.abc import Sequence

from pymodbus.exceptions import ModbusException

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

MODBUS_DEVICE_ID = 1


def build_device_info(entry_id: str) -> DeviceInfo:
    """Return the single device record shared by every platform."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name="Anker Solix X1",
        manufacturer="Anker",
        model="Solix X1",
    )


async def async_write_registers(
    client, address: int, values: Sequence[int], label: str
) -> None:
    """Write holding registers and raise if the write did not succeed."""
    try:
        if not client.connected:
            await client.connect()
        if len(values) == 1:
            result = await client.write_register(
                address, values[0], device_id=MODBUS_DEVICE_ID
            )
        else:
            result = await client.write_registers(
                address, list(values), device_id=MODBUS_DEVICE_ID
            )
    except ModbusException as err:
        raise HomeAssistantError(f"Modbus error writing {label}: {err}") from err

    if result.isError():
        raise HomeAssistantError(
            f"The inverter rejected the write to {label} (register {address})"
        )
