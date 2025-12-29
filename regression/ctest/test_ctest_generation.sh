#!/bin/bash
# Temporary CTest generation test script
# This validates that CTest generation works correctly
# TODO: Integrate into testing_tool.py with FILE: directive support

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ESBMC="${ESBMC:-../../build/src/esbmc/esbmc}"  # Default path, can override

if [ ! -f "$ESBMC" ]; then
    echo "Error: ESBMC not found at: $ESBMC"
    echo "Set ESBMC environment variable or build ESBMC first"
    exit 1
fi

TESTS_PASSED=0
TESTS_FAILED=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

run_test() {
    local test_name=$1
    local test_dir="$SCRIPT_DIR/$test_name"

    echo "Running test: $test_name"

    if [ ! -d "$test_dir" ]; then
        echo -e "${RED}✗${NC} Test directory not found: $test_dir"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    cd "$test_dir"

    # Clean up previous test outputs
    rm -f test_case.c test_case_*.c CMakeLists.txt 2>/dev/null

    # Read test.desc
    if [ ! -f "test.desc" ]; then
        echo -e "${RED}✗${NC} test.desc not found"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Parse test.desc (simple parsing, line by line)
    local mode=$(sed -n '1p' test.desc)
    local main_file=$(sed -n '2p' test.desc)
    local args=$(sed -n '3p' test.desc)

    # Run ESBMC
    if ! $ESBMC $main_file $args > output.log 2>&1; then
        # ESBMC might return non-zero on verification failure, but that's OK
        # We only care that it runs and generates files
        :
    fi

    # Verify files were generated
    local files_ok=true

    if [ ! -f "test_case.c" ] && [ ! -f "test_case_1.c" ]; then
        echo -e "${RED}✗${NC} No test case file generated (expected test_case.c or test_case_1.c)"
        files_ok=false
    fi

    if [ ! -f "CMakeLists.txt" ]; then
        echo -e "${RED}✗${NC} CMakeLists.txt not generated"
        files_ok=false
    fi

    if [ "$files_ok" = false ]; then
        echo "ESBMC output:"
        cat output.log
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Additional validation based on test name
    case "$test_name" in
        "bool-svcomp")
            if ! grep -q "_Bool __VERIFIER_nondet_bool" test_case.c; then
                echo -e "${RED}✗${NC} _Bool type not found in test_case.c (SV-COMP compliance)"
                TESTS_FAILED=$((TESTS_FAILED + 1))
                return 1
            fi
            if ! grep -q "static const _Bool v\[\]" test_case.c; then
                echo -e "${RED}✗${NC} _Bool array not found"
                TESTS_FAILED=$((TESTS_FAILED + 1))
                return 1
            fi
            ;;
        "simple-int")
            if ! grep -q "int __VERIFIER_nondet_int" test_case.c; then
                echo -e "${RED}✗${NC} int type not found in test_case.c"
                TESTS_FAILED=$((TESTS_FAILED + 1))
                return 1
            fi
            if ! grep -q "static const int v\[\]" test_case.c; then
                echo -e "${RED}✗${NC} int array not found"
                TESTS_FAILED=$((TESTS_FAILED + 1))
                return 1
            fi
            ;;
    esac

    # Verify CMakeLists.txt structure
    if ! grep -q "cmake_minimum_required" CMakeLists.txt; then
        echo -e "${RED}✗${NC} CMakeLists.txt missing cmake_minimum_required"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    if ! grep -q "add_executable" CMakeLists.txt; then
        echo -e "${RED}✗${NC} CMakeLists.txt missing add_executable"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    echo -e "${GREEN}✓${NC} $test_name passed"
    TESTS_PASSED=$((TESTS_PASSED + 1))

    # Clean up
    rm -f output.log

    cd "$SCRIPT_DIR"
}

# Main test execution
echo "========================================"
echo "CTest Generation Regression Tests"
echo "========================================"
echo "ESBMC: $ESBMC"
echo ""

# Run all tests
run_test "simple-int"
run_test "bool-svcomp"

# Summary
echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo "========================================"

if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
fi

exit 0
