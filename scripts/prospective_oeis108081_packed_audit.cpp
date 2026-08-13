#include <chrono>
#include <cstdint>
#include <iostream>
#include <unordered_set>
#include <vector>

using U128 = unsigned __int128;
struct H {
  size_t operator()(U128 x) const noexcept {
    uint64_t lo = static_cast<uint64_t>(x);
    uint64_t hi = static_cast<uint64_t>(x >> 64);
    lo ^= hi + 0x9e3779b97f4a7c15ULL + (lo << 6) + (lo >> 2);
    lo ^= lo >> 30; lo *= 0xbf58476d1ce4e5b9ULL;
    lo ^= lo >> 27; lo *= 0x94d049bb133111ebULL;
    return static_cast<size_t>(lo ^ (lo >> 31));
  }
};
using Set = std::unordered_set<U128, H>;

static int get(U128 w, unsigned p) {
  return static_cast<int>((w >> (5 * p)) & 31) - 16;
}
static void put(U128& w, unsigned p, int v) {
  w |= static_cast<U128>(v + 16) << (5 * p);
}

int main() {
  const uint64_t expected[] = {0,1,2,7,25,92,344,1300,4950,18955,72905,
    281403,1089343,4227273,16438345};
  std::vector<Set> x(15);
  U128 z = 0; put(z, 0, 0); x[1].insert(z);
  auto t0 = std::chrono::steady_clock::now();
  for (unsigned n = 2; n <= 14; ++n) {
    x[n].max_load_factor(0.8f); x[n].reserve(expected[n]);
    for (unsigned i = 1; i < n; ++i) {
      unsigned j = n - i;
      for (U128 u : x[i]) for (U128 v : x[j]) {
        U128 left = 0, right = 0;
        for (unsigned p = 0; p < i; ++p) put(left, p, get(u, i-1-p)-1);
        for (unsigned p = 0; p < j; ++p) put(left, i+p, get(v,p));
        for (unsigned p = 0; p < i; ++p) put(right, p, get(u,p));
        for (unsigned p = 0; p < j; ++p) put(right, i+p, get(v,j-1-p)+1);
        x[n].insert(left); x[n].insert(right);
      }
    }
    double s = std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
    std::cout << "n=" << n << " count=" << x[n].size()
              << " expected=" << expected[n]
              << " equal=" << (x[n].size()==expected[n] ? "true":"false")
              << " elapsed=" << s << "\n";
    std::cout.flush();
    if (x[n].size()!=expected[n]) return 2;
  }
}
