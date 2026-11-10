"""8 workers (PART 3.7; method §11: 8 was the sweet spot, more hits the same government servers).
Agency groups are split into N parts (biggest first, greedy by rows). Each part runs in its own thread, writes its own
results file (results-<i>.jsonl) and saves its state (state-<i>.json) every SAVE_EVERY rows, so a run that is stopped
(--max-minutes, exit 3) resumes with --resume. Built to run under kpc_shard too: AREAS from the environment and
KPC_SHARD_I picks the part number for the state file. The polite fetcher's per-host lock keeps every host at one request
per 2 s for the whole process, so 8 threads never hit one host more than one at a time (well under the 2-per-host rule)."""
import concurrent.futures as cf, json, os, pathlib, threading, time, traceback

SAVE_EVERY = 25


def areas_from_env(default):
    a = os.environ.get('AREAS')
    return [x.strip() for x in a.split(',') if x.strip()] if a else default


def split(groups, n):
    parts = [[] for _ in range(max(1, n))]; load = [0] * len(parts)
    for g in groups:
        i = load.index(min(load)); parts[i].append(g); load[i] += len(g[1])
    return [p for p in parts if p]


class State:
    def __init__(self, out_dir, part, resume):
        sh = os.environ.get('KPC_SHARD_I')
        self.p = pathlib.Path(out_dir) / f'state-{sh + "-" if sh else ""}{part}.json'
        self.done = set()
        if resume and self.p.exists():
            try: self.done = set(json.load(open(self.p)).get('done', []))
            except ValueError: pass
        self.n_new = 0

    def mark(self, key):
        self.done.add(key); self.n_new += 1
        if self.n_new % SAVE_EVERY == 0: self.save()

    def save(self):
        tmp = self.p.with_suffix('.tmp')
        json.dump({'done': sorted(self.done), 'saved': time.strftime('%Y-%m-%d %H:%M:%S')}, open(tmp, 'w'))
        os.replace(tmp, self.p)


def run(groups, fn, out_dir, tag, n=8, resume=False, deadline=None, log=None):
    """fn(agency, row, part) -> result dict or None. Returns (results, timed_out). Never raises for one bad row."""
    out_dir = pathlib.Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    parts = split([g for g in groups if g[1]], n)
    if not parts: return [], False
    results, lk, timed = [], threading.Lock(), threading.Event()

    def one(i, part):
        st = State(out_dir, f'{tag}-{i}', resume)
        rp = out_dir / f'results-{tag}-{i}.jsonl'
        mine = []
        if resume and rp.exists():
            for ln in open(rp, encoding='utf-8'):
                try: mine.append(json.loads(ln))
                except ValueError: pass
        with open(rp, 'a', encoding='utf-8') as f:
            for agency, rows in part:
                for row in rows:
                    key = f"{row['area']}|{row['ref']}"
                    if key in st.done: continue
                    if deadline and time.time() > deadline: timed.set(); st.save(); return mine
                    try:
                        res = fn(agency, row, i)
                    except Exception as ex:  # noqa: BLE001  never stop for one row
                        res = {'ref': row['ref'], 'area': row['area'], 'error': f'{type(ex).__name__}: {ex}'[:300],
                               'trace': traceback.format_exc()[-600:]}
                    if deadline and time.time() > deadline:   # Nov 10: this row ran into the time budget (its reads stopped): not kept, not marked done, redone on --resume
                        timed.set(); st.save(); return mine
                    if res is not None:
                        mine.append(res); f.write(json.dumps(res, ensure_ascii=False) + '\n'); f.flush()
                    st.mark(key)
        st.save()
        return mine

    with cf.ThreadPoolExecutor(len(parts)) as ex:
        for got in ex.map(lambda ip: one(*ip), enumerate(parts)):
            with lk: results.extend(got)
    return results, timed.is_set()
