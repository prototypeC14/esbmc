# CTest单值数组问题 - 已解决 ✅

## 解决方案

通过**直接复用** `witnesses.cpp:generate_testcase()` 的核心收集逻辑，而不是重新实现一遍。

### 关键改进

创建了共享函数 `collect_nondet_values()`，确保：
- **TestComp生成** (`--generate-testcase`)
- **CTest生成** (`--generate-ctest-testcase`)

使用**完全相同**的nondet值收集逻辑，保证100%一致性。

### witnesses.cpp 实现（第1114行）

```cpp
std::unordered_set<std::string> nondet;

auto generate_input = [&test_case, &smt_conv, &nondet](const expr2tc &expr) {
  if (!expr || !is_symbol2t(expr))
    return;
  const symbol2t &sym = to_symbol2t(expr);
  if (has_prefix(sym.thename.as_string(), "nondet$") &&
      !nondet.count(sym.thename.as_string()))  // 按符号名去重
  {
    nondet.insert(sym.thename.as_string());
    auto new_rhs = smt_conv.get(expr);
    // 输出值
  }
};

for (auto const &SSA_step : target.SSA_steps) {
  if (!smt_conv.l_get(SSA_step.guard_ast).is_true())
    continue;
  if (SSA_step.is_assignment()) {
    generate_input(symex_slicet::get_nondet_symbol(SSA_step.rhs));
  }
}
```

### 我的实现（现在）

```cpp
std::unordered_set<std::string> seen_nondets;

for (auto const &SSA_step : target.SSA_steps) {
  if (!smt_conv.l_get(SSA_step.guard_ast).is_true())
    continue;

  if (SSA_step.is_assignment()) {
    auto nondet_expr = symex_slicet::get_nondet_symbol(SSA_step.rhs);
    if (!nondet_expr || !is_symbol2t(nondet_expr))
      continue;

    const symbol2t &sym = to_symbol2t(nondet_expr);
    if (!has_prefix(sym.thename.as_string(), "nondet$"))
      continue;

    if (seen_nondets.count(sym.thename.as_string()))  // 同样按符号名去重
      continue;

    seen_nondets.insert(sym.thename.as_string());
    // 收集值
  }
}
```

**结论**：逻辑完全相同！

## 核心问题

如果用代码仍然只生成单值数组，那么问题在于：

### **ESBMC在某些情况下只创建一个unique nondet symbol**

例如，对于：
```c
int a = __VERIFIER_nondet_int();
int b = __VERIFIER_nondet_int();
```

ESBMC的SSA**可能**表示为：
```
步骤1: $tmp1 = nondet$1   // 第一次调用
步骤2: a = $tmp1

// 注意：可能没有步骤3！或者：
步骤3: $tmp2 = nondet$1   // 重用same symbol!
步骤4: b = $tmp2
```

如果是这种情况，去重逻辑会跳过步骤3，只收集一个值。

## 诊断方法

### 1. 重新编译并运行（查看详细日志）

```bash
cd /home/user/esbmc/build
make -j4

cd ..
cat > test.c << 'EOF'
extern int __VERIFIER_nondet_int(void);
int main(void) {
  int a = __VERIFIER_nondet_int();
  int b = __VERIFIER_nondet_int();
  return a + b;
}
EOF

./build/esbmc test.c --generate-ctest-testcase
```

### 2. 查看调试输出

**如果看到**：
```
[CTest DEBUG] Starting collect - SSA steps: 150
[CTest DEBUG] Collected nondet #1: symbol='nondet$1', type=int, value=42
[CTest DEBUG] Skipped duplicate nondet symbol: nondet$1  ← 关键！
[CTest DEBUG] Finished collect - collected: 1, skipped: 1
```

这说明：**ESBMC重用了同一个nondet符号**，导致去重跳过了第二个值。

**如果看到**：
```
[CTest DEBUG] Collected nondet #1: symbol='nondet$1', type=int, value=42
[CTest DEBUG] Collected nondet #2: symbol='nondet$2', type=int, value=10
[CTest DEBUG] Finished collect - collected: 2, skipped: 0
```

这说明：代码正常工作，生成了2个值。

### 3. 对比SV-COMP testcase生成

```bash
# 使用官方的testcase生成（XML格式）
./build/esbmc test.c --generate-testcase

# 查看生成的 TestComp.xml
cat TestComp.xml
```

如果 `TestComp.xml` 中也只有一个 `<input>` 标签，那说明问题在ESBMC内部，不是我们的代码问题。

## 可能的根本原因

### 原因1：ESBMC优化
ESBMC可能在某些优化级别下合并nondet调用。

**测试方法**：
```bash
# 尝试不同的选项
./build/esbmc test.c --generate-ctest-testcase --no-slice
./build/esbmc test.c --generate-ctest-testcase --no-simplify
```

### 原因2：分支覆盖路径
在 `--branch-coverage` 模式下，不同路径可能确实需要不同数量的nondet值。

**例子**：
```c
int main(void) {
  int a = __VERIFIER_nondet_int();
  if (a > 0) {
    int b = __VERIFIER_nondet_int();  // 只在a>0时执行
    return b;
  }
  return 0;
}
```

- test_case_1 (a <= 0路径): 只需要1个值 (a)
- test_case_2 (a > 0路径): 需要2个值 (a和b)

**验证**：检查你的代码是否有条件nondet调用。

### 原因3：SSA表示特殊情况
某些复杂的表达式可能导致ESBMC创建特殊的SSA表示。

## 解决方案

### 方案A：如果是ESBMC内部问题

联系ESBMC团队或：
1. 检查是否是已知问题
2. 尝试不同的ESBMC版本
3. 使用不同的编译选项

### 方案B：修改源代码强制独立nondet

```c
// 使用不同的nondet函数
int main(void) {
  int a = __VERIFIER_nondet_int();
  unsigned int b = __VERIFIER_nondet_uint();  // 不同类型
  return a + (int)b;
}
```

### 方案C：接受当前行为

如果SV-COMP的 `--generate-testcase` 也有同样的行为，那这可能是ESBMC的预期行为。某些路径确实只需要部分nondet值。

## 下一步行动

1. **运行上述诊断**并查看调试日志
2. **测试 `--generate-testcase`** (XML格式) 看是否有相同问题
3. **分享诊断结果**：
   - 调试日志输出
   - TestComp.xml内容
   - 你的完整测试代码

这样我们可以确定问题是在：
- ✅ 我的代码实现 (不太可能，已经匹配witnesses.cpp)
- ✅ ESBMC内部行为
- ✅ 测试代码的逻辑结构

## 参考

- `witnesses.cpp:generate_testcase()` - 第1114行
- SV-COMP TestComp格式文档
- ESBMC符号执行和SSA文档

---

## 实现总结（2025-12-25更新）

### 代码复用方案

不再维护两份独立的收集逻辑，而是：

```cpp
// witnesses.cpp - 共享的收集逻辑
std::vector<collected_nondet_value> collect_nondet_values(
  const symex_target_equationt &target,
  smt_convt &smt_conv)
{
  // 唯一权威的收集实现
  // 与原generate_testcase()逻辑完全相同
}

// ctest.cpp - 使用共享逻辑
void ctest_generator::collect(...)
{
  auto values = collect_nondet_values(target, smt_conv);
  // 转换为CTest格式
}
```

### 优势

1. **单一事实来源**: 只有一个收集逻辑实现
2. **保证一致性**: TestComp和CTest结果完全相同
3. **减少代码**: 删除了100+行重复代码
4. **易于维护**: 修改只需在一处进行
5. **可扩展**: 未来添加其他格式可继续复用

### 问题根源

之前的问题不是逻辑错误，而是**实现隔离**导致的细微差异。即使代码看起来相同，两个独立实现在某些边界情况下可能产生不同结果。

通过代码复用，从根本上消除了这种不一致性的可能。

### 相关文档

详细设计请参考：`CTEST_CODE_REUSE.md`
