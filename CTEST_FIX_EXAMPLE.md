# CTest Variable Naming Fix

## 问题描述

之前生成的CTest测试用例包含无效的C变量名，例如：

```c
// ❌ 错误的输出（修复前）
int main() {
    int main::$tmp::return_value$___VERIFIER_nondet_int$2 = 127;
    // ...
}
```

这些变量名包含ESBMC内部标记（`::`、`$`、`return_value`等），在C中是无效的。

## 修复方案

### 1. 改进 `clean_variable_name()` 函数

现在会移除所有ESBMC内部标记：
- 移除 `::` 命名空间分隔符
- 移除 `$tmp::` 临时变量标记
- 移除 `return_value$` 返回值标记
- 移除所有 `$` 字符
- 对于包含 `__VERIFIER_` 的变量，返回空字符串触发回退命名

### 2. 回退命名策略

当无法提取有效的用户变量名时，使用简单的命名：`value_0`, `value_1`, `value_2` 等

## 修复后的输出

```c
// ✅ 正确的输出（修复后）
int main() {
    int value_0 = 127;  // 清晰、有效的C变量名
    // ...
}
```

## 示例对比

### 输入代码
```c
#include <assert.h>

int __VERIFIER_nondet_int();

int main() {
    int x = __VERIFIER_nondet_int();
    int y = __VERIFIER_nondet_int();
    assert(x + y < 100);
    return 0;
}
```

### 修复前生成的测试用例
```c
int main() {
    int main::$tmp::return_value$___VERIFIER_nondet_int$1 = 50;  // ❌ 无效
    int main::$tmp::return_value$___VERIFIER_nondet_int$2 = 60;  // ❌ 无效
    return 0;
}
```

### 修复后生成的测试用例
```c
int main() {
    int x = 50;       // ✅ 如果能识别原始变量名
    int y = 60;       // ✅
    // 或者
    int value_0 = 50; // ✅ 使用回退命名
    int value_1 = 60; // ✅
    return 0;
}
```

## 关键改进

1. **变量名清理**：完全移除ESBMC内部标记，确保生成的是有效的C标识符
2. **回退机制**：当无法提取原始变量名时，使用简单、可靠的命名策略
3. **一致性**：与pytest实现保持一致，使用清晰的参数名

## Coverage计算方式

和pytest一样：
- 每个测试用例是独立的可执行文件
- 每个测试运行时生成自己的 `.gcda` 覆盖率文件
- lcov合并所有 `.gcda` 文件计算总体覆盖率

```bash
# 运行所有测试
ctest

# 合并覆盖率数据
lcov --capture --directory . -o coverage.info
genhtml coverage.info -o coverage_html
```
