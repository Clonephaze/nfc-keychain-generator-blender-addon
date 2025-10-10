# NFC Card & Keychain Generator - Test Suite

This directory contains the test suite for the NFC Card & Keychain Generator Blender addon. The tests are designed to run within Blender using the `bpy` module, without requiring mocks.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── run_tests.py             # Main test runner script
├── test_operators.py        # Tests for operator functionality
├── test_properties.py       # Tests for property definitions and updates
├── test_qr_generator.py     # Tests for QR code generation
├── test_svg_import.py       # Tests for SVG import and processing
├── test_utils.py            # Tests for utility functions
└── README.md                # This file
```

## Running Tests

### Option 1: Command Line (Recommended)

Run all tests from the command line using Blender in background mode:

```powershell
# Windows PowerShell
blender --background --python "tests\run_tests.py"

# With full path
"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python "tests\run_tests.py"
```

```bash
# Linux/macOS
blender --background --python tests/run_tests.py
```

### Option 2: Within Blender's Script Editor

1. Open Blender
2. Switch to the **Scripting** workspace
3. Open `tests/run_tests.py` in the Text Editor
4. Click **Run Script** or press `Alt+P`

### Option 3: Using the Blender Python Console

1. Open Blender
2. Open the Python Console
3. Run:

```python
import sys
sys.path.append(r"C:\Users\Jack\Documents\My Projects\Blender Scripts\NFC-Card-Keychain-w--QR-or-Logo-Placer\tests")
import run_tests
run_tests.main()
```

### Option 4: Run Specific Tests

You can run specific test modules, classes, or methods:

```python
# In Blender's Python console or script
import sys
sys.path.append(r"path\to\tests")
import run_tests

# Run specific module
run_tests.run_specific_test('test_operators', verbosity=2)

# Run specific class
run_tests.run_specific_test('test_operators', test_class='TestSceneSetupOperator', verbosity=2)

# Run specific method
run_tests.run_specific_test('test_operators', 
                           test_class='TestSceneSetupOperator',
                           test_method='test_scene_setup_creates_card_object',
                           verbosity=2)
```

## Test Coverage

### test_operators.py
Tests for all operator functionality including:
- Scene setup operator
- Shape preset operators
- View control operators
- Export operators
- QR code generation operators

### test_properties.py
Tests for property definitions and updates:
- Property group existence and structure
- Property data types and bounds
- Property update callbacks
- Property synchronization with modifiers

### test_qr_generator.py
Tests for QR code generation:
- Segno library availability
- Text/URL QR codes
- WiFi QR codes
- Contact (vCard) QR codes
- Email QR codes

### test_svg_import.py
Tests for SVG import functionality:
- SVG import operator
- Mesh processing functions
- Design slot management
- Manifold mesh validation

### test_utils.py
Tests for utility functions:
- Constants and mappings
- Modifier update functions
- Enum to integer conversions
- Driver setup utilities

## Writing New Tests

### Test Class Template

```python
import unittest
import bpy
from pathlib import Path
import sys

# Add the addon directory to the path
addon_dir = Path(__file__).parent.parent / "nfcCardGen"
if str(addon_dir) not in sys.path:
    sys.path.insert(0, str(addon_dir))

class TestYourFeature(unittest.TestCase):
    """Test description"""

    def setUp(self):
        """Setup before each test"""
        # Clean scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        bpy.context.scene.nfc_card_props.scene_setup = False
        
        # Setup scene if needed
        if bpy.ops.object.scene_setup.poll(bpy.context):
            bpy.ops.object.scene_setup()

    def tearDown(self):
        """Clean up after each test"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

    def test_something(self):
        """Test description"""
        # Your test code here
        self.assertTrue(True, "Test should pass")
```

### Best Practices

1. **Clean State**: Always clean the Blender scene in `setUp()` and `tearDown()`
2. **Descriptive Names**: Use clear, descriptive test method names
3. **Single Purpose**: Each test should test one specific thing
4. **Assertions**: Use appropriate assertion methods (`assertEqual`, `assertIsNotNone`, etc.)
5. **Documentation**: Include docstrings for test classes and methods
6. **Skip When Needed**: Use `self.skipTest()` for tests that require optional dependencies

## Testing with Dependencies

### Segno Library

Some tests require the `segno` library (bundled as a wheel). These tests will automatically skip if segno is not available:

```python
def test_qr_generation(self):
    """Test QR code generation"""
    if not QRCodeGenerator.is_segno_available():
        self.skipTest("Segno library not available")
    
    # Test code here...
```

### File System Access

Tests that need file system access should use Blender's extension paths:

```python
temp_dir = bpy.utils.extension_path_user(__package__, path="temp", create=True)
```

## Continuous Integration

To integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Blender
        run: |
          sudo snap install blender --classic
      
      - name: Run Tests
        run: |
          blender --background --python tests/run_tests.py
```

## Troubleshooting

### Test Failures

If tests fail, check:
1. Is the addon properly installed/enabled?
2. Does the `appendInfo.blend` file exist in the addon directory?
3. Are all dependencies (like segno) available?
4. Is Blender version 4.2 or higher?

### Import Errors

If you get import errors:
1. Ensure the test file is in the `tests/` directory
2. Check that `__init__.py` exists in the `tests/` directory
3. Verify the path to the addon directory in the test file

### Blender Crashes

If Blender crashes during tests:
1. Run tests one module at a time to isolate the issue
2. Check Blender's console output for error messages
3. Ensure tests properly clean up after themselves

## Contact

For questions or issues with the test suite, please open an issue on GitHub:
https://github.com/Clonephaze/nfc-keychain-generator-blender-addon/issues
