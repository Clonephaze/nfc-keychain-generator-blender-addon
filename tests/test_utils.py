"""
Tests for utility functions in the NFC Card & Keychain Generator addon.
"""

import unittest
import bpy
from pathlib import Path
import sys

# Add the addon directory to the path
addon_dir = Path(__file__).parent.parent / "nfcCardGen"
if str(addon_dir) not in sys.path:
    sys.path.insert(0, str(addon_dir))

# Add parent directory for module import
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from nfcCardGen.utils import (
    OBJECT_NAME,
    MOD_OPT_MAPPING,
    DRIVER_MAPPINGS,
    update_modifier_option,
)


class TestConstants(unittest.TestCase):
    """Test that constants are properly defined"""

    def test_object_name_constant(self):
        """Test OBJECT_NAME constant"""
        self.assertEqual(OBJECT_NAME, "Card", "OBJECT_NAME should be 'Card'")

    def test_mod_opt_mapping_exists(self):
        """Test MOD_OPT_MAPPING dictionary exists and has entries"""
        self.assertIsInstance(MOD_OPT_MAPPING, dict)
        self.assertGreater(len(MOD_OPT_MAPPING), 0)

    def test_mod_opt_mapping_structure(self):
        """Test MOD_OPT_MAPPING has correct structure"""
        for key, value in MOD_OPT_MAPPING.items():
            self.assertIsInstance(key, str, f"Key {key} should be a string")
            self.assertIsInstance(value, tuple, f"Value for {key} should be a tuple")
            self.assertEqual(len(value), 2, f"Value for {key} should have 2 elements")

    def test_driver_mappings_exists(self):
        """Test DRIVER_MAPPINGS dictionary exists"""
        self.assertIsInstance(DRIVER_MAPPINGS, dict)

    def test_common_mod_opt_mappings(self):
        """Test that common modifier options are mapped"""
        required_keys = [
            "SHAPE_CHOICE",
            "CORNER_RADII",
            "KEYCHAIN_CHOICE",
            "INITIAL_HEIGHT",
            "MAGNET_CHOICE",
            "NFC_CHOICE",
            "BEVEL_AMOUNT",
        ]
        
        for key in required_keys:
            self.assertIn(
                key,
                MOD_OPT_MAPPING,
                f"{key} should be in MOD_OPT_MAPPING"
            )


class TestModifierUtils(unittest.TestCase):
    """Test modifier utility functions (without scene setup)"""

    def test_update_modifier_option_invalid_name(self):
        """Test updating a modifier option with invalid logical name"""
        result = update_modifier_option("INVALID_NAME", 5.0)
        
        # Should return False for invalid name
        self.assertFalse(result, "Invalid logical name should return False")
    
    def test_update_modifier_option_valid_name_without_card(self):
        """Test that update_modifier_option handles missing Card object gracefully"""
        # Without Card object, should return False or handle gracefully
        result = update_modifier_option("CORNER_RADII", 5.0)
        
        # Should be boolean (might be False if Card doesn't exist)
        self.assertIsInstance(result, bool)


class TestEnumConversion(unittest.TestCase):
    """Test enum to integer conversion for geometry nodes"""

    def test_mag_shape_enum_conversion_logic(self):
        """Test MAG_SHAPE enum to integer conversion logic"""
        # Test that the function accepts both string and int values
        # (without requiring Card object to exist)
        result_circle = update_modifier_option("MAG_SHAPE", "CIRCLE")
        result_hex = update_modifier_option("MAG_SHAPE", "HEXAGON")
        
        # Both should return boolean
        self.assertIsInstance(result_circle, bool)
        self.assertIsInstance(result_hex, bool)
        
        # Test integer values directly
        result_0 = update_modifier_option("MAG_SHAPE", 0)
        result_1 = update_modifier_option("MAG_SHAPE", 1)
        
        self.assertIsInstance(result_0, bool)
        self.assertIsInstance(result_1, bool)


def suite():
    """Create test suite"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestConstants))
    test_suite.addTest(unittest.makeSuite(TestModifierUtils))
    test_suite.addTest(unittest.makeSuite(TestEnumConversion))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
