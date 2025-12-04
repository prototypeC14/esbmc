"""
Manual verification of pytest generation logic.
This demonstrates what the generated test will do.
"""
from test_div_example import div1


def test_div1_counterexample_manual():
    """
    This simulates what the ESBMC-generated pytest test will do.
    """
    print("Testing counterexample: cond=0, x=0")

    # Input values from counterexample
    cond = 0
    x = 0

    # This call should trigger ZeroDivisionError
    try:
        result = div1(cond, x)
        print("✗ FAIL: Expected ZeroDivisionError but got result:", result)
        return False
    except ZeroDivisionError:
        print("✓ PASS: ZeroDivisionError raised as expected")
        return True
    except Exception as e:
        print(f"✗ FAIL: Unexpected exception: {type(e).__name__}: {e}")
        return False


def test_div1_correct_behavior():
    """
    Test cases that should work correctly.
    """
    print("\nTesting correct behavior:")

    test_cases = [
        (1, 50, 5),    # cond=1, x=50 -> 50 // 10 = 5
        (1, 100, 10),  # cond=1, x=100 -> 100 // 10 = 10
        (0, 10, 4),    # cond=0, x=10 -> 42 // 10 = 4
        (0, 2, 21),    # cond=0, x=2 -> 42 // 2 = 21
    ]

    all_passed = True
    for cond, x, expected in test_cases:
        try:
            result = div1(cond, x)
            if result == expected:
                print(f"  ✓ div1({cond}, {x}) = {result} (expected {expected})")
            else:
                print(f"  ✗ div1({cond}, {x}) = {result} (expected {expected})")
                all_passed = False
        except Exception as e:
            print(f"  ✗ div1({cond}, {x}) raised {type(e).__name__}: {e}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("=" * 60)
    print("Manual Verification of ESBMC Pytest Generation")
    print("=" * 60)

    # Test the counterexample
    bug_test_passed = test_div1_counterexample_manual()

    # Test correct behavior
    correct_test_passed = test_div1_correct_behavior()

    print("\n" + "=" * 60)
    if bug_test_passed and correct_test_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60)
