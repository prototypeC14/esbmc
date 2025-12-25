# CTest 支持的 VERIFIER 类型

## 完整类型支持列表

CTest生成器完全支持以下 `__VERIFIER_nondet_*` 函数类型：

### 整数类型

| VERIFIER函数 | C类型 | 位宽 | 值范围 | 示例值 |
|------------|------|-----|--------|-------|
| `__VERIFIER_nondet_int()` | `int` | 32位 | -2147483648 ~ 2147483647 | `-10, 0, 127` |
| `__VERIFIER_nondet_uint()` | `unsigned int` | 32位 | 0 ~ 4294967295 | `0, 255, 1000` |
| `__VERIFIER_nondet_char()` | `char` | 8位 | -128 ~ 127 | `-10, 0, 'A'` |
| `__VERIFIER_nondet_uchar()` | `unsigned char` | 8位 | 0 ~ 255 | `0, 65, 255` |
| `__VERIFIER_nondet_short()` | `short` | 16位 | -32768 ~ 32767 | `-100, 0, 1000` |
| `__VERIFIER_nondet_ushort()` | `unsigned short` | 16位 | 0 ~ 65535 | `0, 1000, 30000` |
| `__VERIFIER_nondet_long()` | `long long` | 64位 | -2^63 ~ 2^63-1 | `-1000000, 0, 1000000` |
| `__VERIFIER_nondet_ulong()` | `unsigned long long` | 64位 | 0 ~ 2^64-1 | `0, 1000000, 1000000000` |

### 浮点类型

| VERIFIER函数 | C类型 | 精度 | 示例值 |
|------------|------|------|-------|
| `__VERIFIER_nondet_float()` | `float` | 单精度 | `0.0, 3.14, -1.5` |
| `__VERIFIER_nondet_double()` | `double` | 双精度 | `0.0, 2.718281828, -9.81` |

### 其他类型

| VERIFIER函数 | C类型 | 说明 | 示例值 |
|------------|------|------|-------|
| `__VERIFIER_nondet_bool()` | `int` | 布尔值 | `0, 1` |
| `__VERIFIER_nondet_pointer()` | `void*` | 指针类型 | `NULL, 0xABCD` |

## 使用示例

### 1. 单一类型多次调用

```c
#include <stdio.h>

extern int __VERIFIER_nondet_int(void);

int main(void) {
  int a = __VERIFIER_nondet_int();  // 第1次调用
  int b = __VERIFIER_nondet_int();  // 第2次调用
  int c = __VERIFIER_nondet_int();  // 第3次调用

  printf("%d %d %d\n", a, b, c);
  return 0;
}
```

**生成的 test_case_1.c**：
```c
int __VERIFIER_nondet_int(void) {
  static int i = 0;
  static const int v[] = { 10, 20, 30 };  // a=10, b=20, c=30
  return v[i++];
}
```

### 2. 多种类型混合使用

```c
#include <stdio.h>

extern int __VERIFIER_nondet_int(void);
extern float __VERIFIER_nondet_float(void);
extern unsigned char __VERIFIER_nondet_uchar(void);

int main(void) {
  int x = __VERIFIER_nondet_int();
  float y = __VERIFIER_nondet_float();
  unsigned char z = __VERIFIER_nondet_uchar();

  printf("%d %.2f %u\n", x, y, z);
  return 0;
}
```

**生成的 test_case_1.c**：
```c
int __VERIFIER_nondet_int(void) {
  static int i = 0;
  static const int v[] = { 42 };
  return v[i++];
}

float __VERIFIER_nondet_float(void) {
  static int i = 0;
  static const float v[] = { 3.14 };
  return v[i++];
}

unsigned char __VERIFIER_nondet_uchar(void) {
  static int i = 0;
  static const unsigned char v[] = { 255 };
  return v[i++];
}
```

### 3. 浮点数测试

```c
#include <stdio.h>
#include <math.h>

extern double __VERIFIER_nondet_double(void);

double compute_area(double radius) {
  return 3.14159 * radius * radius;
}

int main(void) {
  double r = __VERIFIER_nondet_double();
  double area = compute_area(r);
  printf("Area: %.2f\n", area);
  return 0;
}
```

**生成的 test_case_1.c**：
```c
double __VERIFIER_nondet_double(void) {
  static int i = 0;
  static const double v[] = { 5.0 };
  return v[i++];
}
```

## 类型自动识别

生成器会自动识别每个 `__VERIFIER_nondet_*` 调用的类型：

1. **分析SSA**: ESBMC在符号执行时记录每个nondet调用的类型
2. **提取类型信息**: 从SMT求解器获取具体类型（位宽、符号性等）
3. **映射到VERIFIER类型**: 使用 `type_to_verifier_string()` 映射
4. **生成对应函数**: 为每种类型生成独立的函数实现

## 类型映射规则

```cpp
// 内部类型 → VERIFIER类型
signedbv(8)   → char
signedbv(16)  → short
signedbv(32)  → int
signedbv(64)  → long

unsignedbv(8)  → uchar
unsignedbv(16) → ushort
unsignedbv(32) → uint
unsignedbv(64) → ulong

floatbv(32)   → float
floatbv(64)   → double

bool          → bool
pointer       → pointer
```

## 常见问题

### Q1: 为什么只生成了一个值？

**A**: 之前的bug已修复。现在使用LHS变量名去重，确保每次nondet调用都被收集：

```cpp
// 修复前：按nondet符号名去重（错误）
if (seen_nondets.count(sym.thename.as_string()))
  continue;

// 修复后：按LHS变量名去重（正确）
if (seen_lhs.count(lhs_name))
  continue;
```

### Q2: 如何验证生成的类型是否正确？

**A**: 查看生成的 `test_case_N.c` 文件：

```bash
cat test_case_1.c
```

确认：
- 函数签名正确（如 `int __VERIFIER_nondet_int(void)`）
- 数组类型匹配（如 `static const int v[]`）
- 值的数量与调用次数一致

### Q3: 支持自定义类型吗？

**A**: 目前只支持SV-COMP标准的基本类型。对于结构体或数组，需要：
- 使用多个基本类型的nondet调用
- 或手动修改生成的测试用例

## 完整工作流程

```bash
# 1. 准备源代码（使用任意支持的类型）
cat > test.c << 'EOF'
extern int __VERIFIER_nondet_int(void);
extern float __VERIFIER_nondet_float(void);

int main() {
  int x = __VERIFIER_nondet_int();
  float y = __VERIFIER_nondet_float();
  return (x > 0 && y > 0.0) ? 0 : 1;
}
EOF

# 2. 生成测试用例
esbmc test.c --branch-coverage --generate-ctest-testcase

# 3. 查看生成的文件
ls -l test_case_*.c

# 4. 检查类型
cat test_case_1.c

# 5. 编译运行
mkdir build && cd build
cmake -DENABLE_COVERAGE=ON ..
make
ctest

# 6. 查看覆盖率
gcovr -r . --branches
```

## 扩展类型支持

如果需要添加新类型支持，修改 `type_to_verifier_string()` 函数：

```cpp
std::string ctest_generator::type_to_verifier_string(const type2tc &type) const
{
  // 添加新类型映射
  if (is_your_custom_type(type))
  {
    return "your_custom_type";
  }
  // ...
}
```

对应的C类型映射在 `type_to_c_string()` 中定义。
