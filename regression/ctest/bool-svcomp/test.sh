#!/bin/bash
# Test script for bool-svcomp CTest generation test
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

if ! grep -q "_Bool __VERIFIER_nondet_bool(void)" test_case.c; then
    echo "ERROR: Missing _Bool __VERIFIER_nondet_bool function"
    exit 1
fi

if ! grep -q "static const _Bool v\[\]" test_case.c; then
    echo "ERROR: Missing static const _Bool array"
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

# All validations passed
echo "VERIFICATION SUCCESSFUL"
exit 0
