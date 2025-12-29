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

# Validate complete function structure using grep -Pzo (Perl regex, multiline)
# This checks for the complete _Bool function with proper SV-COMP compliant type
if ! grep -Pzo '_Bool __VERIFIER_nondet_bool\(void\) \{[^}]*static int i = 0;[^}]*static const _Bool v\[\][^}]*return v\[i\+\+\];[^}]*\}' test_case.c > /dev/null; then
    echo "ERROR: __VERIFIER_nondet_bool function structure incorrect or not using _Bool type"
    exit 1
fi

# Validate CMakeLists.txt exists and contains expected content
if [ ! -f "CMakeLists.txt" ]; then
    echo "ERROR: CMakeLists.txt not generated"
    exit 1
fi

# Validate complete CMakeLists.txt structure
if ! grep -q "cmake_minimum_required(VERSION 3.10)" CMakeLists.txt; then
    echo "ERROR: Missing or incorrect cmake_minimum_required"
    exit 1
fi

if ! grep -q "add_executable(test_case test_case.c)" CMakeLists.txt; then
    echo "ERROR: Missing or incorrect add_executable"
    exit 1
fi

# All validations passed
echo "VERIFICATION SUCCESSFUL"
exit 0
