import sys, time
sys.set_int_max_str_digits(2000000)
t0=time.time(); found=[]
b=2
while time.time()-t0<100:
    if '0' not in str(b**40): found.append(b)
    b+=1
print("A103662 a_40: bases scanned 2..%d ; zeroless b^40 found: %s"%(b-1,found))
# sanity: reproduce a(n) for small n
def sm(n):
    b=2
    while b<2000000:
        if '0' not in str(b**n): return b**n
        b+=1
    return None
print("a(0..9) recomputed:",[sm(n) if n>0 else 1 for n in range(10)])
print("OEIS head        : [1,2,4,8,16,32,64,128,256,512]")
print("a(10),a(11),a(12):",sm(10),sm(11),sm(12))
print("OEIS             : 9765625 177147 531441")
