fix=[]
for d in range(1,80):
    for s in range(1, 9*d+1):
        v=d**s
        ds=str(v)
        if len(ds)==d and sum(int(ch) for ch in ds)==s: fix.append(v)
print("all n>0 with (#digits n)^(digitsum n) == n, up to 79 digits:", sorted(set(fix)))
