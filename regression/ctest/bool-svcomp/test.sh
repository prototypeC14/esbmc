#!/bin/bash
# Test script for bool-svcomp CTest generation test
# This script runs ESBMC and outputs generated file contents for validation

set -e

# Clean up any previous test outputs
rm -f test_case.c test_case_*.c CMakeLists.txt

# Run ESBMC to generate CTest test case
${ESBMC:-esbmc} main.c --generate-ctest-testcase

# Output generated files to stdout for test.desc validation
if [ -f "test_case.c" ]; then
    echo "=== BEGIN test_case.c ==="
    cat test_case.c
    echo "=== END test_case.c ==="
fi

if [ -f "CMakeLists.txt" ]; then
    echo "=== BEGIN CMakeLists.txt ==="
    cat CMakeLists.txt
    echo "=== END CMakeLists.txt ==="
fi

exit 0
