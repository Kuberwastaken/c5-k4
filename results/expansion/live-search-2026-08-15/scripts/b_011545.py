import time, urllib.request, math
# pull the b-file for pi digits (A011545) -> use A000796 digits of pi instead
url="https://oeis.org/A000796/b000796.txt"
req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'})
txt=urllib.request.urlopen(req, timeout=30).read().decode()
ds=[]
for line in txt.splitlines():
    line=line.strip()
    if not line or line.startswith('#'): continue
    p=line.split()
    ds.append(int(p[1]))
print("digits of pi available:",len(ds), "first 12:",ds[:12])
t0=time.time(); bad=[]
v=0
for i,d in enumerate(ds):
    v=v*10+d
    r=math.isqrt(v)
    if r*r==v: bad.append((i,v))
    if time.time()-t0>40: break
print("checked a(n) for n=0..%d"%i)
print("perfect squares among truncations of pi:", bad)
