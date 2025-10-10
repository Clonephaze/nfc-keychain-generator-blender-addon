"""
Tests for QR code generation functionality.
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

from nfcCardGen.qr_generator import QRCodeGenerator


class TestQRCodeGenerator(unittest.TestCase):
    """Test the QR code generator functionality"""

    def test_segno_available(self):
        """Test that segno library is available"""
        self.assertTrue(
            QRCodeGenerator.is_segno_available(),
            "Segno library should be available"
        )

    def test_qr_type_constants(self):
        """Test that QR type constants are defined"""
        self.assertEqual(QRCodeGenerator.QR_TYPE_TEXT, "TEXT")
        self.assertEqual(QRCodeGenerator.QR_TYPE_WIFI, "WIFI")
        self.assertEqual(QRCodeGenerator.QR_TYPE_CONTACT, "CONTACT")
        self.assertEqual(QRCodeGenerator.QR_TYPE_EMAIL, "EMAIL")


class TestTextQROperator(unittest.TestCase):
    """Test text/URL QR code generation operator"""

    def test_text_qr_operator_exists(self):
        """Test that text QR operator is registered"""
        self.assertTrue(
            hasattr(bpy.ops.object, 'generate_text_qr'),
            "generate_text_qr operator should be registered"
        )

    def test_qr_properties_exist(self):
        """Test that QR-related properties exist"""
        props = bpy.context.scene.nfc_card_props
        
        # Check if QR-related properties are accessible (they have _1 and _2 suffixes)
        self.assertTrue(
            hasattr(props, 'qr_text_content_1') or hasattr(props, 'qr_mode_1'),
            "QR-related properties should exist"
        )


class TestWifiQROperator(unittest.TestCase):
    """Test WiFi QR code generation operator"""

    def test_wifi_qr_operator_exists(self):
        """Test that WiFi QR operator is registered"""
        self.assertTrue(
            hasattr(bpy.ops.object, 'generate_wifi_qr'),
            "generate_wifi_qr operator should be registered"
        )


class TestContactQROperator(unittest.TestCase):
    """Test contact (vCard) QR code generation operator"""

    def test_contact_qr_operator_exists(self):
        """Test that contact QR operator is registered"""
        self.assertTrue(
            hasattr(bpy.ops.object, 'generate_contact_qr'),
            "generate_contact_qr operator should be registered"
        )


class TestEmailQROperator(unittest.TestCase):
    """Test email QR code generation operator"""

    def test_email_qr_operator_exists(self):
        """Test that email QR operator is registered"""
        self.assertTrue(
            hasattr(bpy.ops.object, 'generate_email_qr'),
            "generate_email_qr operator should be registered"
        )


def suite():
    """Create test suite"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestQRCodeGenerator))
    test_suite.addTest(unittest.makeSuite(TestTextQROperator))
    test_suite.addTest(unittest.makeSuite(TestWifiQROperator))
    test_suite.addTest(unittest.makeSuite(TestContactQROperator))
    test_suite.addTest(unittest.makeSuite(TestEmailQROperator))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
