"""
Tests for SVG import and processing functionality.
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

from nfcCardGen.svg_import import _find_logo_placer_node_group


class TestSVGImportHelpers(unittest.TestCase):
    """Test SVG import helper functions"""

    def test_find_logo_placer_function_exists(self):
        """Test that _find_logo_placer_node_group function exists"""
        # Just test that the function is importable and callable
        self.assertTrue(callable(_find_logo_placer_node_group),
                        "_find_logo_placer_node_group should be callable")


class TestSVGImportOperator(unittest.TestCase):
    """Test SVG import operator"""

    def test_svg_import_operator_exists(self):
        """Test that SVG import operator is registered"""
        self.assertTrue(
            hasattr(bpy.ops.object, 'import_and_process_svg'),
            "import_and_process_svg operator should be registered"
        )

    def test_svg_design_properties_exist(self):
        """Test that SVG design properties exist"""
        props = bpy.context.scene.nfc_card_props
        
        # Check if design-related properties are accessible
        self.assertTrue(
            hasattr(props, 'offset_x_1') or hasattr(props, 'scale_1'),
            "SVG design properties should exist"
        )


class TestClearDesignOperator(unittest.TestCase):
    """Test clear design operator"""

    def test_clear_design_operator_exists(self):
        """Test that clear design operator is registered"""
        self.assertTrue(
            hasattr(bpy.ops.object, 'clear_design'),
            "clear_design operator should be registered"
        )


def suite():
    """Create test suite"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSVGImportHelpers))
    test_suite.addTest(unittest.makeSuite(TestSVGImportOperator))
    test_suite.addTest(unittest.makeSuite(TestClearDesignOperator))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
