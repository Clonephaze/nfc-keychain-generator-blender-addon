#!/bin/bash
# Shell script to run tests for NFC Card & Keychain Generator addon
# This script will attempt to find Blender and run the test suite

# Common Blender installation paths
BLENDER_PATHS=(
    "/usr/bin/blender"
    "/usr/local/bin/blender"
    "/snap/bin/blender"
    "/Applications/Blender.app/Contents/MacOS/Blender"
    "$HOME/Applications/Blender.app/Contents/MacOS/Blender"
)

BLENDER_EXE=""

# Try to find Blender
for path in "${BLENDER_PATHS[@]}"; do
    if [ -f "$path" ]; then
        BLENDER_EXE="$path"
        break
    fi
done

# If not found, check if blender is in PATH
if [ -z "$BLENDER_EXE" ]; then
    if command -v blender &> /dev/null; then
        BLENDER_EXE="blender"
    fi
fi

# If still not found, error out
if [ -z "$BLENDER_EXE" ]; then
    echo "ERROR: Could not find Blender installation."
    echo "Please install Blender 4.2 or higher, or specify the path manually."
    echo ""
    echo "Usage: ./run_tests.sh [/path/to/blender]"
    echo ""
    exit 1
fi

echo "Found Blender at: $BLENDER_EXE"
echo ""

# If user provided custom path, use it
if [ ! -z "$1" ]; then
    BLENDER_EXE="$1"
    echo "Using custom Blender path: $BLENDER_EXE"
    echo ""
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run tests
echo "Running tests..."
echo "================================================================================"
"$BLENDER_EXE" --background --python "$SCRIPT_DIR/tests/run_tests.py" -- "$@"

# Capture exit code
TEST_RESULT=$?

echo "================================================================================"
echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo "Tests completed successfully!"
    echo "Exit code: $TEST_RESULT"
else
    echo "Tests failed!"
    echo "Exit code: $TEST_RESULT"
fi
echo ""

exit $TEST_RESULT
