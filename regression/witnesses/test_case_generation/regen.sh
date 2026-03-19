#!/usr/bin/env bash
# regen.sh — Re-run ESBMC to regenerate CTest artefacts for all ctest_gen_*
# directories.
#
# Usage:
#   ./regen.sh [ESBMC_BINARY]
#
# ESBMC_BINARY defaults to "esbmc" on $PATH.  Pass an absolute path when
# using a local build, e.g.:
#   ./regen.sh /home/user/esbmc/build/src/esbmc/esbmc

set -euo pipefail

ESBMC="${1:-esbmc}"

if ! command -v "$ESBMC" &>/dev/null && [[ ! -x "$ESBMC" ]]; then
  echo "ERROR: esbmc binary not found: $ESBMC" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pass=0
fail=0
skip=0

for dir in "$SCRIPT_DIR"/ctest_gen_*/; do
  [[ -d "$dir" ]] || continue

  # Determine source file from test.desc (line 2) when present,
  # otherwise fall back to main.c / main.cpp.
  desc="$dir/test.desc"
  if [[ -f "$desc" ]]; then
    src_file="$(sed -n '2p' "$desc")"
  elif [[ -f "$dir/main.cpp" ]]; then
    src_file="main.cpp"
  elif [[ -f "$dir/main.c" ]]; then
    src_file="main.c"
  else
    echo "SKIP  $(basename "$dir")  (no source file found)"
    (( skip++ )) || true
    continue
  fi

  if [[ ! -f "$dir/$src_file" ]]; then
    echo "SKIP  $(basename "$dir")  (source '$src_file' missing)"
    (( skip++ )) || true
    continue
  fi

  # Remove previously generated artefacts so stale files don't linger.
  (
    cd "$dir"
    rm -f CMakeLists.txt esbmc_verifier.h test_case_*.c test_case_*.cpp
  )

  # Run esbmc from inside the directory so all outputs land there.
  if (
    cd "$dir"
    "$ESBMC" "$src_file" --branch-coverage --generate-ctest-testcase \
      >"esbmc.log" 2>&1
  ); then
    echo "OK    $(basename "$dir")"
    (( pass++ )) || true
  else
    echo "FAIL  $(basename "$dir")  (see $(basename "$dir")/esbmc.log)"
    (( fail++ )) || true
  fi
done

echo ""
echo "Results: $pass ok, $fail failed, $skip skipped"
[[ $fail -eq 0 ]]
