// 测试 _Bool 类型 (SV-COMP 标准)
#include <stdio.h>

// 按照 SV-COMP 标准声明
extern _Bool __VERIFIER_nondet_bool(void);

int main(void) {
  _Bool flag1 = __VERIFIER_nondet_bool();
  _Bool flag2 = __VERIFIER_nondet_bool();

  printf("Boolean test:\n");
  printf("  flag1: %d\n", flag1);
  printf("  flag2: %d\n", flag2);

  // 测试不同分支
  if (flag1) {
    if (flag2) {
      printf("Both true\n");
      return 1;
    } else {
      printf("Only flag1 true\n");
      return 2;
    }
  } else {
    if (flag2) {
      printf("Only flag2 true\n");
      return 3;
    } else {
      printf("Both false\n");
      return 0;
    }
  }
}
