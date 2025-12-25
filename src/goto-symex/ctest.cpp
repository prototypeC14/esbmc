#include <goto-symex/ctest.h>
#include <goto-symex/slice.h>
#include <ac_config.h>
#include <util/prefix.h>
#include <util/message/format.h>
#include <irep2/irep2_expr.h>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <fstream>
#include <unordered_set>

std::string ctest_generator::clean_variable_name(const std::string &name) const
{
  std::string var_name = name;

  // Remove everything before the last '@' (symbol mangling)
  size_t at_pos = var_name.rfind('@');
  if (at_pos != std::string::npos)
    var_name = var_name.substr(at_pos + 1);

  // Remove everything after '!' (SSA suffix)
  size_t exclaim_pos = var_name.find('!');
  if (exclaim_pos != std::string::npos)
    var_name = var_name.substr(0, exclaim_pos);

  // Remove everything after '?' (other suffix)
  size_t question_pos = var_name.find('?');
  if (question_pos != std::string::npos)
    var_name = var_name.substr(0, question_pos);

  // Remove "c::main::" or "c::" prefix if present
  if (has_prefix(var_name, "c::main::"))
    var_name = var_name.substr(9);
  else if (has_prefix(var_name, "c::"))
    var_name = var_name.substr(3);

  return var_name;
}

std::string ctest_generator::extract_function_name(
  const symex_target_equationt &target,
  smt_convt &smt_conv) const
{
  // Try to extract function name from SSA steps
  for (auto const &SSA_step : target.SSA_steps)
  {
    if (!smt_conv.l_get(SSA_step.guard_ast).is_true())
      continue;

    if (SSA_step.source.pc->location.function() != "")
    {
      std::string full_func = SSA_step.source.pc->location.function().as_string();

      // Skip internal functions
      if (!has_prefix(full_func, "__ESBMC_") &&
          !has_prefix(full_func, "__VERIFIER_") &&
          full_func != "c::__ESBMC_main")
      {
        // Clean up function name (remove "c::" prefix if present)
        if (has_prefix(full_func, "c::"))
          return full_func.substr(3);
        else
          return full_func;
      }
    }
  }

  return "main";  // Default to main
}

std::string ctest_generator::type_to_c_string(const type2tc &type) const
{
  if (is_signedbv_type(type) || is_unsignedbv_type(type))
  {
    unsigned width = type->get_width();
    if (is_signedbv_type(type))
    {
      if (width == 8) return "char";
      if (width == 16) return "short";
      if (width == 32) return "int";
      if (width == 64) return "long long";
      return "int";  // Default
    }
    else
    {
      if (width == 8) return "unsigned char";
      if (width == 16) return "unsigned short";
      if (width == 32) return "unsigned int";
      if (width == 64) return "unsigned long long";
      return "unsigned int";  // Default
    }
  }
  else if (is_floatbv_type(type))
  {
    unsigned width = type->get_width();
    if (width == 32) return "float";
    if (width == 64) return "double";
    return "double";  // Default
  }
  else if (is_bool_type(type))
  {
    return "int";  // C uses int for bool
  }
  else if (is_pointer_type(type))
  {
    return "void*";
  }

  return "int";  // Fallback
}

std::string ctest_generator::format_c_value(
  const expr2tc &value,
  const type2tc &type) const
{
  if (is_constant_int2t(value))
  {
    return integer2string(to_constant_int2t(value).value);
  }
  else if (is_constant_floatbv2t(value))
  {
    return to_constant_floatbv2t(value).value.to_ansi_c_string();
  }
  else if (is_constant_bool2t(value))
  {
    return to_constant_bool2t(value).value ? "1" : "0";
  }

  return "0";  // Fallback
}

void ctest_generator::clear()
{
  std::lock_guard<std::mutex> lock(data_mutex);
  test_cases.clear();
  function_name.clear();
  source_file.clear();
}

void ctest_generator::collect(
  const symex_target_equationt &target,
  smt_convt &smt_conv,
  const namespacet &ns)
{
  (void)ns;  // May be used later

  std::vector<test_variable> current_test;
  std::unordered_set<std::string> seen_nondets;

  // Extract function name if not already set
  std::string extracted_func_name;
  if (function_name.empty())
    extracted_func_name = extract_function_name(target, smt_conv);

  // Extract nondet values from counterexample
  for (auto const &SSA_step : target.SSA_steps)
  {
    if (!smt_conv.l_get(SSA_step.guard_ast).is_true())
      continue;

    if (SSA_step.is_assignment())
    {
      // Extract variable name
      std::string var_name;
      if (is_symbol2t(SSA_step.lhs))
      {
        const symbol2t &lhs_sym = to_symbol2t(SSA_step.lhs);
        var_name = clean_variable_name(lhs_sym.get_symbol_name());
      }

      // Check if this is a nondet assignment
      auto nondet_expr = symex_slicet::get_nondet_symbol(SSA_step.rhs);
      if (!nondet_expr || !is_symbol2t(nondet_expr))
        continue;

      const symbol2t &sym = to_symbol2t(nondet_expr);
      if (!has_prefix(sym.thename.as_string(), "nondet$"))
        continue;

      if (seen_nondets.count(sym.thename.as_string()))
        continue;

      seen_nondets.insert(sym.thename.as_string());

      // Get concrete value and type
      auto concrete_value = smt_conv.get(nondet_expr);

      test_variable var;
      var.name = var_name;
      var.type = type_to_c_string(concrete_value->type);
      var.value = format_c_value(concrete_value, concrete_value->type);

      current_test.push_back(var);
    }
  }

  // Store collected data if we found any nondet values
  if (!current_test.empty())
  {
    std::lock_guard<std::mutex> lock(data_mutex);

    // Store function name if we found one
    if (!extracted_func_name.empty() && function_name.empty())
      function_name = extracted_func_name;

    // Store source file if not set
    if (source_file.empty())
      source_file = config.options.get_option("input-file");

    test_cases.push_back(current_test);
  }
}

bool ctest_generator::has_tests() const
{
  std::lock_guard<std::mutex> lock(data_mutex);
  return !test_cases.empty();
}

void ctest_generator::generate(const std::string &output_dir) const
{
  std::lock_guard<std::mutex> lock(data_mutex);

  if (test_cases.empty())
  {
    log_warning("No test cases collected. No CTest files generated.");
    return;
  }

  // Create output directory if needed (output_dir is actually a filename prefix)
  std::string dir_path = output_dir;
  size_t last_slash = dir_path.rfind('/');
  if (last_slash != std::string::npos)
    dir_path = dir_path.substr(0, last_slash);

  // Generate individual test case files
  std::vector<std::string> test_file_names;

  for (size_t i = 0; i < test_cases.size(); ++i)
  {
    std::string test_file_name = "test_case_" + std::to_string(i + 1) + ".c";
    test_file_names.push_back(test_file_name);

    std::ofstream test_file(test_file_name);

    // Header
    test_file << "// Auto-generated by ESBMC " << ESBMC_VERSION << "\n";
    test_file << "// Test case " << (i + 1) << " of " << test_cases.size() << "\n";
    test_file << "// Source: " << source_file << "\n\n";

    test_file << "#include <stdio.h>\n";
    test_file << "#include <assert.h>\n\n";

    // Main function with hardcoded values
    test_file << "int main() {\n";

    for (const auto &var : test_cases[i])
    {
      test_file << "    " << var.type << " " << var.name
                << " = " << var.value << ";\n";
    }

    test_file << "\n";
    test_file << "    // Call function under test (if not main)\n";
    if (function_name != "main" && !function_name.empty())
    {
      test_file << "    " << function_name << "(";
      for (size_t j = 0; j < test_cases[i].size(); ++j)
      {
        if (j > 0) test_file << ", ";
        test_file << test_cases[i][j].name;
      }
      test_file << ");\n";
    }
    else
    {
      test_file << "    // This test case exercises the main function logic\n";
      test_file << "    // Add your test assertions here\n";
    }

    test_file << "\n    return 0;\n";
    test_file << "}\n";

    test_file.close();
  }

  // Generate CMakeLists.txt
  std::ofstream cmake_file("CMakeLists.txt");

  cmake_file << "# Auto-generated by ESBMC " << ESBMC_VERSION << "\n";
  cmake_file << "cmake_minimum_required(VERSION 3.10)\n";
  cmake_file << "project(ESBMCGeneratedTests)\n\n";

  cmake_file << "# Enable coverage reporting\n";
  cmake_file << "option(ENABLE_COVERAGE \"Enable coverage reporting\" OFF)\n";
  cmake_file << "if(ENABLE_COVERAGE)\n";
  cmake_file << "    set(CMAKE_C_FLAGS \"${CMAKE_C_FLAGS} --coverage\")\n";
  cmake_file << "    set(CMAKE_CXX_FLAGS \"${CMAKE_CXX_FLAGS} --coverage\")\n";
  cmake_file << "endif()\n\n";

  cmake_file << "# Enable testing\n";
  cmake_file << "enable_testing()\n\n";

  for (size_t i = 0; i < test_file_names.size(); ++i)
  {
    std::string test_name = "test_case_" + std::to_string(i + 1);
    cmake_file << "add_executable(" << test_name << " " << test_file_names[i] << ")\n";
    cmake_file << "add_test(NAME " << test_name << " COMMAND " << test_name << ")\n";
    cmake_file << "set_tests_properties(" << test_name
               << " PROPERTIES WILL_FAIL TRUE)\n\n";
  }

  cmake_file.close();

  log_status("Generated {} CTest test case(s) with CMakeLists.txt", test_cases.size());
}

void ctest_generator::generate_single(
  const std::string &output_dir,
  const symex_target_equationt &target,
  smt_convt &smt_conv,
  const namespacet &ns)
{
  (void)output_dir;
  (void)ns;

  // Extract source file
  std::string src_file = config.options.get_option("input-file");

  // Track nondet symbols we've seen
  std::unordered_set<std::string> seen_nondets;
  std::vector<test_variable> test_vars;

  // Extract function name
  std::string func_name = extract_function_name(target, smt_conv);

  // Traverse SSA steps to extract nondet variables
  for (auto const &SSA_step : target.SSA_steps)
  {
    if (!smt_conv.l_get(SSA_step.guard_ast).is_true())
      continue;

    if (SSA_step.is_assignment())
    {
      // Extract the variable name from lhs
      std::string var_name;
      if (is_symbol2t(SSA_step.lhs))
      {
        const symbol2t &lhs_sym = to_symbol2t(SSA_step.lhs);
        var_name = clean_variable_name(lhs_sym.get_symbol_name());
      }

      // Check if this is a nondet assignment
      auto nondet_expr = symex_slicet::get_nondet_symbol(SSA_step.rhs);
      if (!nondet_expr || !is_symbol2t(nondet_expr))
        continue;

      const symbol2t &sym = to_symbol2t(nondet_expr);
      if (!has_prefix(sym.thename.as_string(), "nondet$"))
        continue;

      if (seen_nondets.count(sym.thename.as_string()))
        continue;

      seen_nondets.insert(sym.thename.as_string());

      // Get the concrete value from the solver
      auto concrete_value = smt_conv.get(nondet_expr);

      test_variable var;
      var.name = var_name;
      var.type = type_to_c_string(concrete_value->type);
      var.value = format_c_value(concrete_value, concrete_value->type);

      test_vars.push_back(var);
    }
  }

  if (test_vars.empty())
  {
    log_warning("No nondet variables found. No CTest test case generated.");
    return;
  }

  // Generate single test file
  std::string test_file_name = "test_case.c";
  std::ofstream test_file(test_file_name);

  test_file << "// Auto-generated by ESBMC " << ESBMC_VERSION << "\n";
  test_file << "// Source: " << src_file << "\n\n";

  test_file << "#include <stdio.h>\n";
  test_file << "#include <assert.h>\n\n";

  test_file << "int main() {\n";

  for (const auto &var : test_vars)
  {
    test_file << "    " << var.type << " " << var.name
              << " = " << var.value << ";\n";
  }

  test_file << "\n";
  if (func_name != "main" && !func_name.empty())
  {
    test_file << "    " << func_name << "(";
    for (size_t i = 0; i < test_vars.size(); ++i)
    {
      if (i > 0) test_file << ", ";
      test_file << test_vars[i].name;
    }
    test_file << ");\n";
  }
  else
  {
    test_file << "    // Test case for main function\n";
  }

  test_file << "\n    return 0;\n";
  test_file << "}\n";

  test_file.close();

  // Generate simple CMakeLists.txt
  std::ofstream cmake_file("CMakeLists.txt");

  cmake_file << "# Auto-generated by ESBMC " << ESBMC_VERSION << "\n";
  cmake_file << "cmake_minimum_required(VERSION 3.10)\n";
  cmake_file << "project(ESBMCGeneratedTest)\n\n";

  cmake_file << "option(ENABLE_COVERAGE \"Enable coverage reporting\" OFF)\n";
  cmake_file << "if(ENABLE_COVERAGE)\n";
  cmake_file << "    set(CMAKE_C_FLAGS \"${CMAKE_C_FLAGS} --coverage\")\n";
  cmake_file << "endif()\n\n";

  cmake_file << "enable_testing()\n\n";
  cmake_file << "add_executable(test_case test_case.c)\n";
  cmake_file << "add_test(NAME test_case COMMAND test_case)\n";
  cmake_file << "set_tests_properties(test_case PROPERTIES WILL_FAIL TRUE)\n";

  cmake_file.close();

  log_status("Generated CTest test case: {}", test_file_name);
}
