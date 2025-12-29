#!/bin/bash
# Test script for simple-int CTest generation test
# This script runs ESBMC and validates generated file contents by comparing with expected files

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Clean up any previous test outputs
rm -f test_case.c test_case_*.c CMakeLists.txt

# Run ESBMC to generate CTest test case
${ESBMC:-esbmc} main.c --generate-ctest-testcase

# Check that expected files were generated
if [ ! -f "test_case.c" ]; then
    echo "ERROR: test_case.c not generated"
    exit 1
fi

if [ ! -f "CMakeLists.txt" ]; then
    echo "ERROR: CMakeLists.txt not generated"
    exit 1
fi

# Check that no unexpected files were generated (test_case_*.c should not exist)
if ls test_case_*.c 2>/dev/null | grep -q .; then
    echo "ERROR: Unexpected test_case_*.c files generated"
    ls test_case_*.c
    exit 1
fi

# Helper function to strip comments and empty lines
strip_comments() {
    grep -v "^[[:space:]]*\/\/" "$1" | grep -v "^[[:space:]]*#" | grep -v "^[[:space:]]*$"
}

# Compare test_case.c (without comments)
strip_comments test_case.c > test_case_stripped.c
strip_comments "$SCRIPT_DIR/expected_test_case.c" > expected_test_case_stripped.c

if ! diff -u expected_test_case_stripped.c test_case_stripped.c; then
    echo "ERROR: test_case.c differs from expected"
    exit 1
fi

# Compare CMakeLists.txt (without comments)
strip_comments CMakeLists.txt > CMakeLists_stripped.txt
strip_comments "$SCRIPT_DIR/expected_CMakeLists.txt" > expected_CMakeLists_stripped.txt

if ! diff -u expected_CMakeLists_stripped.txt CMakeLists_stripped.txt; then
    echo "ERROR: CMakeLists.txt differs from expected"
    exit 1
fi

# Clean up temporary files
rm -f test_case_stripped.c expected_test_case_stripped.c
rm -f CMakeLists_stripped.txt expected_CMakeLists_stripped.txt

# All validations passed
echo "VERIFICATION SUCCESSFUL"
exit 0
