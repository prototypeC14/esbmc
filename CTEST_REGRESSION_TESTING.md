# CTest Generator Regression Testing Strategy

## Problem

ESBMC's regression test system is designed for testing stdout/stderr output using regex matching. However, CTest generator produces **file outputs** (test_case.c, CMakeLists.txt), which requires a different testing approach.

## Current Regression Test Format

Standard ESBMC tests use `test.desc`:
```
CORE                          # Line 1: Test mode
main.c                        # Line 2: Test file
--branch-coverage             # Line 3: ESBMC arguments
^Generated 4 test cases$      # Line 4+: Expected output regex
```

## Proposed Solutions for CTest

### Option 1: File Existence + Content Regex (Recommended)

**Approach**: Extend test.desc to support file content checking.

**New format**:
```
CORE
main.c
--branch-coverage --generate-ctest-testcase
^Generated.*test cases$
FILE:test_case_1.c:__VERIFIER_nondet_int.*static const int v\[\]
FILE:test_case_1.c:return v\[i\+\+\]
FILE:CMakeLists.txt:cmake_minimum_required
FILE:CMakeLists.txt:add_executable\(test_case_1
```

**Syntax**: `FILE:<filename>:<regex>`

**Advantages**:
- ✅ Minimal changes to testing_tool.py
- ✅ Flexible - can check key patterns without exact matching
- ✅ Doesn't break on minor formatting changes
- ✅ Can verify multiple files

**Implementation**:
```python
# In testing_tool.py
def check_file_output(test_dir, file_checks):
    for check in file_checks:
        filename, pattern = check.split(':', 1)
        filepath = os.path.join(test_dir, filename)
        if not os.path.exists(filepath):
            return False, f"File {filename} not found"
        with open(filepath) as f:
            content = f.read()
            if not re.search(pattern, content):
                return False, f"Pattern not found in {filename}: {pattern}"
    return True, "OK"
```

### Option 2: Golden File Comparison

**Approach**: Store expected output files and do exact comparison.

**Structure**:
```
regression/ctest/simple-int/
├── test.desc
├── main.c
└── expected/
    ├── test_case.c
    └── CMakeLists.txt
```

**test.desc**:
```
CORE
main.c
--generate-ctest-testcase
COMPARE_FILE:test_case.c:expected/test_case.c
COMPARE_FILE:CMakeLists.txt:expected/CMakeLists.txt
```

**Advantages**:
- ✅ Exact verification
- ✅ Easy to understand what's expected

**Disadvantages**:
- ❌ Brittle - breaks on version number changes, comment changes
- ❌ Requires maintaining golden files
- ❌ Hard to update when format changes

### Option 3: Compile and Run Test

**Approach**: Actually compile and run the generated test.

**test.desc**:
```
CORE
main.c
--generate-ctest-testcase
^Generated.*test cases$
BUILD_AND_RUN:gcc main.c test_case.c -o test && ./test
^.*$  # Expected exit code 0
```

**Advantages**:
- ✅ Strongest validation - tests actually work
- ✅ Catches compilation errors
- ✅ Platform-agnostic

**Disadvantages**:
- ❌ Requires build tools in CI
- ❌ Slower tests
- ❌ Complex test infrastructure

### Option 4: Hybrid Approach (Best)

Combine Options 1 and 3:

**Fast Smoke Test** (Option 1):
- Check file existence
- Verify key patterns exist
- Run on every commit

**Thorough Validation** (Option 3):
- Compile and run generated tests
- Run periodically or on release branches
- Use THOROUGH test mode

## Recommended Implementation

### Step 1: Extend testing_tool.py

Add support for `FILE:` directive in test.desc:

```python
class TestCase:
    def _initialize_test_case(self):
        # ... existing code ...
        self.file_checks = []  # New field

        for line in fp:
            line = line.strip()
            if line.startswith("FILE:"):
                # Parse: FILE:filename:regex
                parts = line[5:].split(':', 1)
                self.file_checks.append((parts[0], parts[1]))
            else:
                self.test_regex.append(line)

    def verify_file_outputs(self):
        """Verify generated file contents"""
        for filename, pattern in self.file_checks:
            filepath = os.path.join(self.test_dir, filename)
            if not os.path.exists(filepath):
                raise AssertionError(f"Expected file not generated: {filename}")

            with open(filepath) as f:
                content = f.read()
                if not re.search(pattern, content, re.MULTILINE):
                    raise AssertionError(
                        f"Pattern not found in {filename}:\n"
                        f"  Expected: {pattern}\n"
                        f"  File content preview:\n{content[:200]}..."
                    )
```

### Step 2: Create Test Cases

**Example: Simple Integer Test**

`regression/ctest/simple-int/main.c`:
```c
extern int __VERIFIER_nondet_int(void);

int main(void) {
    int x = __VERIFIER_nondet_int();
    if (x > 0) return 1;
    return 0;
}
```

`regression/ctest/simple-int/test.desc`:
```
CORE
main.c
--generate-ctest-testcase
^CTest DEBUG.*Collected \d+ nondet values$
FILE:test_case.c:int __VERIFIER_nondet_int\(void\)
FILE:test_case.c:static const int v\[\]
FILE:test_case.c:return v\[i\+\+\]
FILE:CMakeLists.txt:cmake_minimum_required\(VERSION 3\.10\)
FILE:CMakeLists.txt:add_executable\(test_case
```

**Example: Multiple Types Test**

`regression/ctest/mixed-types/test.desc`:
```
CORE
main.c
--branch-coverage --generate-ctest-testcase
FILE:test_case_1.c:int __VERIFIER_nondet_int
FILE:test_case_1.c:float __VERIFIER_nondet_float
FILE:test_case_1.c:_Bool __VERIFIER_nondet_bool
FILE:CMakeLists.txt:enable_testing
```

**Example: Bool Type (SV-COMP Compliance)**

`regression/ctest/bool-svcomp/test.desc`:
```
CORE
main.c
--generate-ctest-testcase
FILE:test_case.c:_Bool __VERIFIER_nondet_bool\(void\)
FILE:test_case.c:static const _Bool v\[\]
```

### Step 3: Add Compilation Tests (THOROUGH mode)

`regression/ctest/compile-test/test.desc`:
```
THOROUGH
main.c
--generate-ctest-testcase
COMPILE:gcc -std=c99 main.c test_case.c -o test
EXPECT_EXIT:0
```

## Test Organization

```
regression/ctest/
├── simple-int/          # Basic int test
├── simple-float/        # Float test
├── simple-bool/         # _Bool (SV-COMP compliance)
├── mixed-types/         # Multiple types in one program
├── multiple-calls/      # Same type called multiple times
├── branch-coverage/     # Multiple test cases
├── all-types/           # All 12 supported types
└── compile-test/        # Actually compile and run (THOROUGH)
```

## Implementation Checklist

- [ ] Extend testing_tool.py to support FILE: directive
- [ ] Add basic CTest regression tests (CORE mode)
- [ ] Add compilation tests (THOROUGH mode)
- [ ] Update CI to run ctest regression tests
- [ ] Document testing approach in CONTRIBUTIONS.md

## Alternative: Shell Script Tests

If modifying testing_tool.py is too complex, create standalone shell tests:

`regression/ctest/run_tests.sh`:
```bash
#!/bin/bash
set -e

ESBMC=../../esbmc

# Test 1: Simple int
cd simple-int
$ESBMC main.c --generate-ctest-testcase > /dev/null
grep -q "__VERIFIER_nondet_int" test_case.c || exit 1
grep -q "static const int v\[\]" test_case.c || exit 1
echo "✓ simple-int"
cd ..

# Test 2: Bool type
cd bool-svcomp
$ESBMC main.c --generate-ctest-testcase > /dev/null
grep -q "_Bool __VERIFIER_nondet_bool" test_case.c || exit 1
echo "✓ bool-svcomp"
cd ..

echo "All CTest tests passed!"
```

## Conclusion

**Recommendation**: Use **Hybrid Approach (Option 4)**
- Implement FILE: directive in testing_tool.py for fast smoke tests
- Add a few THOROUGH mode tests that compile and run
- Start with 5-10 basic tests covering key functionality
- Expand coverage over time

This provides good coverage without excessive maintenance burden.
