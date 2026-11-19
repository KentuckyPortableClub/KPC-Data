#!/usr/bin/env python3
"""Nov 19 (storage): a .gz file whose inside did not change is not written again (two Python
versions write a different gzip header byte, so identical questions were saved as 'new'), and the
scoreboard is not saved when only its date stamp moved. Offline, temp folder only."""
import gzip, importlib.util, json, os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / '.github' / 'scripts'))
import kpc_json_any as J
ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg); ok = ok and bool(c)


d = pathlib.Path(tempfile.mkdtemp(prefix='kpc-same-'))
f = d / 'q.json'; gz = d / 'q.json.gz'
obj = {'built': '2026-11-19', 'questions': [{'ref': 'US-1', 'answer': ''}] * 50}
J.save_json_gz(f, obj, indent=1)
raw = gzip.decompress(gz.read_bytes())
other = bytearray(gzip.compress(raw, compresslevel=9, mtime=0)); other[9] = 0x03 if other[9] != 0x03 else 0xff   # the other Python's header byte
gz.write_bytes(bytes(other)); before = gz.read_bytes()
check(gzip.decompress(before) == raw, 'set-up: the other header byte still reads the same')
J.save_json_gz(f, obj, indent=1)
check(gz.read_bytes() == before, 'same inside, other header byte: the file is NOT written again')
obj2 = dict(obj, built='2026-11-20')
J.save_json_gz(f, obj2, indent=1)
check(J.load_json_any(f)['built'] == '2026-11-20', 'a real change is written')
gz.write_bytes(b'not gzip at all')
J.save_json_gz(f, obj, indent=1)
check(J.load_json_any(f) == obj, 'a file that does not read is written fresh')
t = d / 'page.md'; J.save_text_gz(t, 'hello'); b = (d / 'page.md.gz').read_bytes(); st = (d / 'page.md.gz').stat().st_mtime_ns
J.save_text_gz(t, 'hello'); check((d / 'page.md.gz').stat().st_mtime_ns == st, 'text page, same words: not written again')
J.save_text_gz(t, 'hello 2'); check(gzip.decompress((d / 'page.md.gz').read_bytes()) == b'hello 2', 'text page, new words: written')
(d / 'p.json').write_text('{}'); J.save_json_gz(d / 'p.json', {'a': 1}); J.save_json_gz(d / 'p.json', {'a': 1})
check(not (d / 'p.json').exists() and (d / 'p.json.gz').exists(), 'the plain twin is still removed')

os.chdir(d)
spec = importlib.util.spec_from_file_location('sb', HERE / '.github/scripts/kpc_scoreboard_bot.py'); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
p = d / 'scoreboard.json'
S.save(p, {'generated': '2026-11-18', 'states': {'KY': 1}})
S.save(p, {'generated': '2026-11-19', 'states': {'KY': 1}})
check(json.load(open(p))['generated'] == '2026-11-18', 'scoreboard: only the date moved -> not saved again')
S.save(p, {'generated': '2026-11-19', 'states': {'KY': 2}})
check(json.load(open(p)) == {'generated': '2026-11-19', 'states': {'KY': 2}}, 'scoreboard: a count changed -> saved, with the new date')
S.save(d / 'new.json', {'built': 'x', 'parks': {}}); check((d / 'new.json').exists(), 'scoreboard: a first save still happens')

print('ALL PASS' if ok else 'SOME FAILED'); sys.exit(0 if ok else 1)
