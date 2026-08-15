import urllib.request
req=urllib.request.Request("https://oeis.org/A000796/b000796.txt", headers={'User-Agent':'Mozilla/5.0 Chrome/120.0'})
ds=[int(l.split()[1]) for l in urllib.request.urlopen(req,timeout=30).read().decode().splitlines() if l.strip() and not l.startswith('#')]
s=''.join(map(str,ds))
best=0;bi=0;cur=0
for i,ch in enumerate(s):
    cur = cur+1 if ch=='9' else 0
    if cur>best: best=cur; bi=i-cur+1
print("digits available:",len(s))
print("longest run of 9s in first %d digits: length %d starting at digit index %d (1-indexed position %d)"%(len(s),best,bi,bi+1))
# conjecture2 needs run of ~n nines starting just after position n+1 -> n <= best and start index n+1
hits=[n for n in range(1,len(s)//2) if all(c=='9' for c in s[n+1:n+1+n])]
print("n with d_{n+2}..d_{2n+1} all 9 (necessary condition for conjecture2 failure):", hits[:10])
