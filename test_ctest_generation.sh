#!/bin/bash
# Test script to verify CTest generation with multiple nondet calls

set -e

echo "=== CTest Multiple Nondet Test ==="
echo

# Create test program
cat > test_multiple_nondet.c << 'EOF'
#include <stdio.h>

extern int __VERIFIER_nondet_int(void);

static int compute(int a, int b) {
  if (a > 0) {
    if (b == 0) {
      return 10;
    } else {
      return 11;
    }
  } else {
    if (b < 0) {
      return 20;
    } else {
      return 21;
    }
  }
}

int main(void) {
  int a = __VERIFIER_nondet_int();  // nondet call #1
  int b = __VERIFIER_nondet_int();  // nondet call #2
  int r = compute(a, b);
  printf("%d\n", r);
  return 0;
}
EOF

echo "Created test_multiple_nondet.c"
echo

# Run ESBMC to generate test cases
echo "Running ESBMC with --branch-coverage..."
./esbmc test_multiple_nondet.c --branch-coverage --generate-ctest-testcase

echo
echo "=== Generated Test Cases ==="
echo

# Check generated files
for file in test_case_*.c; do
  if [ -f "$file" ]; then
    echo "--- $file ---"
    cat "$file"
    echo

    # Count values in array
    value_count=$(grep -oP 'v\[\] = \{ \K[^}]+' "$file" | tr ',' '\n' | wc -l)
    echo "Number of values in array: $value_count"
    echo

    if [ "$value_count" -lt 2 ]; then
      echo "⚠️  WARNING: Expected at least 2 values, but found $value_count"
      echo "   This may indicate the deduplication issue is still present."
    else
      echo "✓ OK: Found $value_count values as expected"
    fi
    echo "========================================"
    echo
  fi
done

# Check CMakeLists.txt
if [ -f CMakeLists.txt ]; then
  echo "--- CMakeLists.txt ---"
  cat CMakeLists.txt
  echo
fi

echo "Test complete!"
