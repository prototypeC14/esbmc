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

# Validate complete function structure using grep -Pzo (Perl regex, multiline)
if ! grep -Pzo 'int __VERIFIER_nondet_int\(void\) \{[^}]*static int i = 0;[^}]*static const int v\[\][^}]*return v\[i\+\+\];[^}]*\}' test_case.c > /dev/null; then
    echo "ERROR: __VERIFIER_nondet_int function structure incorrect"
    exit 1
fi

# Validate CMakeLists.txt exists and contains expected content
if [ ! -f "CMakeLists.txt" ]; then
    echo "ERROR: CMakeLists.txt not generated"
    exit 1
fi

# Validate complete CMakeLists.txt structure
read -r -d '' cmake_expected << 'EOF' || true
cmake_minimum_required(VERSION 3.10)
project(ESBMCGeneratedTest C)

add_executable(test_case test_case.c)
EOF

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
