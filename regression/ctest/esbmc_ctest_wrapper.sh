#!/bin/bash
# Wrapper script for ESBMC CTest generation testing
# This script acts as a "tool" wrapper that runs ESBMC and then outputs
# generated file contents to stdout so testing_tool.py can validate them
#
# Usage: This script is called by testing_tool.py via --tool parameter
#        It expects the real ESBMC binary path in ESBMC_BIN environment variable

# Find real ESBMC binary
if [ -z "$ESBMC_BIN" ]; then
    # Fallback: try to find esbmc in PATH or common locations
    if command -v esbmc >/dev/null 2>&1; then
        ESBMC="esbmc"
    elif [ -f "../../build/src/esbmc/esbmc" ]; then
        ESBMC="../../build/src/esbmc/esbmc"
    else
        echo "Error: ESBMC_BIN not set and cannot find esbmc binary" >&2
        exit 1
    fi
else
    ESBMC="$ESBMC_BIN"
fi

# Run ESBMC with all provided arguments
"$ESBMC" "$@"
ESBMC_EXIT_CODE=$?

# Output marker for test validation
echo "=== ESBMC CTest Generation Output ==="

# Check and output generated files (in the test directory)
if [ -f "test_case.c" ]; then
    echo "=== BEGIN test_case.c ==="
    cat test_case.c
    echo "=== END test_case.c ==="
elif [ -f "test_case_1.c" ]; then
    # Multiple test cases (coverage mode)
    for file in test_case_*.c; do
        if [ -f "$file" ]; then
            echo "=== BEGIN $file ==="
            cat "$file"
            echo "=== END $file ==="
        fi
    done
fi

if [ -f "CMakeLists.txt" ]; then
    echo "=== BEGIN CMakeLists.txt ==="
    cat CMakeLists.txt
    echo "=== END CMakeLists.txt ==="
fi

# Return ESBMC's original exit code
exit $ESBMC_EXIT_CODE
