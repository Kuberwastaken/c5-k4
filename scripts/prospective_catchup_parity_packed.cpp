#include <algorithm>
#include <bit>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;

constexpr char kSchema[] = "catchup-parity-packed-v1";
constexpr char kUpstreamCommit[] =
    "6c0950bec7743f5098c0196c6aee7b22c1ec8005";
constexpr char kUpstreamTree[] =
    "5af0d2a3a319ee2458f8cd061db7c49aeba1b35e";
constexpr char kSourceBlob[] = "ce8251a228ea79a6b2f8414e9eb6b5291a640677";
constexpr char kSourceSha256[] =
    "7e940f2e37a1794e98fc21454096429da13243669a432b9239743aaf46f1d3c0";
constexpr char kActivationToken[] = "AUTHORIZE_FROZEN_CATCHUP_N24_V1";
constexpr std::uint64_t kExpectedN23States = 95'451'689ULL;
constexpr std::uint64_t kExpectedN23Calls = 826'741'149ULL;

enum class Value : std::int8_t { loss = -1, draw = 0, win = 1 };
enum class Code : std::uint32_t { unknown = 0, loss = 1, draw = 2, win = 3 };

class DeadlineExceeded final : public std::exception {
 public:
  const char* what() const noexcept override { return "internal deadline exceeded"; }
};

volatile std::sig_atomic_t g_termination_signal = 0;

void request_controlled_stop(const int signal) { g_termination_signal = signal; }

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

int integer_value(const Value value) { return static_cast<int>(value); }

Value negate(const Value value) {
  return static_cast<Value>(-integer_value(value));
}

Code encode(const Value value) {
  if (value == Value::loss) return Code::loss;
  if (value == Value::draw) return Code::draw;
  return Code::win;
}

Value decode(const Code code) {
  if (code == Code::loss) return Value::loss;
  if (code == Code::draw) return Value::draw;
  if (code == Code::win) return Value::win;
  throw std::logic_error("attempted to decode an unknown memo slot");
}

bool is_hex_commit(const std::string& text) {
  if (text.size() != 40) return false;
  return std::all_of(text.begin(), text.end(), [](const unsigned char c) {
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
  });
}

class PackedMemo {
 public:
  explicit PackedMemo(const int n)
      : words_(std::size_t{1} << static_cast<unsigned>(n), 0) {}

  bool find(const std::uint32_t mask, const int deficit, Value& value) const {
    const unsigned shift = 2U * (static_cast<unsigned>(deficit) >> 1U);
    const auto code = static_cast<Code>((words_[mask] >> shift) & 3U);
    if (code == Code::unknown) return false;
    value = decode(code);
    return true;
  }

  void insert(const std::uint32_t mask, const int deficit, const Value value) {
    const unsigned shift = 2U * (static_cast<unsigned>(deficit) >> 1U);
    const std::uint32_t old_code = (words_[mask] >> shift) & 3U;
    const std::uint32_t new_code = static_cast<std::uint32_t>(encode(value));
    if (old_code != 0U && old_code != new_code) {
      throw std::logic_error("memo value contradiction");
    }
    if (old_code == 0U) {
      words_[mask] |= new_code << shift;
      ++size_;
    }
  }

  std::uint64_t size() const { return size_; }
  std::uint64_t bytes() const {
    return static_cast<std::uint64_t>(words_.size()) * sizeof(std::uint32_t);
  }

 private:
  std::vector<std::uint32_t> words_;
  std::uint64_t size_ = 0;
};

struct EdgeRecord {
  int move = 0;
  bool swapped = false;
  std::uint32_t child_mask = 0;
  int child_deficit = 0;
  int child_sum = 0;
  Value child_value = Value::draw;
  Value move_value = Value::draw;
};

class CatchUpSolver {
 public:
  CatchUpSolver(const int n, const double deadline_seconds)
      : n_(n), full_mask_((std::uint32_t{1} << static_cast<unsigned>(n)) - 1U),
        total_sum_(n * (n + 1) / 2), memo_(n), started_(Clock::now()),
        deadline_seconds_(deadline_seconds) {
    if (n < 1 || n > 24) {
      throw std::invalid_argument("the packed solver supports 1 <= N <= 24");
    }
  }

  Value solve() {
    Value best = Value::loss;
    for (int x = 1; x <= n_ && best != Value::win; ++x) {
      const std::uint32_t next = full_mask_ ^ (std::uint32_t{1} << (x - 1));
      best = std::max(best, negate(post_opening(next, x, total_sum_ - x)));
    }
    result_ = best;
    solved_ = true;
    return best;
  }

  std::uint64_t memo_size() const { return memo_.size(); }
  std::uint64_t memo_bytes() const { return memo_.bytes(); }
  std::uint64_t calls() const { return calls_; }
  double elapsed() const { return seconds_since(started_); }

  void write_strategy_dag(const std::string& path,
                          const std::string& campaign_commit) const {
    if (!solved_ || result_ == Value::draw) {
      throw std::logic_error("strategy DAG is required only for a solved non-draw");
    }
    const std::filesystem::path final_path(path);
    std::filesystem::path partial_path(path + ".partial");
    std::error_code ignored;
    std::filesystem::remove(partial_path, ignored);
    std::ofstream out(partial_path, std::ios::out | std::ios::trunc);
    if (!out) throw std::runtime_error("cannot create partial strategy DAG");
    out << "{\"event\":\"certificate_start\",\"schema\":\""
        << kSchema << "-strategy-dag\",\"n\":" << n_
        << ",\"campaign_commit\":\"" << campaign_commit
        << "\",\"root_value\":" << integer_value(result_) << "}\n";

    std::unordered_set<std::uint64_t> emitted;
    std::vector<EdgeRecord> root_edges;
    for (int x = 1; x <= n_; ++x) {
      const std::uint32_t child_mask =
          full_mask_ ^ (std::uint32_t{1} << (x - 1));
      const int child_sum = total_sum_ - x;
      const Value child = recorded_value(child_mask, x, child_sum);
      const Value move_value = negate(child);
      if (result_ == Value::win && move_value != Value::win) continue;
      if (result_ == Value::loss && move_value != Value::loss) {
        throw std::logic_error("root loss certificate found a non-losing move");
      }
      root_edges.push_back({x, true, child_mask, x, child_sum, child,
                            move_value});
      emit_strategy_node(out, emitted, child_mask, x, child_sum, child);
      if (result_ == Value::win) break;
    }
    emit_root(out, root_edges);
    out << "{\"event\":\"certificate_end\",\"nodes\":" << emitted.size()
        << "}\n";
    out.flush();
    if (!out) throw std::runtime_error("failed while writing strategy DAG");
    out.close();
    try {
      std::filesystem::rename(partial_path, final_path);
    } catch (...) {
      std::filesystem::remove(partial_path, ignored);
      throw;
    }
  }

 private:
  void check_state(const std::uint32_t mask, const int deficit,
                   const int remaining_sum) const {
    if (deficit < 0 || deficit > n_) {
      throw std::logic_error("deficit bound invariant failed");
    }
    if (((deficit + remaining_sum) & 1) != (total_sum_ & 1)) {
      throw std::logic_error("deficit parity invariant failed");
    }
    if ((mask & ~full_mask_) != 0U) {
      throw std::logic_error("mask bound invariant failed");
    }
  }

  void check_deadline() const {
    if (g_termination_signal != 0) throw DeadlineExceeded();
    if (deadline_seconds_ > 0.0 && seconds_since(started_) >= deadline_seconds_) {
      throw DeadlineExceeded();
    }
  }

  Value post_opening(const std::uint32_t mask, const int deficit,
                     const int remaining_sum) {
    ++calls_;
    if ((calls_ & ((std::uint64_t{1} << 18U) - 1U)) == 0U) check_deadline();
    check_state(mask, deficit, remaining_sum);
    if (mask == 0U) return deficit == 0 ? Value::draw : Value::loss;
    if (remaining_sum < deficit) return Value::loss;

    Value cached = Value::draw;
    if (memo_.find(mask, deficit, cached)) return cached;

    Value best = Value::loss;
    std::uint32_t available = mask;
    while (available != 0U && best != Value::win) {
      const unsigned index = std::countr_zero(available);
      const std::uint32_t bit = std::uint32_t{1} << index;
      available ^= bit;
      const int x = static_cast<int>(index) + 1;
      const std::uint32_t next = mask ^ bit;
      const int next_sum = remaining_sum - x;
      const Value value = x >= deficit
                              ? negate(post_opening(next, x - deficit, next_sum))
                              : post_opening(next, deficit - x, next_sum);
      best = std::max(best, value);
    }

    memo_.insert(mask, deficit, best);
    if (memo_.size() >= next_progress_) {
      emit_progress("memo_progress");
      next_progress_ += 1'000'000ULL;
    }
    return best;
  }

  Value recorded_value(const std::uint32_t mask, const int deficit,
                       const int remaining_sum) const {
    check_state(mask, deficit, remaining_sum);
    if (mask == 0U) return deficit == 0 ? Value::draw : Value::loss;
    if (remaining_sum < deficit) return Value::loss;
    Value value = Value::draw;
    if (!memo_.find(mask, deficit, value)) {
      throw std::logic_error("strategy DAG requested an unexplored state");
    }
    return value;
  }

  std::vector<EdgeRecord> certificate_edges(const std::uint32_t mask,
                                             const int deficit,
                                             const int remaining_sum,
                                             const Value value) const {
    std::vector<EdgeRecord> edges;
    if (mask == 0U || remaining_sum < deficit) return edges;
    std::uint32_t available = mask;
    while (available != 0U) {
      const unsigned index = std::countr_zero(available);
      const std::uint32_t bit = std::uint32_t{1} << index;
      available ^= bit;
      const int x = static_cast<int>(index) + 1;
      const bool swapped = x >= deficit;
      const int next_deficit = swapped ? x - deficit : deficit - x;
      const std::uint32_t next_mask = mask ^ bit;
      const int next_sum = remaining_sum - x;
      const Value child = recorded_value(next_mask, next_deficit, next_sum);
      const Value move_value = swapped ? negate(child) : child;
      if (value == Value::win && move_value != Value::win) continue;
      if (value == Value::loss && move_value != Value::loss) {
        throw std::logic_error("loss certificate omitted a non-losing move");
      }
      edges.push_back({x, swapped, next_mask, next_deficit, next_sum, child,
                       move_value});
      if (value == Value::win) break;
    }
    if (edges.empty()) throw std::logic_error("nonterminal certificate has no edge");
    return edges;
  }

  static std::uint64_t state_key(const std::uint32_t mask, const int deficit) {
    return (static_cast<std::uint64_t>(mask) << 5U) |
           static_cast<unsigned>(deficit);
  }

  static void write_edges(std::ofstream& out,
                          const std::vector<EdgeRecord>& edges) {
    out << "[";
    for (std::size_t i = 0; i < edges.size(); ++i) {
      if (i != 0) out << ',';
      const auto& edge = edges[i];
      out << "{\"move\":" << edge.move
          << ",\"swapped\":" << (edge.swapped ? "true" : "false")
          << ",\"child_mask\":" << edge.child_mask
          << ",\"child_deficit\":" << edge.child_deficit
          << ",\"child_sum\":" << edge.child_sum
          << ",\"child_value\":" << integer_value(edge.child_value)
          << ",\"move_value\":" << integer_value(edge.move_value) << "}";
    }
    out << "]";
  }

  void emit_strategy_node(std::ofstream& out,
                          std::unordered_set<std::uint64_t>& emitted,
                          const std::uint32_t mask, const int deficit,
                          const int remaining_sum, const Value value) const {
    check_deadline();
    const std::uint64_t key = state_key(mask, deficit);
    if (!emitted.insert(key).second) return;
    const auto edges = certificate_edges(mask, deficit, remaining_sum, value);
    out << "{\"event\":\"node\",\"mask\":" << mask
        << ",\"deficit\":" << deficit << ",\"remaining_sum\":"
        << remaining_sum << ",\"value\":" << integer_value(value)
        << ",\"edges\":";
    write_edges(out, edges);
    out << "}\n";
    for (const auto& edge : edges) {
      emit_strategy_node(out, emitted, edge.child_mask, edge.child_deficit,
                         edge.child_sum, edge.child_value);
    }
  }

  void emit_root(std::ofstream& out, const std::vector<EdgeRecord>& edges) const {
    out << "{\"event\":\"root\",\"value\":" << integer_value(result_)
        << ",\"edges\":";
    write_edges(out, edges);
    out << "}\n";
  }

  void emit_progress(const char* event) const {
    emit_prefix(event, n_);
    std::cout << ",\"memo_states\":" << memo_.size()
              << ",\"memo_bytes\":" << memo_.bytes()
              << ",\"calls\":" << calls_ << ",\"rss_kib\":"
              << resident_kib() << ",\"seconds\":" << std::setprecision(9)
              << elapsed();
    flush_row();
  }

  int n_;
  std::uint32_t full_mask_;
  int total_sum_;
  PackedMemo memo_;
  Clock::time_point started_;
  double deadline_seconds_;
  std::uint64_t calls_ = 0;
  std::uint64_t next_progress_ = 1'000'000ULL;
  Value result_ = Value::draw;
  bool solved_ = false;
};

void emit_start(const char* mode, const int n, const double deadline_seconds,
                const std::string& campaign_commit) {
  emit_prefix("run_start", n);
  std::cout << ",\"schema\":\"" << kSchema << "\",\"mode\":\"" << mode
            << "\",\"upstream_commit\":\"" << kUpstreamCommit
            << "\",\"upstream_tree\":\"" << kUpstreamTree
            << "\",\"source_blob\":\"" << kSourceBlob
            << "\",\"source_sha256\":\"" << kSourceSha256
            << "\",\"campaign_commit\":\"" << campaign_commit
            << "\",\"move_order\":\"ascending_set_bits\""
            << ",\"state\":\"remaining_mask,current_deficit,remaining_sum\""
            << ",\"memo\":\"uint32_per_mask_two_bits_per_parity_slot\""
            << ",\"deadline_seconds\":" << deadline_seconds
            << ",\"rss_kib\":" << resident_kib();
  flush_row();
}

int run_one(const int n, const char* mode, const double deadline_seconds,
            const std::string& campaign_commit, const bool enforce_n23_counts,
            const std::string& certificate_path) {
  emit_start(mode, n, deadline_seconds, campaign_commit);
  CatchUpSolver solver(n, deadline_seconds);
  try {
    const Value value = solver.solve();
    if (deadline_seconds > 0.0 && solver.elapsed() > deadline_seconds) {
      throw DeadlineExceeded();
    }
    bool matches = true;
    if (enforce_n23_counts) {
      matches = value == Value::draw && solver.memo_size() == kExpectedN23States &&
                solver.calls() == kExpectedN23Calls && solver.elapsed() <= 38.0;
    }
    const bool certificate_mode = std::string(mode) == "n24_target" ||
                                  std::string(mode) == "small_certificate";
    const bool require_certificate = certificate_mode && value != Value::draw;
    if (require_certificate) {
      if (certificate_path.empty()) {
        throw std::logic_error("non-draw requires a strategy DAG path");
      }
      solver.write_strategy_dag(certificate_path, campaign_commit);
    }
    emit_prefix("result", n);
    std::cout << ",\"mode\":\"" << mode << "\",\"value\":"
              << integer_value(value) << ",\"value_name\":\""
              << (value == Value::loss ? "loss" : value == Value::draw ? "draw" : "win")
              << "\",\"memo_states\":" << solver.memo_size()
              << ",\"memo_bytes\":" << solver.memo_bytes()
              << ",\"calls\":" << solver.calls() << ",\"rss_kib\":"
              << resident_kib() << ",\"seconds\":" << std::setprecision(9)
              << solver.elapsed() << ",\"matches_frozen_gate\":"
              << (matches ? "true" : "false")
              << ",\"certificate_emitted\":"
              << (require_certificate ? "true" : "false");
    flush_row();
    return matches ? 0 : 3;
  } catch (const DeadlineExceeded&) {
    const bool signalled = g_termination_signal != 0;
    emit_prefix(signalled ? "controlled_signal" : "controlled_timeout", n);
    std::cout << ",\"mode\":\"" << mode << "\",\"memo_states\":"
              << solver.memo_size() << ",\"memo_bytes\":" << solver.memo_bytes()
              << ",\"calls\":" << solver.calls() << ",\"rss_kib\":"
              << resident_kib() << ",\"seconds\":" << std::setprecision(9)
              << solver.elapsed();
    if (signalled) std::cout << ",\"signal\":" << g_termination_signal;
    flush_row();
    return signalled ? 76 : 75;
  }
}

void usage(const char* program) {
  std::cerr << "usage: " << program
            << " --small N | --small-certificate N --certificate PATH"
               " | --source-controls | --n23-gate --campaign-commit SHA"
               " | --n24-target --campaign-commit SHA --activation-token TOKEN"
               " --certificate PATH\n";
}

std::string argument_after(const int argc, char** argv, const std::string& key) {
  for (int i = 1; i + 1 < argc; ++i) {
    if (argv[i] == key) return argv[i + 1];
  }
  return {};
}

bool has_argument(const int argc, char** argv, const std::string& key) {
  for (int i = 1; i < argc; ++i) {
    if (argv[i] == key) return true;
  }
  return false;
}

}  // namespace

int main(const int argc, char** argv) {
  try {
    std::signal(SIGTERM, request_controlled_stop);
    std::signal(SIGINT, request_controlled_stop);
    if (argc == 3 && std::string(argv[1]) == "--small") {
      const int n = std::stoi(argv[2]);
      if (n < 1 || n > 12) throw std::invalid_argument("small N must be 1..12");
      return run_one(n, "small_control", 0.0, "TARGET_FREE", false, "");
    }
    if (argc == 5 && std::string(argv[1]) == "--small-certificate" &&
        std::string(argv[3]) == "--certificate") {
      const int n = std::stoi(argv[2]);
      if (n < 1 || n > 12) {
        throw std::invalid_argument("small certificate N must be 1..12");
      }
      return run_one(n, "small_certificate", 0.0,
                     "0000000000000000000000000000000000000000", false,
                     argv[4]);
    }
    if (argc == 2 && std::string(argv[1]) == "--source-controls") {
      constexpr int controls[] = {3, 4, 7, 8, 11, 12, 15, 16, 19, 20};
      for (const int n : controls) {
        const int code = run_one(n, "source_control", 54.0, "TARGET_FREE", false, "");
        if (code != 0) return code;
      }
      return 0;
    }

    const std::string campaign = argument_after(argc, argv, "--campaign-commit");
    if (!is_hex_commit(campaign)) {
      throw std::invalid_argument("campaign commit must be exactly 40 lowercase hex characters");
    }
    if (has_argument(argc, argv, "--n23-gate")) {
      return run_one(23, "n23_performance_gate", 38.0, campaign, true, "");
    }
    if (has_argument(argc, argv, "--n24-target")) {
      const std::string token = argument_after(argc, argv, "--activation-token");
      const std::string certificate = argument_after(argc, argv, "--certificate");
      if (token != kActivationToken) {
        throw std::invalid_argument("N=24 target is mechanically disabled without the frozen activation token");
      }
      if (certificate.empty()) {
        throw std::invalid_argument("N=24 requires a strategy DAG output path");
      }
      return run_one(24, "n24_target", 54.0, campaign, false, certificate);
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
