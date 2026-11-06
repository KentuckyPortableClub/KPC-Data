#!/usr/bin/env python3
"""Read JSON / JSONL from a path or that path plus '.gz', preferring .gz when it is on disk.

One helper for the storage files (waiting-room questions, verdicts.jsonl, external-results.json,
ready.json). A plain file is still read when no .gz sibling exists, so a checkout that has not
been compressed keeps working. Writers of those files use save_json_gz / append_jsonl_gz /
save_text_gz and drop the plain copy.
"""
import glob, gzip, json, pathlib


def _pair(path):
    """(plain path, gz path) for a logical path or a path that already ends in .gz."""
    p = pathlib.Path(path)
    s = str(p)
    if s.endswith('.gz'):
        return pathlib.Path(s[:-3]), p
    return p, pathlib.Path(s + '.gz')


def resolve_any(path):
    """The file to open: path+'.gz' when it exists, otherwise path. A path that already ends
    in .gz is used as-is when that file exists."""
    plain, gz = _pair(path)
    if gz.is_file():
        return gz
    return plain


def load_json_any(path):
    """JSON object from path or path+'.gz'. .gz wins when both exist."""
    p = resolve_any(path)
    if str(p).endswith('.gz'):
        with gzip.open(p, 'rt', encoding='utf-8') as fh:
            return json.load(fh)
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


def iter_jsonl_any(path):
    """JSON objects, one per line, from path or path+'.gz'. Blank and broken lines are skipped.
    Missing file yields nothing."""
    p = resolve_any(path)
    if not p.is_file():
        return
    opener = gzip.open if str(p).endswith('.gz') else open
    with opener(p, 'rt', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except ValueError:
                continue


def glob_json_any(pattern):
    """Glob a logical pattern such as 'data/waiting/questions/*.json'.

    Also matches the .gz form. Returns one logical path (no .gz suffix) per file, .gz preferred
    when both copies exist, so Path(p).stem stays the name the board already uses.
    """
    found = {}
    for hit in glob.glob(pattern) + glob.glob(pattern + '.gz'):
        logical = hit[:-3] if hit.endswith('.gz') else hit
        if logical not in found or hit.endswith('.gz'):
            found[logical] = logical
    return [found[k] for k in sorted(found)]


def save_json_gz(path, obj, end='', **kwargs):
    """Write obj as gzip JSON at path+'.gz' and remove the plain file."""
    plain, gz = _pair(path)
    gz.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(obj, **kwargs) + end).encode('utf-8')
    gz.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    if plain.exists() and plain.resolve() != gz.resolve():
        plain.unlink()
    return gz


def save_text_gz(path, text):
    """Write text as gzip at path+'.gz' and remove the plain file. For the question .md pages."""
    plain, gz = _pair(path)
    gz.parent.mkdir(parents=True, exist_ok=True)
    raw = text.encode('utf-8') if isinstance(text, str) else text
    gz.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    if plain.exists() and plain.resolve() != gz.resolve():
        plain.unlink()
    return gz


def append_jsonl_gz(path, obj):
    """Append one JSON line to path.gz. A plain file with no .gz yet is folded in first, then removed."""
    plain, gz = _pair(path)
    line = (json.dumps(obj, ensure_ascii=False) + '\n').encode('utf-8')
    gz.parent.mkdir(parents=True, exist_ok=True)
    if plain.is_file() and not gz.is_file():
        raw = plain.read_bytes()
        if raw and not raw.endswith(b'\n'):
            raw += b'\n'
        gz.write_bytes(gzip.compress(raw + line, compresslevel=9, mtime=0))
        plain.unlink()
        return gz
    with gzip.open(gz, 'ab') as fh:
        fh.write(line)
    if plain.is_file() and plain.resolve() != gz.resolve():
        plain.unlink()
    return gz
