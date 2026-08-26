import sys, time, json
sys.path.insert(0, '.')
import sweep as SW
from collections import Counter

ctxs = SW.load_contexts()
print('contexts:', len(ctxs), flush=True)
data = json.load(open('/Users/kuber.mehta/Personal-Projects/c5-k4/'
                      'data/wowii-conjectures.json'))
opens = [e for e in data if e['status'] == 'open']
t0 = time.time()
errs = []
statuses = Counter()
for k, e in enumerate(opens):
    eid = e['id']
    per = Counter()
    for gname, X in sorted(ctxs.items()):
        try:
            rds = SW.get_readings(eid, X)
        except Exception as ex:
            errs.append((eid, gname, 'BUILDER', repr(ex)[:90]))
            continue
        if rds is None:
            errs.append((eid, gname, 'NOBUILDER', ''))
            continue
        for rd in rds:
            try:
                st, det = SW.eval_reading_on(rd, X)
                per[st] += 1
            except Exception as ex:
                errs.append((eid, gname, rd['interp'][:40], repr(ex)[:90]))
    statuses.update(per)
    if (k + 1) % 40 == 0:
        print(f'{k+1}/{len(opens)} {time.time()-t0:.0f}s errs={len(errs)}',
              flush=True)
print('status totals:', dict(statuses))
print(f'total errors: {len(errs)}')
seen = set()
for eid, g, tag, ex in errs:
    key = (str(eid), tag, ex[:60])
    if key in seen:
        continue
    seen.add(key)
    print('ERR', eid, g, tag, ex)
