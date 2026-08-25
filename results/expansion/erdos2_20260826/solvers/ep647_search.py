import sys, time
from sympy import divisor_count

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
t0 = time.time()

def tau(m):
    return divisor_count(m)

# M[n] = max_{0<=m<n} (m + tau(m)); condition for n: M[n] <= n + 2
sols = []
maxv = 0
tau_prev = {}
# rolling: maintain current max of m+tau(m) over m<n
cur_max = -1
n = 1
while n <= N:
    # add m = n-1 into window (window is m < n)
    m = n - 1
    t = tau(m)
    v = m + t
    if v > cur_max:
        cur_max = v
    if n > 24 and cur_max <= n + 2:
        sols.append(n)
        print("SOLUTION n =", n, flush=True)
    n += 1
print(f"searched n=1..{N}; solutions >24: {sols if len(sols)<50 else str(len(sols))+' many'}; elapsed {time.time()-t0:.1f}s")
