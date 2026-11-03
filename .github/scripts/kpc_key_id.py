#!/usr/bin/env python3
"""Nov 2 review (Mapping #7, copy bot key ids): a STABLE content fingerprint for each answer key, used by kpc-copy-from-links.yml.

Before: one sha1 over the raw bytes of all three keys (US + Canada + world) together. So a Canada change gave the US key a new
made-up build id too, and a rebuild that only moved a time stamp ('updated', 'made', 'seconds' ...) looked like a new build.
Now each key gets its own fingerprint, and time stamps / build stamps are left out, so the same key content = the same id.

  kpc_key_id.py one <KPC-Links dir> us-key|ca-key|world-key   -> 10 hex characters (the made-up id is US-f<these>)
  kpc_key_id.py all <KPC-Links dir>                           -> 16 hex characters over the three per-key fingerprints
Reads only the top-level *.json files of data/<key>/ (the same files as before). Never fails: an unreadable file counts by its bytes."""
import hashlib, json, os, sys

KEYS = ('us-key', 'ca-key', 'world-key')
# top-level keys that only say WHEN or WHICH RUN, not what the key holds
STAMPS = {'build', 'built', 'previous_build', 'previous_built', 'rebuilt', 'failed', 'complete', 'updated', 'updated_at',
          'made', 'date', 'generated', 'generated_at', 'checked', 'checked_at'}
ROW_STAMPS = {'seconds'}   # index.json: how long each state took to build


def norm_file(name, raw):
    try: d = json.loads(raw)
    except ValueError: return raw
    if isinstance(d, dict):
        d = {k: v for k, v in d.items() if k not in STAMPS}
        if name == 'index.json':
            for part in ('states', 'provinces', 'countries'):
                if isinstance(d.get(part), dict):
                    d[part] = {s: ({k: v for k, v in r.items() if k not in ROW_STAMPS} if isinstance(r, dict) else r) for s, r in d[part].items()}
    return json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def one(root, key):
    h = hashlib.sha1()
    d = os.path.join(root, 'data', key)
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, f)
        if not f.endswith('.json') or not os.path.isfile(p): continue
        with open(p, 'rb') as fh: raw = fh.read()
        h.update(f.encode() + b'\0' + norm_file(f, raw) + b'\0')
    return h.hexdigest()


def all_keys(root):
    return hashlib.sha1(' '.join(f'{k}:{one(root, k)}' for k in KEYS).encode()).hexdigest()


if __name__ == '__main__':
    mode, root = sys.argv[1], sys.argv[2]
    print(one(root, sys.argv[3])[:10] if mode == 'one' else all_keys(root)[:16])
