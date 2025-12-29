# CTest Generation Regression Tests

This directory contains regression tests for the CTest test case generator (`--generate-ctest-testcase`).

## Test Structure

Each test directory contains:
- `main.c` - Source code to test
- `test.desc` - Test descriptor (format compatible with ESBMC regression system)

## Running Tests

### Quick Test (Shell Script)

```bash
# From this directory
./test_ctest_generation.sh

# Or specify ESBMC path
ESBMC=/path/to/esbmc ./test_ctest_generation.sh
```

### Integration with ESBMC Testing Framework

**Note**: Full integration requires extending `testing_tool.py` to support file content verification.

See `CTEST_REGRESSION_TESTING.md` in repository root for implementation plan.

## Current Tests

### simple-int
Tests basic integer nondet generation.

**Verifies**:
- `test_case.c` is generated
- Contains `int __VERIFIER_nondet_int(void)`
- Contains `static const int v[]`
- `CMakeLists.txt` is generated with proper structure

### bool-svcomp
Tests `_Bool` type generation per SV-COMP standard.

**Verifies**:
- Generates `_Bool` (not `int`) for `__VERIFIER_nondet_bool()`
- Uses `static const _Bool v[]`
- Complies with C99/SV-COMP standard

## Adding New Tests

1. Create directory: `regression/ctest/my-test/`
2. Add `main.c` with test code
3. Add `test.desc`:
   ```
   CORE
   main.c
   --generate-ctest-testcase
   ^.*Generated.*$
   ```
4. Add test case to `test_ctest_generation.sh`
5. Run tests to verify

## Test Coverage Goals

- [x] Basic integer type
- [x] _Bool type (SV-COMP compliance)
- [ ] Float/double types
- [ ] Multiple types in one file
- [ ] Multiple nondet calls of same type
- [ ] Branch coverage mode (multiple test cases)
- [ ] All 12 supported types

## Future Work

Extend `testing_tool.py` to support:
```
FILE:test_case.c:__VERIFIER_nondet_int
FILE:test_case.c:static const int v\[\]
FILE:CMakeLists.txt:cmake_minimum_required
```

This will integrate CTest tests into the main regression suite.

## Manual Verification

To manually verify a test:

```bash
cd simple-int

# Generate test
/path/to/esbmc main.c --generate-ctest-testcase

# Inspect generated files
cat test_case.c
cat CMakeLists.txt

# Compile and run (optional)
mkdir build && cd build
cmake ..
make
./test_case
echo $?  # Should be 0 or 1 (test exit code)
```

## CI Integration

Add to `.github/workflows/`:

```yaml
- name: Run CTest generation tests
  run: |
    cd regression/ctest
    ./test_ctest_generation.sh
```
