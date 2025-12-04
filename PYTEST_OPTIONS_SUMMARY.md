# Python Pytest Generation - Command Options

## 两种方式 (Two Options)

### ✅ 方法1: `--generate-python-testcase` （推荐 / Recommended）

**专门用于Python的pytest生成**

```bash
# 基础用法
esbmc example.py --generate-python-testcase
# 输出: test_counterexample.py

# 多个counterexample
esbmc example.py --multi-property --generate-python-testcase
# 输出: test_counterexample_1.py, test_counterexample_2.py, ...
```

**优点:**
- ✅ 明确的意图（专门用于Python）
- ✅ 适合CI/CD（无歧义）
- ✅ 简洁清晰

### 🔄 方法2: `--generate-testcase` （通用）

**自动检测文件类型**

```bash
# Python文件 → 生成pytest格式
esbmc example.py --generate-testcase

# C文件 → 生成XML格式（Test-Comp）
esbmc example.c --generate-testcase
```

**优点:**
- ✅ 一个命令支持多种语言
- ✅ 向后兼容

## 快速对比

| 选项 | Python (.py) | C (.c) | 推荐场景 |
|------|-------------|--------|---------|
| `--generate-python-testcase` | pytest ✅ | ❌ 不支持 | Python专项 |
| `--generate-testcase` | pytest ✅ | XML ✅ | 混合项目 |

## 实际例子

### 场景1: 纯Python项目

```bash
# 推荐使用
esbmc src/calculator.py --generate-python-testcase
pytest test_counterexample.py
```

### 场景2: Python + C 混合项目

```bash
# 使用自动检测
esbmc src/module.py --generate-testcase    # → pytest
esbmc src/core.c --generate-testcase       # → XML
```

### 场景3: CI/CD Pipeline

```yaml
# .gitlab-ci.yml
test-generation:
  script:
    - esbmc **/*.py --generate-python-testcase  # 明确指定
    - pytest test_counterexample_*.py
```

## 查看帮助

```bash
esbmc --help | grep "generate.*testcase"
```

输出:
```
--generate-testcase              generate test case from counterexample (XML for C, pytest for Python)
--generate-python-testcase       generate pytest test case from counterexample (Python only)
```

## 完整工作流

```bash
# 1. 创建Python代码
cat > bug.py << 'EOF'
def divide(x, y):
    return x / y

result = divide(10, 0)  # Bug!
EOF

# 2. 生成pytest测试（两种方式任选）
esbmc bug.py --generate-python-testcase
# 或
esbmc bug.py --generate-testcase

# 3. 运行测试
pytest test_counterexample.py -v

# 输出:
# test_divide_counterexample PASSED ✓
```

## 技术细节

### 实现位置
- **命令行定义**: `src/esbmc/options.cpp:209-211`
- **逻辑处理**: `src/esbmc/bmc.cpp:156-180, 501-532`
- **生成函数**: `src/goto-symex/witnesses.cpp:1179-1432`

### 判断逻辑
```cpp
if (options.get_bool_option("generate-python-testcase")) {
  // 总是生成pytest
  generate_testcase_python(...);
}
else if (options.get_bool_option("generate-testcase")) {
  // 自动检测文件类型
  if (input_file.ends_with(".py"))
    generate_testcase_python(...);  // pytest
  else
    generate_testcase(...);          // XML
}
```

## 更多文档

- **快速入门**: [QUICKSTART_PYTEST_GENERATION.md](QUICKSTART_PYTEST_GENERATION.md)
- **完整文档**: [PYTEST_GENERATION.md](PYTEST_GENERATION.md)
