import numpy as np, time
t0=time.time()
LIM=5_000_000
sig=np.load('sig.npy')
idx=np.arange(LIM+1)
dev=np.abs(sig[:LIM+1]-2*idx)
mask=(idx>0)&(dev<=10)
mem=idx[mask]
print("count of A108864 members <= %d:"%LIM, len(mem))
print("first 62 (0-indexed a(0..61)):", mem[:62].tolist())
odd=[int(v) for v in mem.tolist() if v%2==1]
print("ODD members:", odd)
print("index (0-based) of each odd member:", [int(np.searchsorted(mem,v)) for v in odd])
