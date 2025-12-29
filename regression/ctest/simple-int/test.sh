#!/bin/bash
# Test script for simple-int CTest generation test
# This script runs ESBMC and validates generated file contents

set -e

# Clean up any previous test outputs
rm -f test_case.c test_case_*.c CMakeLists.txt

# Run ESBMC to generate CTest test case
${ESBMC:-esbmc} main.c --generate-ctest-testcase

# Validate test_case.c exists and contains expected content
if [ ! -f "test_case.c" ]; then
    echo "ERROR: test_case.c not generated"
    exit 1
fi

if ! grep -q "int __VERIFIER_nondet_int(void)" test_case.c; then
    echo "ERROR: Missing __VERIFIER_nondet_int function"
    exit 1
fi

if ! grep -q "static const int v\[\]" test_case.c; then
    echo "ERROR: Missing static const int array"
    exit 1
fi

if ! grep -q "return v\[i++\]" test_case.c; then
    echo "ERROR: Missing return statement"
    exit 1
fi

# Validate CMakeLists.txt exists and contains expected content
if [ ! -f "CMakeLists.txt" ]; then
    echo "ERROR: CMakeLists.txt not generated"
    exit 1
fi

if ! grep -q "cmake_minimum_required" CMakeLists.txt; then
    echo "ERROR: Missing cmake_minimum_required"
    exit 1
fi

if ! grep -q "add_executable" CMakeLists.txt; then
    echo "ERROR: Missing add_executable"
    exit 1
fi

# All validations passed
echo "VERIFICATION SUCCESSFUL"
exit 0
