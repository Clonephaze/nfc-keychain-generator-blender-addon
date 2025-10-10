"""
Test runner for the NFC Card & Keychain Generator addon.

This script runs all tests within Blender. It can be executed from the command line
using Blender's Python API, or from within Blender's scripting workspace.

Usage from command line:
    blender --background --python tests/run_tests.py

Usage from Blender's scripting workspace:
    1. Open this file in Blender's Text Editor
    2. Click "Run Script" or press Alt+P
"""

import sys
import unittest
from pathlib import Path
import bpy

# Add the addon to the path and enable it
addon_dir = Path(__file__).parent.parent / "nfcCardGen"
if str(addon_dir) not in sys.path:
    sys.path.insert(0, str(addon_dir))

# Add the tests directory to the path
tests_dir = Path(__file__).parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

# Try to enable the addon if it's installed
try:
    # Try to enable as an installed addon first
    addon_name = None
    for mod in bpy.context.preferences.addons:
        if 'nfc' in mod.module.lower():
            addon_name = mod.module
            break
    
    if addon_name:
        bpy.ops.preferences.addon_enable(module=addon_name)
        print(f"Enabled addon: {addon_name}")
except Exception as e:
    print(f"Note: Could not enable addon as installed extension: {e}")
    print("Tests will run with direct module imports")

# Import all test modules
import test_operators
import test_properties
import test_qr_generator
import test_svg_import
import test_utils


def run_all_tests(verbosity=2):
    """
    Run all addon tests and return the results.
    
    Args:
        verbosity: Level of detail in test output (0=quiet, 1=normal, 2=verbose)
        
    Returns:
        unittest.TestResult object
    """
    # Create the test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test modules
    suite.addTests(loader.loadTestsFromModule(test_operators))
    suite.addTests(loader.loadTestsFromModule(test_properties))
    suite.addTests(loader.loadTestsFromModule(test_qr_generator))
    suite.addTests(loader.loadTestsFromModule(test_svg_import))
    suite.addTests(loader.loadTestsFromModule(test_utils))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def run_specific_test(module_name, test_class=None, test_method=None, verbosity=2):
    """
    Run a specific test module, class, or method.
    
    Args:
        module_name: Name of the test module (e.g., 'test_operators')
        test_class: Optional class name within the module
        test_method: Optional method name within the class
        verbosity: Level of detail in test output
        
    Returns:
        unittest.TestResult object
    """
    # Import the module
    module = __import__(module_name)
    
    # Create suite based on specificity
    if test_method and test_class:
        # Run specific test method
        suite = unittest.TestSuite()
        test_case = getattr(module, test_class)(test_method)
        suite.addTest(test_case)
    elif test_class:
        # Run specific test class
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(getattr(module, test_class))
    else:
        # Run entire module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def main():
    """Main entry point for the test runner"""
    print("="*70)
    print("NFC Card & Keychain Generator - Test Suite")
    print("="*70)
    print()
    
    # Run all tests
    result = run_all_tests(verbosity=2)
    
    # Print summary
    print()
    print("="*70)
    print("Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
