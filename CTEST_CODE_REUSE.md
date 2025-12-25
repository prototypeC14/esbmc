# CTest 代码复用重构

## 概述

CTest生成器现在**直接复用** `--generate-testcase` (TestComp XML生成) 的核心逻辑，确保100%一致性。

## 设计原理

### 问题

之前的实现中，CTest生成器和TestComp生成器各自实现了nondet值收集逻辑：

- `generate_testcase()`: 用于 `--generate-testcase` (生成TestComp.xml)
- `ctest_generator::collect()`: 用于 `--generate-ctest-testcase` (生成CTest)

虽然逻辑看起来相同，但在某些情况下结果不一致：
- TestComp: 正确生成2个值 (`-2147483633, 0` 和 `1, 0`)
- CTest: 某些路径只生成1个值

### 解决方案

提取共享的收集逻辑到独立函数：

```cpp
// witnesses.h
struct collected_nondet_value
{
  std::string symbol_name;  // e.g., "nondet$symex::nondet3"
  expr2tc value_expr;       // The concrete value expression
  type2tc type;             // The type
};

std::vector<collected_nondet_value> collect_nondet_values(
  const symex_target_equationt &target,
  smt_convt &smt_conv);
```

### 使用方式

**TestComp (witnesses.cpp):**
```cpp
void generate_testcase(
  const std::string &file_name,
  const symex_target_equationt &target,
  smt_convt &smt_conv)
{
  auto values = collect_nondet_values(target, smt_conv);

  // Output to XML
  for (const auto &val : values) {
    if (is_constant_int2t(val.value_expr))
      test_case << "<input>" << to_constant_int2t(val.value_expr).value << "</input>\n";
    // ...
  }
}
```

**CTest (ctest.cpp):**
```cpp
void ctest_generator::collect(
  const symex_target_equationt &target,
  smt_convt &smt_conv,
  const namespacet &ns)
{
  auto values = collect_nondet_values(target, smt_conv);

  // Convert to test_variable format
  for (const auto &val : values) {
    test_variable var;
    var.verifier_type = type_to_verifier_string(val.type);
    var.c_type = type_to_c_string(val.type);
    var.value = format_c_value(val.value_expr, val.type);
    current_test.push_back(var);
  }
}
```

## 优势

1. **唯一权威源**: `collect_nondet_values()` 是唯一的收集逻辑实现
2. **100%一致性**: CTest和TestComp保证使用完全相同的收集逻辑
3. **代码复用**: 减少重复代码，降低维护成本
4. **易于调试**: 只需在一个地方修改和调试收集逻辑
5. **可扩展性**: 未来添加其他测试格式时可继续复用

## 实现细节

### collect_nondet_values() 核心逻辑

```cpp
std::vector<collected_nondet_value> collect_nondet_values(
  const symex_target_equationt &target,
  smt_convt &smt_conv)
{
  std::vector<collected_nondet_value> results;
  std::unordered_set<std::string> seen_nondets;

  for (auto const &SSA_step : target.SSA_steps)
  {
    // 只处理guard为true的步骤
    if (!smt_conv.l_get(SSA_step.guard_ast).is_true())
      continue;

    if (SSA_step.is_assignment())
    {
      auto nondet_expr = symex_slicet::get_nondet_symbol(SSA_step.rhs);
      if (!nondet_expr || !is_symbol2t(nondet_expr))
        continue;

      const symbol2t &sym = to_symbol2t(nondet_expr);
      if (!has_prefix(sym.thename.as_string(), "nondet$"))
        continue;

      // 按符号名去重
      if (seen_nondets.count(sym.thename.as_string()))
        continue;

      seen_nondets.insert(sym.thename.as_string());

      // 获取具体值
      auto concrete_value = smt_conv.get(nondet_expr);

      collected_nondet_value val;
      val.symbol_name = sym.thename.as_string();
      val.value_expr = concrete_value;
      val.type = concrete_value->type;

      results.push_back(val);
    }
  }

  return results;
}
```

### 类型转换

CTest生成器添加了额外的类型映射层：

- `type_to_verifier_string()`: 将类型映射到VERIFIER函数名 (如 "int", "uint", "float")
- `type_to_c_string()`: 将类型映射到C类型 (如 "int", "unsigned int", "float")
- `format_c_value()`: 将值格式化为C代码字符串

## 测试验证

```bash
cd /home/user/esbmc

# 使用TestComp格式
./build/esbmc example_compute.c --branch-coverage --generate-testcase
cat TestComp.xml

# 使用CTest格式
./build/esbmc example_compute.c --branch-coverage --generate-ctest-testcase
cat test_case_1.c test_case_2.c

# 两者应该收集到相同数量的nondet值
```

## 文件结构

```
src/goto-symex/
├── witnesses.h           # 声明 collect_nondet_values()
├── witnesses.cpp         # 实现 collect_nondet_values()
│                         # 和 generate_testcase() (使用shared logic)
├── ctest.h              # CTest生成器声明
└── ctest.cpp            # CTest生成器实现 (使用shared logic)
```

## 相关文档

- `CTEST_NEW_FORMAT.md`: CTest生成格式说明
- `CTEST_SUPPORTED_TYPES.md`: 支持的类型列表
- `FINAL_ANALYSIS.md`: 单值数组问题分析（已通过代码复用解决）
