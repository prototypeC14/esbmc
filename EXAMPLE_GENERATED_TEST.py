"""
This is an EXAMPLE of what ESBMC will AUTO-GENERATE.

To actually generate this file, you would run:
  esbmc example_div_bug.py --generate-testcase

Then ESBMC will create: test_counterexample.py (like this file)

This file shows the expected output format.
"""
import pytest
from example_div_bug import div1


def test_div1_counterexample():
    """
    Test case generated from ESBMC counterexample.

    This test should trigger the bug found by ESBMC.
    Run with: pytest EXAMPLE_GENERATED_TEST.py
    """
    # Input values from counterexample
    cond = 0
    x = 0

    # This call should reproduce the bug
    with pytest.raises(ZeroDivisionError):
        result = div1(cond, x)


def test_div1_manual():
    """
    Manual test - customize this to verify the fix.
    """
    # TODO: Add test cases for correct behavior after fixing the bug
    # Example:
    # assert div1(1, 5) == 0  # 5 // 10 = 0
    # assert div1(0, 10) == 4  # 42 // 10 = 4
    pass


# To verify this works without running ESBMC:
if __name__ == "__main__":
    print("Testing the example...")
    try:
        test_div1_counterexample()
        print("✗ Test should have raised ZeroDivisionError!")
    except AssertionError:
        print("✓ Test correctly detected ZeroDivisionError")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
