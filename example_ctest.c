// 示例：数组边界检查
#include <assert.h>

extern int __VERIFIER_nondet_int();

#define ARRAY_SIZE 10

int safe_array_access(int index) {
    int array[ARRAY_SIZE] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

    // 检查数组边界
    assert(index >= 0 && index < ARRAY_SIZE);

    return array[index];
}

int main() {
    int idx = __VERIFIER_nondet_int();

    int value = safe_array_access(idx);

    return 0;
}
