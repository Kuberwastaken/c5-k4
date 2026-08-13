#include <algorithm>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr char kUpstreamCommit[] =
    "7a38c469ec329d0c97c068e03c58834f61628e7e";
constexpr char kSourceBlob[] = "ce8251a228ea79a6b2f8414e9eb6b5291a640677";
constexpr char kContractSha256[] =
    "ab99508a9f5b924088897dbaf967c8f7125ae2380c5e061e7e9721c76a999403";

using Clock = std::chrono::steady_clock;

double seconds_since(const Clock::time_point start) {
  return std::chrono::duration<double>(Clock::now() - start).count();
}

std::uint64_t resident_kib() {
  std::ifstream status("/proc/self/status");
  std::string label;
  while (status >> label) {
    if (label == "VmRSS:") {
      std::uint64_t value = 0;
      std::string unit;
      status >> value >> unit;
      return value;
    }
    status.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
  }
  return 0;
}

void emit_prefix(const char* event, const int n) {
  std::cout << "{\"event\":\"" << event << "\",\"n\":" << n;
}

void flush_row() { std::cout << "}" << std::endl; }

std::uint64_t mix(std::uint64_t x) {
  x += 0x9e3779b97f4a7c15ULL;
  x = (x ^ (x >> 30U)) * 0xbf58476d1ce4e5b9ULL;
  x = (x ^ (x >> 27U)) * 0x94d049bb133111ebULL;
  return x ^ (x >> 31U);
}

class FlatMemo {
 public:
  explicit FlatMemo(const std::size_t initial_capacity) {
    if (!std::has_single_bit(initial_capacity)) {
      throw std::invalid_argument("memo capacity must be a power of two");
    }
    keys_.assign(initial_capacity, 0);
    values_.assign(initial_capacity, 0);
  }

  bool find(const std::uint64_t key, std::int8_t& value) const {
    const std::uint64_t stored = key + 1;
    std::size_t slot = mix(key) & (keys_.size() - 1);
    while (keys_[slot] != 0) {
      if (keys_[slot] == stored) {
        value = values_[slot];
        return true;
      }
      slot = (slot + 1) & (keys_.size() - 1);
    }
    return false;
  }

  bool insert(const std::uint64_t key, const std::int8_t value) {
    bool resized = false;
    if ((size_ + 1) * 10 > keys_.size() * 7) {
      rehash(keys_.size() * 2);
      resized = true;
    }
    insert_unchecked(key, value);
    return resized;
  }

  std::size_t size() const { return size_; }
  std::size_t capacity() const { return keys_.size(); }
  double load() const {
    return static_cast<double>(size_) / static_cast<double>(keys_.size());
  }

 private:
  void insert_unchecked(const std::uint64_t key, const std::int8_t value) {
    const std::uint64_t stored = key + 1;
    std::size_t slot = mix(key) & (keys_.size() - 1);
    while (keys_[slot] != 0) {
      if (keys_[slot] == stored) {
        values_[slot] = value;
        return;
      }
      slot = (slot + 1) & (keys_.size() - 1);
    }
    keys_[slot] = stored;
    values_[slot] = value;
    ++size_;
  }

  void rehash(const std::size_t capacity) {
    std::vector<std::uint64_t> old_keys;
    std::vector<std::int8_t> old_values;
    old_keys.swap(keys_);
    old_values.swap(values_);
    const std::size_t old_size = size_;
    keys_.assign(capacity, 0);
    values_.assign(capacity, 0);
    size_ = 0;
    for (std::size_t i = 0; i < old_keys.size(); ++i) {
      if (old_keys[i] != 0) {
        insert_unchecked(old_keys[i] - 1, old_values[i]);
      }
    }
    if (size_ != old_size) {
      throw std::logic_error("memo rehash lost entries");
    }
  }

  std::vector<std::uint64_t> keys_;
  std::vector<std::int8_t> values_;
  std::size_t size_ = 0;
};

std::size_t initial_capacity(const int n) {
  if (n <= 12) return std::size_t{1} << 12U;
  if (n <= 16) return std::size_t{1} << 19U;
  if (n <= 20) return std::size_t{1} << 24U;
  return std::size_t{1} << 26U;
}

class CatchUpSolver {
 public:
  explicit CatchUpSolver(const int n)
      : n_(n), full_mask_((std::uint32_t{1} << n) - 1),
        remaining_sum_(std::size_t{1} << n, 0), memo_(initial_capacity(n)) {
    if (n < 1 || n > 24) {
      throw std::invalid_argument("the exact solver supports 1 <= N <= 24");
    }
    for (std::uint32_t mask = 1; mask <= full_mask_; ++mask) {
      const unsigned bit = std::countr_zero(mask);
      remaining_sum_[mask] = static_cast<std::uint16_t>(
          remaining_sum_[mask & (mask - 1)] + bit + 1);
    }
  }

  int solve() {
    int best = -1;
    // Lean's Finset.Icc enumeration is semantically unordered, but Outcome.best
    // is order-independent. Ascending order is frozen for reproducible traces.
    for (int x = 1; x <= n_ && best < 1; ++x) {
      const std::uint32_t next = full_mask_ ^ (std::uint32_t{1} << (x - 1));
      best = std::max(best, -post_opening(next, x));
    }
    return best;
  }

  std::size_t memo_size() const { return memo_.size(); }
  std::size_t memo_capacity() const { return memo_.capacity(); }
  double memo_load() const { return memo_.load(); }
  std::uint64_t calls() const { return calls_; }

 private:
  int post_opening(const std::uint32_t mask, const int deficit) {
    ++calls_;
    if (mask == 0) return deficit == 0 ? 0 : -1;
    if (remaining_sum_[mask] < deficit) return -1;

    const std::uint64_t key = (static_cast<std::uint64_t>(mask) << 9U) |
                              static_cast<unsigned>(deficit);
    std::int8_t cached = 0;
    if (memo_.find(key, cached)) return cached;

    int best = -1;
    for (int x = 1; x <= n_ && best < 1; ++x) {
      const std::uint32_t bit = std::uint32_t{1} << (x - 1);
      if ((mask & bit) == 0) continue;
      const std::uint32_t next = mask ^ bit;
      const int value = x >= deficit
                            ? -post_opening(next, x - deficit)
                            : post_opening(next, deficit - x);
      best = std::max(best, value);
    }

    const bool resized = memo_.insert(key, static_cast<std::int8_t>(best));
    if (resized) emit_progress("memo_rehash");
    if (memo_.size() >= next_progress_) {
      emit_progress("memo_progress");
      next_progress_ += 1'000'000;
    }
    return best;
  }

  void emit_progress(const char* event) const {
    emit_prefix(event, n_);
    std::cout << ",\"memo_size\":" << memo_.size()
              << ",\"memo_capacity\":" << memo_.capacity()
              << ",\"memo_load\":" << std::setprecision(9) << memo_.load()
              << ",\"calls\":" << calls_
              << ",\"rss_kib\":" << resident_kib();
    flush_row();
  }

  int n_;
  std::uint32_t full_mask_;
  std::vector<std::uint16_t> remaining_sum_;
  FlatMemo memo_;
  std::uint64_t calls_ = 0;
  std::size_t next_progress_ = 1'000'000;
};

void emit_start(const char* mode, const int n) {
  emit_prefix("run_start", n);
  std::cout << ",\"mode\":\"" << mode << "\""
            << ",\"upstream_commit\":\"" << kUpstreamCommit << "\""
            << ",\"source_blob\":\"" << kSourceBlob << "\""
            << ",\"contract_sha256\":\"" << kContractSha256 << "\""
            << ",\"move_order\":\"ascending\""
            << ",\"state\":\"remaining_mask,current_deficit\""
            << ",\"rss_kib\":" << resident_kib();
  flush_row();
}

int run_one(const int n, const char* kind, const int expected) {
  emit_start(kind, n);
  const auto started = Clock::now();
  CatchUpSolver solver(n);
  const int value = solver.solve();
  emit_prefix("result", n);
  std::cout << ",\"kind\":\"" << kind << "\""
            << ",\"value\":" << value;
  if (expected >= -1) {
    std::cout << ",\"expected\":" << expected
              << ",\"matches_expected\":"
              << (value == expected ? "true" : "false");
  }
  std::cout << ",\"memo_size\":" << solver.memo_size()
            << ",\"memo_capacity\":" << solver.memo_capacity()
            << ",\"memo_load\":" << std::setprecision(9)
            << solver.memo_load() << ",\"calls\":" << solver.calls()
            << ",\"rss_kib\":" << resident_kib()
            << ",\"seconds\":" << std::setprecision(9)
            << seconds_since(started);
  flush_row();
  return expected >= -1 && value != expected ? 2 : 0;
}

void usage(const char* program) {
  std::cerr << "usage: " << program << " --calibrate | --n 23 | --n 24\n";
}

}  // namespace

int main(const int argc, char** argv) {
  try {
    if (argc == 2 && std::string(argv[1]) == "--calibrate") {
      constexpr int controls[] = {3, 4, 7, 8, 11, 12, 15, 16, 19, 20};
      for (const int n : controls) {
        const int result = run_one(n, "calibration", 0);
        if (result != 0) return result;
      }
      return 0;
    }
    if (argc == 3 && std::string(argv[1]) == "--n") {
      const int n = std::stoi(argv[2]);
      if (n != 23 && n != 24) {
        throw std::invalid_argument("development N must be 23 or 24");
      }
      return run_one(n, "development", -2);
    }
    usage(argv[0]);
    return 64;
  } catch (const std::bad_alloc&) {
    std::cout << "{\"event\":\"resource_failure\",\"kind\":\"bad_alloc\","
                 "\"rss_kib\":"
              << resident_kib() << "}" << std::endl;
    return 70;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 65;
  }
}
