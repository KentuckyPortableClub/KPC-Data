"""Two passes (PART 3.6, method §11). PASS 1 on every gap; PASS 2 only on the NOT FOUND + weak rows, with every finding
learned in pass 1 (findings.jsonl re-read first). Each result records which pass solved it."""
import time
from . import workers

WEAK = ('weak',)


def needs_pass2(r):
    if r.get('error'): return True
    if r.get('status') in ('not found', 'weak'): return True
    return (r.get('confidence') or {}).get('level') == 'weak' and r.get('status') != 'blocked'


def two_passes(engine, plugin, groups):
    res1, timed = workers.run(groups, lambda ag, row, i: _tag(plugin.work_row(ag, row, engine, 1), 1), engine.out / 'work' / plugin.KIND,
                              f'p1', n=engine.n_workers, resume=engine.resume, deadline=engine.deadline)
    if timed: return res1, {'pass1': _count(res1), 'pass2': None, 'timed_out': True}
    engine.findings.refresh()
    again = {(r['area'], r['ref']) for r in res1 if needs_pass2(r)}
    g2 = [(ag, [row for row in rows if (row['area'], row['ref']) in again]) for ag, rows in groups]
    g2 = [g for g in g2 if g[1]]
    res2, timed = workers.run(g2, lambda ag, row, i: _tag(plugin.work_row(ag, row, engine, 2), 2), engine.out / 'work' / plugin.KIND,
                              f'p2', n=engine.n_workers, resume=engine.resume, deadline=engine.deadline)
    by = {(r['area'], r['ref']): r for r in res1}
    solved2 = 0
    for r in res2:
        k = (r['area'], r['ref'])
        old = by.get(k)
        if _better(r, old):
            if old and old.get('status') != 'found' and r.get('status') == 'found': solved2 += 1
            by[k] = r
    final = list(by.values())
    return final, {'pass1': _count(res1), 'pass2': _count(res2), 'pass2_solved': solved2, 'timed_out': timed}


RANK = {'found': 3, 'candidate': 2, 'weak': 1, 'not found': 0, 'blocked': 0}


def _better(a, b):
    if not b: return True
    return RANK.get(a.get('status'), 0) > RANK.get(b.get('status'), 0)


def _tag(r, n):
    if r is not None: r['pass'] = n
    return r


def _count(rs):
    c = {}
    for r in rs: c[r.get('status', 'error' if r.get('error') else '?')] = c.get(r.get('status', 'error' if r.get('error') else '?'), 0) + 1
    return c
