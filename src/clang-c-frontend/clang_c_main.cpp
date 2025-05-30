#include <cassert>
#include <util/arith_tools.h>
#include <util/c_types.h>
#include <util/config.h>
#include <util/expr_util.h>
#include <util/message.h>
#include <util/namespace.h>
#include <util/std_code.h>
#include <util/std_expr.h>
#include <clang-c-frontend/clang_c_main.h>

void clang_c_maint::init_variable(codet &dest, const symbolt &sym)
{
  const exprt &value = sym.value;

  if (value.is_nil())
    return;

  assert(!value.type().is_code());

  exprt symbol("symbol", sym.type);
  symbol.identifier(sym.id);

  code_assignt code(symbol, sym.value);
  code.location() = sym.location;

  codet adjusted("decl-block");
  adjust_init(code, adjusted);

  dest.move_to_operands(adjusted.has_operands() ? adjusted : code);
}

void clang_c_maint::adjust_init(code_assignt &, codet &)
{
  // currently nothing to be adjusted for C
}

void clang_c_maint::static_lifetime_init(const contextt &context, codet &dest)
{
  dest = code_blockt();

  // Do assignments based on "value".
  context.foreach_operand_in_order([&dest, this](const symbolt &s) {
    if (s.static_lifetime)
      init_variable(dest, s);
  });

  // call designated "initialization" functions
  context.foreach_operand_in_order([&dest](const symbolt &s) {
    if (s.type.initialization() && s.type.is_code())
    {
      code_function_callt function_call;
      function_call.function() = symbol_expr(s);
      dest.move_to_operands(function_call);
    }
  });
}

bool clang_c_maint::clang_main()
{
  irep_idt main_symbol;

  std::string main = (config.main != "") ? config.main : "main";

  // find main symbol
  std::list<irep_idt> matches;

  forall_symbol_base_map (it, context.symbol_base_map, main)
  {
    // if user provided class/contract name
    if (!config.cname.empty() && !config.main.empty())
    {
      // Allow user to provide a range. e.g.
      // --class "A B" --function test
      // --contract "Base Derieve" --function _ESBMC_main
      // yet only the first matched one will get verified
      std::istringstream iss(config.cname);
      std::string tgt_cname;
      bool is_found_sym = false;
      while (iss >> tgt_cname)
      {
        const std::string fmt = "@" + tgt_cname + "@F@" + main;
        if (it->second.as_string().find(fmt) != std::string::npos)
        {
          is_found_sym = true;
          break;
        }
      }
      if (is_found_sym)
      {
        symbolt *s = context.find_symbol(it->second);
        if (s != nullptr && s->type.is_code())
          matches.push_back(it->second);
        break; // prevent ambiguous
      }
    }
    else
    {
      // look it up
      symbolt *s = context.find_symbol(it->second);
      if (s != nullptr && s->type.is_code())
        matches.push_back(it->second);
    }
  }

  if (matches.empty())
  {
    log_error("main symbol `{}' not found", main);
    return true; // give up
  }

  if (matches.size() >= 2)
  {
    log_error("main symbol `{}' is ambiguous", main);
    return true;
  }

  main_symbol = matches.front();

  // look it up
  symbolt *s = context.find_symbol(main_symbol);
  if (s == nullptr)
    return false; // give up, no main

  const symbolt &symbol = *s;

  // check if it has a body
  if (symbol.value.is_nil())
    return false; // give up

  codet init_code;

  static_lifetime_init(context, init_code);

  init_code.make_block();
  init_code.end_location(symbol.value.end_location());

  // build call to function

  code_function_callt call;
  call.location() = symbol.location;
  call.function() = symbol_expr(symbol);

  const code_typet::argumentst &arguments =
    to_code_type(symbol.type).arguments();

  if (symbol.name == "main")
  {
    if (arguments.size() == 0)
    {
      // ok
    }
    else if (arguments.size() == 2 || arguments.size() == 3)
    {
      namespacet ns(context);

      const symbolt &argc_symbol = *ns.lookup("argc'");
      const symbolt &argv_symbol = *ns.lookup("argv'");

      exprt one = from_integer(1, argc_symbol.type);

      exprt add("+", uint_type());
      add.copy_to_operands(symbol_expr(argc_symbol), one); // argc + 1

      exprt mult("*", uint_type());
      exprt char_pointer_size = from_integer(
        config.ansi_c.pointer_width() / config.ansi_c.char_width, uint_type());
      mult.copy_to_operands(
        add, char_pointer_size); // (argc + 1) * sizeof(char *)

      // assume argc is at least one
      exprt ge(">=", bool_type());
      ge.copy_to_operands(symbol_expr(argc_symbol), one);

      init_code.copy_to_operands(code_assumet(ge));

      // assume argc is at most MAX-1
      BigInt max;

      if (argc_symbol.type.id() == "signedbv")
        max = power(2, atoi(argc_symbol.type.width().c_str()) - 1) - 1;
      else if (argc_symbol.type.id() == "unsignedbv")
        max = power(2, atoi(argc_symbol.type.width().c_str())) - 1;
      else
        assert(false);

      // The argv array of MAX elements of pointer type has to fit
      max /= config.ansi_c.pointer_width() / 8;

      exprt max_minus_one = from_integer(max - 1, argc_symbol.type);

      exprt le("<=", bool_type());
      le.copy_to_operands(symbol_expr(argc_symbol), max_minus_one);

      init_code.copy_to_operands(code_assumet(le));

      // assign argv = { NULL };
      // Adjust __ESBMC_alloc_size as argv is handled as dynamic array
      exprt dynamic_size("dynamic_size", size_type());
      dynamic_size.copy_to_operands(gen_address_of(symbol_expr(argv_symbol)));
      init_code.copy_to_operands(code_assignt(dynamic_size, mult));

      constant_exprt null(
        irep_idt("NULL"), integer2string(0), argv_symbol.type.subtype());

      // Define an array type
      array_typet argv_type(argv_symbol.type.subtype(), dynamic_size);

      // Create an array filled with NULL (no explicit size)
      array_of_exprt null_array(null, argv_type);

      // Assign the initialized array to argv_symbol
      // disable bounds check on that one
      // Logic to perform this ^ moved into goto_check and dereference,
      // rather than load irep2 with additional baggage.
      init_code.copy_to_operands(
        code_assignt(symbol_expr(argv_symbol), null_array));

      exprt::operandst &operands = call.arguments();

      if (arguments.size() == 3)
        operands.resize(3);
      else
        operands.resize(2);

      exprt &op0 = operands[0];
      exprt &op1 = operands[1];

      op0 = symbol_expr(argc_symbol);

      const exprt &arg1 = arguments[1];

      index_exprt arg1_index(
        symbol_expr(argv_symbol),
        gen_zero(index_type()),
        arg1.type().subtype());

      // disable bounds check on that one
      // Logic to perform this ^ moved into goto_check, rather than load
      // irep2 with additional baggage.

      op1 = exprt("address_of", arg1.type());
      op1.move_to_operands(arg1_index);

      if (arguments.size() == 3)
      {
        const symbolt &envp_symbol = *ns.lookup("envp'");
        const symbolt &envp_size_symbol = *ns.lookup("envp_size'");

        exprt envp_ge(">=", bool_type());
        envp_ge.copy_to_operands(symbol_expr(envp_size_symbol), one);

        init_code.copy_to_operands(code_assumet(envp_ge));

        // assume envp_size is at most MAX-1

        exprt envp_le("<=", bool_type());
        envp_le.copy_to_operands(symbol_expr(envp_size_symbol), max_minus_one);

        init_code.copy_to_operands(code_assumet(envp_le));

        index_exprt envp_index(
          symbol_expr(envp_symbol),
          symbol_expr(envp_size_symbol),
          envp_symbol.type.subtype());

        // disable bounds check on that one
        // Logic to perform this ^ moved into goto_check, rather than load
        // irep2 with additional baggage.

        exprt is_null("=", bool_type());
        is_null.copy_to_operands(envp_index, null);

        init_code.copy_to_operands(code_assumet(is_null));

        exprt &op2 = operands[2];
        const exprt &arg2 = arguments[2];

        index_exprt arg2_index(
          symbol_expr(envp_symbol),
          gen_zero(index_type()),
          arg2.type().subtype());

        op2 = exprt("address_of", arg2.type());
        op2.move_to_operands(arg2_index);
      }
    }
    else
      assert(false);
  }
  else
  {
    call.arguments().resize(
      arguments.size(), static_cast<const exprt &>(get_nil_irep()));
  }

  // Call to main symbol is now in "call"; construct calls to thread library
  // hooks for main thread start and main thread end.

  code_function_callt thread_start_call;
  thread_start_call.location() = symbol.location;
  thread_start_call.function() =
    symbol_exprt("c:@F@__ESBMC_pthread_start_main_hook");
  code_function_callt thread_end_call;
  thread_end_call.location() = symbol.location;
  thread_end_call.function() =
    symbol_exprt("c:@F@__ESBMC_pthread_end_main_hook");

  code_function_callt atexit_call;
  atexit_call.location() = symbol.location;
  atexit_call.function() = symbol_exprt("c:@F@__ESBMC_atexit_handler");

  init_code.move_to_operands(thread_start_call);
  init_code.move_to_operands(call);
  init_code.move_to_operands(atexit_call);
  init_code.move_to_operands(thread_end_call);

  // add "main"
  symbolt new_symbol;

  code_typet main_type;
  main_type.return_type() = empty_typet();

  new_symbol.id = "__ESBMC_main";
  new_symbol.name = "__ESBMC_main";
  new_symbol.type.swap(main_type);
  new_symbol.value.swap(init_code);

  if (context.move(new_symbol))
  {
    log_error("main already defined by another language module");
    return true;
  }

  return false;
}
