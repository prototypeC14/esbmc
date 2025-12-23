// Test program for CTest generation
#include <assert.h>

extern int __VERIFIER_nondet_int();

int divide(int a, int b) {
    assert(b != 0);  // This will fail when b=0
    return a / b;
}

int main() {
    int x = __VERIFIER_nondet_int();
    int y = __VERIFIER_nondet_int();

    int result = divide(x, y);

    return 0;
}
