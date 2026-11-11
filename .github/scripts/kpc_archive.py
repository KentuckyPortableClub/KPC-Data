#!/usr/bin/env python3
"""KPC-Archive reader fallback (Nov 7 2026, archive split). Standard library only.

Bulk files that the live site and the bots do not read every day move from KPC-Data to KentuckyPortableClub/KPC-Archive
(same paths; kpc_archive_move.py). The move leaves one list behind in KPC-Data: data/archive-manifest.json
  {"files": [{"path", "sha256", "bytes", "source_commit"}, ...]}.
A reader that wants a moved file calls
    KA.fetch(rel, DATA)        -> bytes, or None  (None = skip cleanly: not archived, switched off, offline, or the bytes do not match)
    KA.listing(prefix, DATA)   -> the archived paths under a folder prefix (from the manifest only; no network)
The network is used ONLY for a path the manifest lists, so before the first move (no manifest) every call returns None at once and
no reader changes behaviour. KPC_ARCHIVE_FETCH=off turns the fetch off. Every download is checked against the manifest's sha256.
Never raises."""
import hashlib, json, os, pathlib, urllib.request
import kpc_host_rules; kpc_host_rules.install()

REPO = 'KentuckyPortableClub/KPC-Archive'
RAW = f'https://raw.githubusercontent.com/{REPO}/main/'
MANIFEST = 'data/archive-manifest.json'
_cache = {}


def url(rel):
    return RAW + str(rel).lstrip('/')


def manifest(data_root='.'):
    """{path: {'sha256', 'bytes', 'source_commit'}} from <data_root>/data/archive-manifest.json ({} when there is none)."""
    p = pathlib.Path(data_root) / MANIFEST
    try:
        st = p.stat()
        key = (str(p), st.st_mtime_ns, st.st_size)
        if key not in _cache:
            doc = json.loads(p.read_text(encoding='utf-8'))
            _cache.clear()
            _cache[key] = {r['path']: r for r in doc.get('files') or [] if isinstance(r, dict) and r.get('path')}
        return _cache[key]
    except Exception:  # noqa: BLE001
        return {}


def is_archived(rel, data_root='.'):
    return str(rel).replace('\\', '/') in manifest(data_root)


def listing(prefix, data_root='.'):
    pre = str(prefix).replace('\\', '/')
    return sorted(p for p in manifest(data_root) if p.startswith(pre))


def _get(u, timeout):          # one place to stub in tests
    req = urllib.request.Request(u, headers={'User-Agent': 'KPC-archive-reader (github.com/KentuckyPortableClub)'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def fetch(rel, data_root='.', timeout=30):
    rel = str(rel).replace('\\', '/')
    row = manifest(data_root).get(rel)
    if not row or os.environ.get('KPC_ARCHIVE_FETCH', 'on').lower() == 'off':
        return None
    try:
        raw = _get(url(rel), timeout)
    except Exception as e:  # noqa: BLE001
        print(f'::notice title=KPC-Archive::{rel} is archived but could not be fetched ({type(e).__name__}); skipped')
        return None
    if hashlib.sha256(raw).hexdigest() != row.get('sha256'):
        print(f'::notice title=KPC-Archive::{rel} downloaded but its sha256 does not match the manifest; skipped')
        return None
    return raw
