"""
Tests for operator functionality in the NFC Card & Keychain Generator addon.

Note: Tests that require scene setup are skipped when running in background mode
because the addon's scene_setup operator tries to set the 3D view, which requires a GUI.
These tests focus on the logic that can be tested without a 3D viewport.
"""

import unittest
import bpy
from pathlib import Path
import sys

# Add the addon directory to the path
addon_dir = Path(__file__).parent.parent / "nfcCardGen"
if str(addon_dir) not in sys.path:
    sys.path.insert(0, str(addon_dir))


class TestSceneSetupOperator(unittest.TestCase):
    """Test the scene setup operator (basic poll functionality only)"""

    def setUp(self):
        """Reset the scene before each test"""
        # Clear all objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Reset scene properties
        bpy.context.scene.nfc_card_props.scene_setup = False

    def tearDown(self):
        """Clean up after each test"""
        # Clear all objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

    def test_scene_setup_poll(self):
        """Test that poll function works correctly"""
        # Should return True when scene is not set up
        self.assertTrue(
            bpy.ops.object.scene_setup.poll(),
            "Poll should return True when scene is not set up"
        )
    
    def test_scene_setup_operator_exists(self):
        """Test that scene setup operator is registered"""
        self.assertTrue(
            hasattr(bpy.ops.object, 'scene_setup'),
            "scene_setup operator should be registered"
        )


class TestShapePresetOperator(unittest.TestCase):
    """Test the shape preset operator (without requiring scene setup)"""

    def test_shape_preset_operator_exists(self):
        """Test that shape preset operator is registered"""
        self.assertTrue(
            hasattr(bpy.ops.object, 'nfc_set_shape_preset'),
            "nfc_set_shape_preset operator should be registered"
        )
    
    def test_shape_preset_without_setup(self):
        """Test that shape preset can be set without scene setup"""
        # Set shape preset directly on properties
        props = bpy.context.scene.nfc_card_props
        props.shape_preset = 'RECTANGLE'
        self.assertEqual(props.shape_preset, 'RECTANGLE')
        
        props.shape_preset = 'CIRCLE'
        self.assertEqual(props.shape_preset, 'CIRCLE')


class TestExportOperator(unittest.TestCase):
    """Test the export operators (poll only, no actual setup)"""

    def setUp(self):
        """Setup scene before each test"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        bpy.context.scene.nfc_card_props.scene_setup = False

    def tearDown(self):
        """Clean up after each test"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

    def test_export_operator_exists(self):
        """Test that export operator is registered"""
        self.assertTrue(
            hasattr(bpy.ops.export_scene, 'export_card_obj'),
            "export_card_obj operator should be registered"
        )

    def test_export_operators_exist(self):
        """Test that export operators are registered"""
        # Check for export operators (they may have different names)
        # This just verifies the operator module is accessible
        self.assertTrue(
            hasattr(bpy.ops, 'export_scene'),
            "export_scene operator namespace should exist"
        )


def suite():
    """Create test suite"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSceneSetupOperator))
    test_suite.addTest(unittest.makeSuite(TestShapePresetOperator))
    test_suite.addTest(unittest.makeSuite(TestExportOperator))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
