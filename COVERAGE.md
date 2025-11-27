# Coverage Analysis

ESBMC supports automated test case generation and coverage analysis for branch, decision, and assertion coverage. This helps identify untested code paths and generate counterexamples showing what inputs are needed to achieve full coverage.

## Usage

ESBMC provides three coverage analysis modes:

```bash
# Branch coverage
esbmc example.c --branch-coverage

# Decision coverage
esbmc example.c --decision-coverage

# Assertion coverage
esbmc example.c --assertion-coverage
```

## Coverage Modes

### Branch Coverage

Branch coverage verifies that all branches of conditional statements are executed. For each `if`, `else`, `while`, or `for` statement, both the true and false branches must be covered.

**Example:**

```c
int check_sign(int n) {
    if (n > 0)
        return 1;
    else
        return -1;
}

int main() {
    check_sign(5);   // Only covers true branch
    return 0;
}
```

```bash
$ esbmc example.c --branch-coverage
...
✗ FAILED: '!(n > 0) at file example.c line 2'

[Coverage]
Branches : 2
Reached : 1
Branch Coverage: 50%

VERIFICATION FAILED
```

The counterexample shows that `n <= 0` is needed to cover the else branch.

**Full coverage example:**

```c
int main() {
    check_sign(5);    // Covers true branch
    check_sign(-3);   // Covers false branch
    return 0;
}
```

```bash
$ esbmc example.c --branch-coverage
...
[Coverage]
Branches : 2
Reached : 2
Branch Coverage: 100%

VERIFICATION SUCCESSFUL
```

### Decision Coverage

Decision coverage verifies that all boolean sub-expressions in conditional statements evaluate to both true and false. This is stronger than branch coverage for complex conditions.

**Example:**

```c
int validate(int x, int y) {
    if (x > 0 && y > 0)  // Complex decision
        return 1;
    else
        return 0;
}

int main() {
    validate(5, 3);   // Only covers: (T && T) = T
    return 0;
}
```

```bash
$ esbmc example.c --decision-coverage
...
VERIFICATION FAILED
```

For full decision coverage, you need to test:
- `(true && true)` → true
- `(true && false)` → false
- `(false && true)` → false
- `(false && false)` → false

**Full coverage example:**

```c
int main() {
    validate(5, 3);    // T && T
    validate(5, -1);   // T && F
    validate(-1, 3);   // F && T
    validate(-1, -1);  // F && F
    return 0;
}
```

### Assertion Coverage

Assertion coverage verifies that all assertions in the code are reached and tested. This ensures that all validation checks are exercised.

**Example:**

```c
int process(int n) {
    assert(n >= 0);
    if (n > 10) {
        assert(n < 100);  // Conditional assertion
        return n * 2;
    }
    return n;
}

int main() {
    process(5);   // Only covers first assertion
    return 0;
}
```

```bash
$ esbmc example.c --assertion-coverage
...
VERIFICATION FAILED
```

**Full coverage example:**

```c
int main() {
    process(5);    // Covers first assertion
    process(50);   // Covers both assertions
    return 0;
}
```

```bash
$ esbmc example.c --assertion-coverage
...
VERIFICATION SUCCESSFUL
```

## Supported Languages

Coverage analysis is supported for:

- **C** - All C89, C99, C11 features
- **C++** - All C++ features supported by ESBMC
- **Python** - Full Python frontend support

## Interpreting Results

### Verification Successful

When `VERIFICATION SUCCESSFUL` is reported with 100% coverage, all code paths have been tested with the provided inputs.

### Verification Failed

When `VERIFICATION FAILED` is reported, ESBMC provides:
1. **Counterexample**: Shows what input values would cover the missing path
2. **Coverage statistics**: Displays how many branches/decisions/assertions were covered
3. **Location**: Points to the exact line and condition that needs additional testing

## Python Examples

### Branch Coverage

```python
def is_positive(n: int) -> int:
    if n > 0:
        return 1
    else:
        return 0

# Only covers positive branch
is_positive(10)
```

```bash
$ esbmc example.py --branch-coverage
...
✗ FAILED: '!(n > 0) at file example.py line 2'

[Coverage]
Branches : 2
Reached : 1
Branch Coverage: 50%

VERIFICATION FAILED
```

### Decision Coverage

```python
def check_range(x: int, y: int) -> int:
    if x > 0 and y > 0:
        return 1
    else:
        return 0

# Full coverage
check_range(5, 3)    # T and T
check_range(5, -1)   # T and F
check_range(-1, 3)   # F and T
check_range(-1, -1)  # F and F
```

```bash
$ esbmc example.py --decision-coverage
...
[Coverage]
Branch Coverage: 100%

VERIFICATION SUCCESSFUL
```

### Assertion Coverage

```python
def validate_positive(n: int) -> int:
    assert n > 0, "n must be positive"
    return n * 2

validate_positive(5)
```

```bash
$ esbmc example.py --assertion-coverage
...
VERIFICATION SUCCESSFUL
```

## Technical Notes

### Coverage vs Testing

- Coverage analysis in ESBMC uses **symbolic execution** and **SMT solving**
- Unlike traditional testing tools, ESBMC **proves** which paths are reachable
- Counterexamples provide **concrete values** to achieve missing coverage
- All paths are explored **automatically** without manual test case writing

### Performance

- Coverage analysis adds false assertions to test each branch/decision
- Verification time increases with code complexity
- Use `THOROUGH` test mode for comprehensive analysis
- For large programs, consider using `--function` to analyze specific functions

### Combining with Other Flags

Coverage analysis can be combined with other ESBMC options:

```bash
# With specific function
esbmc example.c --branch-coverage --function foo

# With bounded model checking
esbmc example.c --branch-coverage --unwind 10

# With memory safety checks
esbmc example.c --branch-coverage --memory-leak-check
```

## Architecture

The Python frontend uses a three-function architecture to ensure accurate coverage:

1. **python_init** - Initialization code (models, intrinsics, imports) marked with `__ESBMC_HIDE`
2. **python_user_main** - User code analyzed for coverage
3. **__ESBMC_main** - Entry point that calls initialization then user code

This ensures that only user code is counted in coverage statistics, not library or initialization code.

## References

- GitHub Issue: [#3132](https://github.com/esbmc/esbmc/issues/3132) - Python coverage support
- Test cases: `regression/python-coverage/` directory
- Implementation: `src/goto-programs/goto_coverage.cpp`
