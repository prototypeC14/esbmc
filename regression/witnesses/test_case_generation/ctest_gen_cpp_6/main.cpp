// No extern "C" declarations for __VERIFIER_* functions.
// This simulates real-world C++ code verified by ESBMC, where the tool
// provides these functions internally and the source file does not declare
// them. The generated CTest build must compile correctly via the
// force-included esbmc_verifier.h.

static int classify(int x, int threshold) {
  if (x > threshold) {
    return 1;
  } else if (x < -threshold) {
    return -1;
  }
  return 0;
}

int main() {
  int x         = __VERIFIER_nondet_int();
  int threshold = __VERIFIER_nondet_int();
  __VERIFIER_assume(threshold > 0);
  int r = classify(x, threshold);
  return 0;
}
