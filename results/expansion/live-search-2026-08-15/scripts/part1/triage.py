import json, os, sys, re
BASE='/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad'
ids=sys.argv[1:]
for i in ids:
    lean=open(os.path.join(BASE,'lean',i+'.lean')).read()
    # strip license header
    idx=lean.find('/-!')
    body=lean[idx:] if idx>=0 else lean
    print('='*90)
    print('### A%06d  (FormalConjectures/OEIS/%s.lean)'%(int(i),i))
    print('='*90)
    print('--- LEAN ---')
    print(body.strip())
    p=os.path.join(BASE,'oeis',i+'.json')
    if os.path.exists(p):
        try:
            d=json.load(open(p))
        except Exception as e:
            print('OEIS JSON parse fail',e); continue
        if not d: print('OEIS: empty'); continue
        e=d[0]
        print('--- OEIS ---')
        print('NAME:', e.get('name'))
        print('OFFSET:', e.get('offset'))
        print('DATA:', e.get('data'))
        for k in ('formula','comment','example','maple','mathematica','program','xref','keyword'):
            v=e.get(k)
            if not v: continue
            if k in ('program','maple','mathematica'): 
                continue
            if isinstance(v,list):
                print(k.upper()+':')
                for line in v[:14]: print('   ',line)
            else:
                print(k.upper()+':',v)
    else:
        print('OEIS: NO CACHE')
    print()
