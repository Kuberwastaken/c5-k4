import sys, time, array
N = int(sys.argv[1]) if len(sys.argv) > 1 else 50_000_000
t0 = time.time()
tau = array.array('i', [0])*1
tau = array.array('i', bytes(4*N))
for d in range(1, N):
    for m in range(d, N, d):
        tau[m] += 1
cur_max = -1
sols = []
for n in range(1, N):
    v = (n-1) + tau[n-1]
    if v > cur_max: cur_max = v
    if n > 24 and cur_max <= n+2:
        sols.append(n)
print("SOLUTIONS>24:", sols[:20], "count:", len(sols), f"elapsed {time.time()-t0:.1f}s")
