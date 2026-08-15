def b3(x):
    ds=[]
    while x: ds.append(x%3); x//=3
    return ds
bad=[]
N=3000
for n in range(0,N+1):
    if 0 not in b3(2**n): bad.append(n)
print("n<=%d with no 0 digit in base-3 rep of 2^n:"%N, bad)
print("violations of Sloane 'a(n)>0 for n>15':", [n for n in bad if n>15])
