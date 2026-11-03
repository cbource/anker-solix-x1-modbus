"""Tests for the multi-inverter unique ID logic (no Home Assistant needed).

Run: python -m unittest discover -s tests
"""

import importlib.util
import pathlib
import unittest

_PATH = (
    pathlib.Path(__file__).parent.parent
    / "custom_components"
    / "anker_solix_x1"
    / "unique_ids.py"
)
_spec = importlib.util.spec_from_file_location("unique_ids", _PATH)
unique_ids = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(unique_ids)

FLAG = unique_ids.CONF_LEGACY_UNIQUE_IDS
decide = unique_ids.should_use_legacy_unique_ids


class BuildUniqueIdTests(unittest.TestCase):
    def test_legacy_keeps_bare_id(self):
        self.assertEqual(
            unique_ids.build_unique_id("solix_x1_grid_power", "A", True),
            "solix_x1_grid_power",
        )

    def test_other_entries_get_suffix(self):
        self.assertEqual(
            unique_ids.build_unique_id("solix_x1_grid_power", "B", False),
            "solix_x1_grid_power_B",
        )

    def test_missing_flag_defaults_to_legacy(self):
        self.assertTrue(unique_ids.uses_legacy_unique_ids({}))
        self.assertFalse(unique_ids.uses_legacy_unique_ids({FLAG: False}))


class DecisionTests(unittest.TestCase):
    def test_fresh_install_first_entry_is_legacy(self):
        self.assertTrue(decide("A", [("A", {})], []))

    def test_upgrade_single_existing_entry_keeps_bare_ids(self):
        registry = [("A", "solix_x1_grid_power"), ("A", "solix_x1_work_mode_control")]
        self.assertTrue(decide("A", [("A", {})], registry))

    def test_second_entry_after_upgrade_is_suffixed(self):
        registry = [("A", "solix_x1_grid_power")]
        others = [("A", {FLAG: True}), ("B", {})]
        self.assertFalse(decide("B", others, registry))

    def test_second_entry_detected_from_registry_alone(self):
        registry = [("A", "solix_x1_grid_power")]
        self.assertFalse(decide("B", [("A", {}), ("B", {})], registry))

    def test_second_entry_detected_from_flag_alone(self):
        self.assertFalse(decide("B", [("A", {FLAG: True}), ("B", {})], []))

    def test_concurrent_first_setup_only_one_wins(self):
        entries = {"A": {}, "B": {}}
        winners = []
        for entry_id in ("A", "B"):
            legacy = decide(entry_id, list(entries.items()), [])
            entries[entry_id] = {FLAG: legacy}
            winners.append(legacy)
        self.assertEqual(winners, [True, False])

    def test_suffixed_entities_of_other_entry_do_not_block(self):
        registry = [("B", "solix_x1_grid_power_B")]
        self.assertTrue(decide("A", [("A", {}), ("B", {FLAG: False})], registry))

    def test_original_removed_then_new_entry_reclaims_bare_ids(self):
        self.assertTrue(decide("C", [("C", {})], []))

    def test_unique_ids_never_collide_across_entries(self):
        base = "solix_x1_grid_power"
        a = unique_ids.build_unique_id(base, "A", True)
        b = unique_ids.build_unique_id(base, "B", False)
        c = unique_ids.build_unique_id(base, "C", False)
        self.assertEqual(len({a, b, c}), 3)


if __name__ == "__main__":
    unittest.main()
