# CTest调试指南 - 解决单值数组问题

## 问题现象

生成的test_case只包含单个值：
```c
int __VERIFIER_nondet_int(void) {
  static int i = 0;
  static const int v[] = { 1 };  // 只有1个值，应该是2个！
  return v[i++];
}
```

## 调试步骤

### 1. 编译最新代码

```bash
cd /home/user/esbmc

# 如果没有build目录，创建并配置
# mkdir build && cd build
# cmake .. -DCMAKE_BUILD_TYPE=Debug

# 如果已有build目录，直接编译
cd build
make -j4

# 验证编译成功
./esbmc --version
```

### 2. 创建测试文件

```bash
cd /home/user/esbmc

cat > debug_test.c << 'EOF'
#include <stdio.h>

extern int __VERIFIER_nondet_int(void);

int main(void) {
  int a = __VERIFIER_nondet_int();  // 第1次调用
  int b = __VERIFIER_nondet_int();  // 第2次调用

  printf("a=%d, b=%d\n", a, b);

  if (a > 0) {
    return 1;
  } else {
    return 0;
  }
}
EOF
```

### 3. 运行ESBMC（查看调试日志）

```bash
# 单个测试用例模式
./build/esbmc debug_test.c --generate-ctest-testcase

# 查看调试日志中的：
# [CTest DEBUG] Starting collect - SSA steps: X
# [CTest DEBUG] Nondet #1: type=int, value=...
# [CTest DEBUG] Nondet #2: type=int, value=...  (应该有这行！)
# [CTest DEBUG] Finished collect - total nondet values: 2

# 查看生成的文件
cat test_case.c
```

### 4. 分支覆盖模式

```bash
# 生成多个测试用例
./build/esbmc debug_test.c --branch-coverage --generate-ctest-testcase

# 查看每个测试用例
for f in test_case_*.c; do
  echo "=== $f ==="
  cat "$f"
  echo
done
```

## 期望的调试输出

### 正常情况（应该看到）：
```
[CTest DEBUG] Starting collect - SSA steps: 150
[CTest DEBUG] Nondet #1: type=int, value=1
[CTest DEBUG] Nondet #2: type=int, value=0
[CTest DEBUG] Finished collect - total nondet values: 2
Generated CTest test case(s) with CMakeLists.txt
```

### 异常情况（如果只收集到1个）：
```
[CTest DEBUG] Starting collect - SSA steps: 150
[CTest DEBUG] Nondet #1: type=int, value=1
[CTest DEBUG] Finished collect - total nondet values: 1  ← 问题！
```

## 可能的原因分析

### 原因1：ESBMC优化
ESBMC可能在某些情况下优化掉了第二次nondet调用。

**验证方法**：
```bash
# 使用更简单的代码
cat > simple_test.c << 'EOF'
extern int __VERIFIER_nondet_int(void);

int main(void) {
  int a = __VERIFIER_nondet_int();
  int b = __VERIFIER_nondet_int();
  return a + b;  // 强制使用两个值
}
EOF

./build/esbmc simple_test.c --generate-ctest-testcase
cat test_case.c
```

### 原因2：SSA表示问题
ESBMC的SSA中可能没有为每次调用创建独立的nondet赋值。

**验证方法**：
```bash
# 查看SSA步骤
./build/esbmc debug_test.c --show-goto-functions
```

### 原因3：分支覆盖路径
在`--branch-coverage`模式下，不同路径可能确实需要不同数量的nondet值。

**验证方法**：
查看每个test_case的数组大小：
```bash
grep -H "v\[\]" test_case_*.c
```

## 如果问题仍存在

请运行以上步骤并提供：

1. **ESBMC版本**：
   ```bash
   ./build/esbmc --version
   ```

2. **调试日志输出**：
   包含 `[CTest DEBUG]` 的所有行

3. **生成的test_case.c内容**

4. **您的测试代码**

这样我可以准确定位问题所在。

## 临时解决方案

如果确实只能收集到1个值，可以考虑：

### 方案A：手动修改生成的测试文件

```bash
# 自动生成后手动补充
cat test_case.c
# 手动将 { 1 } 改为 { 1, 0 }
```

### 方案B：修改源代码强制使用变量

```c
// 确保编译器不会优化掉
int main(void) {
  volatile int a = __VERIFIER_nondet_int();
  volatile int b = __VERIFIER_nondet_int();
  printf("%d %d\n", a, b);  // 强制输出
  return a + b;
}
```

## 下一步

请运行上述调试步骤并分享输出，我们可以根据实际情况进一步调整代码。
