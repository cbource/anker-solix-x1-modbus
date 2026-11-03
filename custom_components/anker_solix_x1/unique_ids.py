"""Unique ID handling so several inverters can coexist.

The first config entry keeps the original bare unique IDs (so the YAML
migration and existing entity registry entries keep working). Every further
entry gets its config entry ID appended so its entities do not collide.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

CONF_LEGACY_UNIQUE_IDS = "legacy_unique_ids"


def build_unique_id(base: str, entry_id: str, legacy: bool) -> str:
    """Return the entity unique ID for a config entry."""
    return base if legacy else f"{base}_{entry_id}"


def uses_legacy_unique_ids(data: Mapping) -> bool:
    """Return the stored decision; entries without one keep the bare IDs."""
    return bool(data.get(CONF_LEGACY_UNIQUE_IDS, True))


def should_use_legacy_unique_ids(
    entry_id: str,
    other_entries: Iterable[tuple[str, Mapping]],
    registry_unique_ids: Iterable[tuple[str, str]],
) -> bool:
    """Decide whether this entry may use the bare unique IDs.

    other_entries: (entry_id, data) of the other config entries.
    registry_unique_ids: (config_entry_id, unique_id) of every registered
    entity of this integration.
    """
    for other_id, data in other_entries:
        if other_id != entry_id and data.get(CONF_LEGACY_UNIQUE_IDS) is True:
            return False

    for config_entry_id, unique_id in registry_unique_ids:
        if config_entry_id == entry_id:
            continue
        if not unique_id.endswith(f"_{config_entry_id}"):
            return False

    return True
