"""
Tests for property definitions and updates in the NFC Card & Keychain Generator addon.
"""

import unittest
import bpy
from pathlib import Path
import sys

# Add the addon directory to the path
addon_dir = Path(__file__).parent.parent / "nfcCardGen"
if str(addon_dir) not in sys.path:
    sys.path.insert(0, str(addon_dir))


class TestPropertyDefinitions(unittest.TestCase):
    """Test that all properties are properly defined"""

    def setUp(self):
        """Setup before each test"""
        # Ensure the addon is loaded
        pass

    def test_property_group_exists(self):
        """Test that the nfc_card_props property group exists"""
        self.assertTrue(
            hasattr(bpy.context.scene, 'nfc_card_props'),
            "Scene should have nfc_card_props property group"
        )

    def test_scene_setup_property(self):
        """Test scene_setup boolean property"""
        props = bpy.context.scene.nfc_card_props
        self.assertIsInstance(
            props.scene_setup,
            bool,
            "scene_setup should be a boolean property"
        )

    def test_shape_preset_property(self):
        """Test shape_preset enum property"""
        props = bpy.context.scene.nfc_card_props
        
        # Should have valid default
        self.assertIn(
            props.shape_preset,
            ['RECTANGLE', 'CIRCLE'],
            "shape_preset should have a valid value"
        )

    def test_corner_radius_property(self):
        """Test corner_radius float property"""
        props = bpy.context.scene.nfc_card_props
        
        # Check that it's a valid number
        self.assertIsInstance(
            props.corner_radius,
            float,
            "corner_radius should be a float"
        )
        
        # Should be within reasonable bounds
        self.assertGreaterEqual(props.corner_radius, 0.0)

    def test_keychain_choice_property(self):
        """Test keychain_choice boolean property"""
        props = bpy.context.scene.nfc_card_props
        
        self.assertIsInstance(
            props.keychain_choice,
            bool,
            "keychain_choice should be a boolean property"
        )

    def test_initial_height_property(self):
        """Test initial_height float property"""
        props = bpy.context.scene.nfc_card_props
        
        self.assertIsInstance(
            props.initial_height,
            float,
            "initial_height should be a float"
        )
        self.assertGreater(props.initial_height, 0.0)

    def test_magnet_properties(self):
        """Test magnet-related properties"""
        props = bpy.context.scene.nfc_card_props
        
        # magnet_choice is a boolean property
        self.assertIsInstance(
            props.magnet_choice,
            bool,
            "magnet_choice should be a boolean property"
        )
        
        # mag_shape is an enum property
        self.assertIn(
            props.mag_shape,
            ['CIRCLE', 'HEXAGON'],
            "mag_shape should have a valid value"
        )

    def test_bevel_properties(self):
        """Test bevel-related properties"""
        props = bpy.context.scene.nfc_card_props
        
        self.assertIsInstance(props.bevel_amount, float)
        self.assertIsInstance(props.bevel_segments, int)
        self.assertGreater(props.bevel_segments, 0)


class TestPropertyUpdates(unittest.TestCase):
    """Test that property updates work correctly (without scene setup)"""

    def test_corner_radius_update(self):
        """Test that corner_radius updates work"""
        props = bpy.context.scene.nfc_card_props
        
        # Change value
        props.corner_radius = 5.0
        
        # Verify change
        self.assertEqual(props.corner_radius, 5.0)

    def test_shape_preset_update(self):
        """Test that shape_preset updates work"""
        props = bpy.context.scene.nfc_card_props
        
        # Change to CIRCLE
        props.shape_preset = 'CIRCLE'
        self.assertEqual(props.shape_preset, 'CIRCLE')
        
        # Change to RECTANGLE
        props.shape_preset = 'RECTANGLE'
        self.assertEqual(props.shape_preset, 'RECTANGLE')

    def test_keychain_choice_update(self):
        """Test keychain_choice property updates"""
        props = bpy.context.scene.nfc_card_props
        
        # keychain_choice is a boolean, test True/False
        props.keychain_choice = True
        self.assertEqual(props.keychain_choice, True)
        
        props.keychain_choice = False
        self.assertEqual(props.keychain_choice, False)

    def test_magnet_choice_update(self):
        """Test magnet_choice property updates"""
        props = bpy.context.scene.nfc_card_props
        
        # magnet_choice is a boolean, test True/False
        props.magnet_choice = True
        self.assertEqual(props.magnet_choice, True)
        
        props.magnet_choice = False
        self.assertEqual(props.magnet_choice, False)

    def test_multiple_property_updates(self):
        """Test that multiple property updates work"""
        props = bpy.context.scene.nfc_card_props
        
        # Make several changes
        props.corner_radius = 3.0
        props.initial_height = 2.5
        props.keychain_choice = True
        props.magnet_choice = True
        
        # Verify all changes were applied
        self.assertEqual(props.corner_radius, 3.0)
        self.assertEqual(props.initial_height, 2.5)
        self.assertEqual(props.keychain_choice, True)
        self.assertEqual(props.magnet_choice, True)


class TestPropertyBounds(unittest.TestCase):
    """Test that properties respect their defined bounds"""

    def test_corner_radius_bounds(self):
        """Test corner_radius stays within bounds"""
        props = bpy.context.scene.nfc_card_props
        
        # Try to set negative (should clamp to 0 or min value)
        props.corner_radius = -5.0
        self.assertGreaterEqual(props.corner_radius, 0.0)

    def test_bevel_segments_bounds(self):
        """Test bevel_segments stays within bounds"""
        props = bpy.context.scene.nfc_card_props
        
        # Try to set to 0 (should clamp to minimum)
        props.bevel_segments = 0
        self.assertGreater(props.bevel_segments, 0)
        
        # Try a valid value
        props.bevel_segments = 4
        self.assertEqual(props.bevel_segments, 4)


def suite():
    """Create test suite"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestPropertyDefinitions))
    test_suite.addTest(unittest.makeSuite(TestPropertyUpdates))
    test_suite.addTest(unittest.makeSuite(TestPropertyBounds))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
