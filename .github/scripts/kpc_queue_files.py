#!/usr/bin/env python3
"""QUEUE FILES (KPC owner, 2026-11-12): the one small place where bots add rows to the layer-intake queue.

data/intake/queue.json is at the 1 MB file cap. KPC-Data #76 taught the intake bot to read every data/intake/queue*.json except a
*hold* file (any case), so new rows go in split files. This module is the writer side of that rule, so each bot does not invent its own:

  - a bot appends to ITS OWN split file, data/intake/queue-<bot>-<n>.json (one writer per file, so two bots never overwrite each
    other's rows when a save copies the file whole); same shape as queue-nov12.json: {"about": ..., "rows": [...]}
  - the file rolls to the next number before ROLL_AT bytes (900,000: headroom under the 1,048,576 cap); a file is never written
    at or over the cap
  - never the full queue.json, never a *hold* file (a bot name that contains "hold" is refused)
  - writes are atomic: a temp file in the same folder, then os.replace
  - known_keys() / index() look across EVERY queue*.json, hold files included: a row that is held (hand-download / saved-copy-only) means
    "do not add this url as a probe-able lead", so a writer that finds its url there adds nothing
  - rows(): every row the intake bot reads (queue.json + split files, never a hold file), in the bot's order
  - save_in_place(): a row that already exists is updated in the file it came from; a hold file is never rewritten, and a file
    that would reach the cap is left as it is (the caller is told False)
No network, no rules, no pins. Offline test: tests/test_queue_writers_nov12.py."""
import json, os, pathlib, re

DIR = pathlib.Path('data/intake')
FILE_CAP = 1_048_576      # the repo's 1 MB per-file cap
ROLL_AT = 900_000         # a split file is not grown past this many bytes (headroom under the cap)
MAIN = 'queue.json'


def is_hold(p):
    return 'hold' in pathlib.Path(p).name.lower()       # the intake bot's rule: hold / HOLD / Hold anywhere in the name


def paths(folder=None, hold=False):
    """Every queue*.json in the folder, sorted (the intake bot's own glob). hold=True adds the *hold* files."""
    folder = pathlib.Path(folder or DIR)
    return [f for f in sorted(folder.glob('queue*.json')) if hold or not is_hold(f)]


def _load(p):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None


def rows(folder=None, hold=False):
    """Row dicts in reader order: queue.json first, then the split files. hold=True also yields the hold files' rows."""
    folder = pathlib.Path(folder or DIR)
    fs = paths(folder, hold)
    fs.sort(key=lambda f: (f.name != MAIN, f.name))
    out = []
    for f in fs:
        d = _load(f)
        out += [r for r in ((d or {}).get('rows') or []) if isinstance(r, dict)] if isinstance(d, dict) else []
    return out


def known_keys(folder=None, key=None):
    """{key(url)} over EVERY queue file, hold files included (a held url must not be queued again)."""
    key = key or (lambda u: u)
    return {key(r.get('url')) for r in rows(folder, hold=True) if r.get('url')}


def index(folder=None, key=None):
    """{key(url): (path, doc, row)} over every queue*.json, hold files included (so the caller can tell a held row). Each file is read once;
    the first file in reader order wins. A row changed in place belongs to its doc: save_in_place(path, doc) puts it back."""
    key = key or (lambda u: u)
    folder = pathlib.Path(folder or DIR)
    out = {}
    for f in sorted(paths(folder, hold=True), key=lambda f: (f.name != MAIN, f.name)):
        d = _load(f)
        for r in ((d or {}).get('rows') or []) if isinstance(d, dict) else []:
            if isinstance(r, dict) and r.get('url'): out.setdefault(key(r['url']), (f, d, r))
    return out


def dumps(doc, newline=True):
    return json.dumps(doc, indent=1, ensure_ascii=False) + ('\n' if newline else '')


def write_atomic(path, text):
    """Temp file beside the target (dot name, .tmp: never matches queue*.json), then os.replace. Refuses a file at the cap."""
    path = pathlib.Path(path)
    data = text.encode('utf-8')
    if len(data) >= FILE_CAP: raise ValueError(f'{path.name}: {len(data)} bytes would reach the 1 MB cap')
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    try:
        with open(tmp, 'wb') as fh:
            fh.write(data); fh.flush(); os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists(): tmp.unlink()


def save_in_place(path, doc):
    """Rewrite an existing row's file after a change (the update goes back to the file it came from). False = left alone:
    a hold file is never written, and a file that would reach the cap is not grown."""
    path = pathlib.Path(path)
    if is_hold(path): return False
    text = dumps(doc, True)
    try:   # keep the file's own style (the intake bot saves queue.json with sorted keys and a final newline; older copies have neither)
        old = path.read_text(encoding='utf-8'); od = json.loads(old)
        for sk in (False, True):
            for nl in (False, True):
                if json.dumps(od, indent=1, ensure_ascii=False, sort_keys=sk) + ('\n' if nl else '') == old:
                    text = json.dumps(doc, indent=1, ensure_ascii=False, sort_keys=sk) + ('\n' if nl else '')
    except (OSError, ValueError): pass
    if len(text.encode('utf-8')) >= FILE_CAP: return False
    write_atomic(path, text)
    return True


def _name(bot):
    b = re.sub(r'[^a-z0-9-]+', '-', str(bot).lower()).strip('-')
    if not b or 'hold' in b: raise ValueError(f'not a usable queue writer name: {bot!r}')
    return b


def _row_cost(r):
    s = json.dumps(r, indent=1, ensure_ascii=False)
    return len(s.encode('utf-8')) + 2 * s.count('\n') + 4     # two levels of indent on every line, the comma and the newline


def append_rows(new_rows, bot, folder=None, about=None):
    """Append rows to this bot's split file data/intake/queue-<bot>-<n>.json, rolling to the next number before ROLL_AT bytes.
    Returns the list of paths written (empty when there is nothing to add). Dedupe is the caller's job (known_keys)."""
    folder = pathlib.Path(folder or DIR)
    name = _name(bot)
    new_rows = [r for r in new_rows if isinstance(r, dict)]
    if not new_rows: return []
    rx = re.compile(rf'^queue-{re.escape(name)}-(\d+)\.json$')
    have = sorted((int(m.group(1)), f) for f in folder.glob('queue-*.json') if (m := rx.match(f.name)))
    n, doc = 1, None
    if have:
        n, f = have[-1]
        d = _load(f)
        if isinstance(d, dict) and isinstance(d.get('rows'), list) and f.stat().st_size < ROLL_AT: doc = d
        else: n += 1                                   # unreadable or full: never overwrite, start the next file
    written = []
    def start(k):
        return {'about': about or f'SPLIT QUEUE (KPC owner, 2026-11-12): queue.json is at the 1 MB file cap, so {name} adds its leads here. '
                                  'Same row shape as queue.json. Only this bot appends to this file. kpc_intake_bot.py reads every '
                                  'data/intake/queue*.json except a *hold* file.', 'rows': []}
    doc = doc or start(n)
    size = len(dumps(doc).encode('utf-8'))
    pending = []
    for r in new_rows:
        c = _row_cost(r)
        if c + 2000 >= ROLL_AT: raise ValueError('one queue row is too large for a queue file')
        if pending and size + c > ROLL_AT - 2000:      # roll: write what fits, start the next number
            doc['rows'] += pending; _put(folder, name, n, doc, written); pending = []
            n += 1; doc = start(n); size = len(dumps(doc).encode('utf-8'))
        pending.append(r); size += c
    doc['rows'] += pending; _put(folder, name, n, doc, written)
    return written


def _put(folder, name, n, doc, written):
    p = folder / f'queue-{name}-{n}.json'
    text = dumps(doc)
    if len(text.encode('utf-8')) > ROLL_AT: raise ValueError(f'{p.name}: {len(text.encode())} bytes is over the roll size {ROLL_AT}')
    write_atomic(p, text); written.append(p)
