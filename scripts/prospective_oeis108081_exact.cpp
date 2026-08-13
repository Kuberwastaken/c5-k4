#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <unordered_set>
#include <vector>

struct Word {
  std::array<int8_t, 14> x{};
  bool operator==(Word const& o) const noexcept { return x == o.x; }
};

struct WordHash {
  size_t operator()(Word const& w) const noexcept {
    uint64_t h = 1469598103934665603ULL;
    for (int8_t c : w.x) {
      h ^= static_cast<uint8_t>(c);
      h *= 1099511628211ULL;
    }
    return static_cast<size_t>(h);
  }
};

using Set = std::unordered_set<Word, WordHash>;

static uint64_t fib(unsigned n) {
  uint64_t a = 0, b = 1;
  while (n--) { uint64_t t = a + b; a = b; b = t; }
  return a;
}

static uint64_t choose(unsigned n, unsigned k) {
  if (k > n) return 0;
  if (k > n - k) k = n - k;
  uint64_t r = 1;
  for (unsigned i = 1; i <= k; ++i) r = r * (n - k + i) / i;
  return r;
}

// Literal OeisA108081.a, including truncated Nat subtraction.
static uint64_t expected(unsigned n) {
  uint64_t s = 0;
  for (unsigned k = 0; k <= n; ++k) {
    unsigned top = n + k == 0 ? 0 : n + k - 1;
    s += choose(top, k) * fib(n - k + 1);
  }
  return s;
}

int main() {
  auto t0 = std::chrono::steady_clock::now();
  std::vector<Set> X(15);
  X[1].insert(Word{});
  for (unsigned n = 1; n <= 14; ++n) {
    if (n > 1) {
      auto want = expected(n - 1);
      X[n].max_load_factor(0.80f);
      X[n].reserve(static_cast<size_t>(want));
      for (unsigned i = 1; i < n; ++i) {
        unsigned j = n - i;
        for (Word const& u : X[i]) for (Word const& v : X[j]) {
          Word left{};
          for (unsigned p = 0; p < i; ++p)
            left.x[p] = static_cast<int8_t>(u.x[i - 1 - p] - 1);
          for (unsigned p = 0; p < j; ++p) left.x[i + p] = v.x[p];
          X[n].insert(left);

          Word right{};
          for (unsigned p = 0; p < i; ++p) right.x[p] = u.x[p];
          for (unsigned p = 0; p < j; ++p)
            right.x[i + p] = static_cast<int8_t>(v.x[j - 1 - p] + 1);
          X[n].insert(right);
        }
      }
    }
    auto elapsed = std::chrono::duration<double>(
      std::chrono::steady_clock::now() - t0).count();
    uint64_t want = expected(n - 1);
    std::cout << "n=" << n << " count=" << X[n].size()
              << " expected=" << want
              << " equal=" << (X[n].size() == want ? "true" : "false")
              << " elapsed=" << elapsed << "\n";
    std::cout.flush();
    if (X[n].size() != want) return 2;
  }
  return 0;
}
