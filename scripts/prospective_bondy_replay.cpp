// Independent endpoint-DP replay for the frozen Bondy k=4 arm.
// For every subset S, p[S] is the minimum nonempty path-cover count, capped
// at five. d[S,v] is the same minimum with v an endpoint of a distinguished
// path. This implementation shares no discovery code.

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr int N = 20;
constexpr int K = 4;
constexpr uint32_t SIZE = 1U << N;
constexpr int INTERNAL_SECONDS = 54;

std::vector<std::pair<int,int>> read_edges(const std::string& path) {
  std::ifstream in(path); if(!in) throw std::runtime_error("cannot open edge file");
  std::vector<std::pair<int,int>> edges;
  std::string line;
  size_t line_number=0;
  while(std::getline(in,line)) {
    ++line_number;
    std::istringstream row(line);
    int u,v;
    std::string trailing;
    if(!(row>>u>>v) || (row>>trailing))
      throw std::runtime_error("malformed edge line " + std::to_string(line_number));
    if(!(0<=u&&u<v&&v<N)) throw std::runtime_error("noncanonical edge");
    edges.push_back({u,v});
  }
  if(in.bad()) throw std::runtime_error("edge file read failure");
  if(edges.size()!=40) throw std::runtime_error("expected 40 peripheral edges");
  if(!std::is_sorted(edges.begin(),edges.end()) || std::adjacent_find(edges.begin(),edges.end())!=edges.end())
    throw std::runtime_error("edge order/duplicate drift");
  return edges;
}

int popcount(uint32_t value) { return __builtin_popcount(value); }
}

int main(int argc,char**argv) {
  try {
    if(argc!=3) throw std::runtime_error("usage: prospective_bondy_replay EDGE_FILE PC_TABLE_FILE");
    const auto edges=read_edges(argv[1]);
    std::array<uint32_t,N> adj{};
    for(auto [u,v]:edges) { adj[u]|=1U<<v; adj[v]|=1U<<u; }
    std::vector<uint8_t> pc(SIZE,5);
    std::vector<uint8_t> endpoint(static_cast<size_t>(SIZE)*N,5);
    pc[0]=0;
    const auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(INTERNAL_SECONDS);
    for(uint32_t mask=1;mask<SIZE;++mask) {
      if((mask&0x1fffU)==0 && std::chrono::steady_clock::now()>=deadline)
        throw std::runtime_error("independent endpoint DP deadline");
      uint32_t vertices=mask;
      uint8_t best_pc=5;
      while(vertices) {
        const uint32_t bit=vertices&(~vertices+1U);
        const int v=__builtin_ctz(bit);
        const uint32_t previous=mask^bit;
        uint8_t best=std::min<uint8_t>(5,static_cast<uint8_t>(pc[previous]+1));
        uint32_t neighbors=previous&adj[v];
        while(neighbors) {
          const uint32_t ubit=neighbors&(~neighbors+1U);
          const int u=__builtin_ctz(ubit);
          best=std::min(best,endpoint[static_cast<size_t>(previous)*N+u]);
          neighbors^=ubit;
        }
        endpoint[static_cast<size_t>(mask)*N+v]=best;
        best_pc=std::min(best_pc,best);
        vertices^=bit;
      }
      pc[mask]=best_pc;
    }
    uint64_t deletion_sets=0;
    const uint32_t all=SIZE-1;
    for(uint32_t removed=0;removed<SIZE;++removed) {
      if(popcount(removed)>=K) continue;
      ++deletion_sets;
      if(pc[all^removed]<=K) {
        std::cout << "{\"status\":\"REJECT_UPPER_BOUND\",\"removed_mask\":" << removed
                  << ",\"pc\":" << static_cast<int>(pc[all^removed])
                  << ",\"deletion_sets\":" << deletion_sets << "}\n";
        return 2;
      }
    }
    std::ofstream table(argv[2],std::ios::binary|std::ios::trunc);
    if(!table) throw std::runtime_error("cannot create pc table");
    table.write(reinterpret_cast<const char*>(pc.data()),static_cast<std::streamsize>(pc.size()));
    table.close(); if(!table) throw std::runtime_error("pc table write failed");
    std::cout << "{\"status\":\"Q4_UPPER_BOUND_VERIFIED\",\"deletion_sets\":" << deletion_sets
              << ",\"pc_table_bytes\":" << pc.size() << "}\n";
    return 0;
  } catch(const std::exception& e) {
    std::cout << "{\"status\":\"GATE_FAIL\",\"error\":\"" << e.what() << "\"}\n";
    return 3;
  }
}
