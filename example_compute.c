#include <stdio.h>

extern int __VERIFIER_nondet_int(void);

static int compute(int a, int b) {
  if (a > 0) {          // 分支 A
    if (b == 0) {       // 分支 B（只在 a>0 时进入）
      return 10;
    } else {
      return 11;
    }
  } else {
    if (b < 0) {        // 分支 C（只在 a<=0 时进入）
      return 20;
    } else {
      return 21;
    }
  }
}

int main(void) {
  int a = __VERIFIER_nondet_int();  // nondet 第 1 次
  int b = __VERIFIER_nondet_int();  // nondet 第 2 次
  int r = compute(a, b);
  printf("%d\n", r);
  return 0;
}
