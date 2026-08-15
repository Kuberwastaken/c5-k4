import os, sys, re, json
BASE='/tmp/claude-1000/-Users-kuber-mehta-Projects-scratch/21f73cfa-6e97-457f-8bb8-ae31d911cc43/scratchpad'
for i in sys.argv[1:]:
    lean=open(os.path.join(BASE,'lean',i+'.lean')).read()
    lines=lean.split('\n')
    out=[]
    # print title block
    ti=lean.find('/-!'); tj=lean.find('-/',ti)
    title=lean[ti:tj+2] if ti>=0 else ''
    # find defs
    defs=[]
    for m in re.finditer(r'^(noncomputable )?(def|abbrev|local notation|notation) .*$', lean, re.M):
        defs.append(m.group(0))
    # capture full def bodies: from 'def ' to next blank-line-then-nonindented
    blocks=re.split(r'\n(?=@\[category|/--|def |noncomputable def |abbrev )', lean)
    print('='*80)
    print('### A%06d  OEIS/%s.lean'%(int(i),i))
    print(title.strip()[:600])
    for b in blocks:
        if b.lstrip().startswith('def ') or b.lstrip().startswith('noncomputable def ') or b.lstrip().startswith('abbrev '):
            print('--DEF--'); print(b.rstrip())
        if 'category research open' in b or 'answer(sorry)' in b:
            print('--OPEN--'); print(b.rstrip())
    print()
