#!/usr/bin/env python3
"""KEY COPY RECONCILE (Nov 6 2026 improvements v2, item 3; Mapping's chat 5:28 PM CST Nov 5: "propose AND patch a reconcile fix
in this round, so the two can't silently diverge again ... a count/stamp check in the copy step that fails closed").

Root cause it guards (AU gap, Quality grade 2026-11-06): KPC-Data's world key had 1,599 more AU outlines than KPC-Links' under the
same build stamp W-42037731597. They were NOT a builder, shard, timeout or filter difference: kpc_key_approved.py (kpc-scoreboard.yml,
Nov 2) adds chat 11 YES records BY RECORD NUMBER to KPC-Data's copy only ('approved' field, how 'name (chat 11 YES)'), the KPC-Links
builder never sees them, and Step B3 copies index.json (the stamp) on every copy while an unchanged KPC-Links area file is put back
as "an old mirror". So one stamp named two different contents. B3 also brought KPC-Links' layers.json over KPC-Data's, which
dropped the new 'approved layer' labels those joins point at: the site (kpc-bounds.js worldKey) could not draw them.

  merge-layers  (B3, before the waiting room) FIRST (v2.1, Quality MUST-ADD) every approved join a world overrides 'no' names
                (record id or name; KPC-Data's and KPC-Links' overrides.json, e.g. AU-8945 vs record 805 Godwin Beach) is taken
                out of 'm' into 'c' ('no: ...', nothing deleted), so it can never draw once its label is back; THEN every layer label a KPC-Data world key file (live or held) points at that is missing
                from the incoming layers.json is put back: its address from KPC-Data's last committed layers.json, else from the
                chat 11 YES question that made the join (data/waiting/questions). Nothing removed. The changed layers.json then
                goes to the waiting room like any changed key file (chat 11 releases it).
  check         (B3, after the waiting room) for every key whose KPC-Data index.json carries the SAME build as KPC-Links', each area
                file of KPC-Data's newest copy (held, else live) must equal KPC-Links' file park for park, EXCEPT joins
                kpc_key_approved.py added ('approved' field) to a park KPC-Links leaves without an outline (or does not have).
                Any other difference, or an approved join whose layer label is missing from KPC-Data's newest layers.json, FAILS
                CLOSED: exit 1, data/status/key-copy/reconcile.json + .md list it, and B3 puts that key's index.json back (the stamp
                does not move) and reports it.
  LINKS=<KPC-Links checkout> (default ../links)   run from the KPC-Data checkout   KEYS=world-key,ca-key,us-key   --selftest
Reads files only, no network."""
import collections, json, os, pathlib, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kpc_json_any import glob_json_any, load_json_any  # noqa: E402

WK, HELD = 'data/world-key', 'data/waiting/in/data/world-key'
OUT = 'data/status/key-copy'


def load(p, d=None):
    try: return load_json_any(p)
    except Exception: return d  # noqa: BLE001


def newest(rel):
    h = os.path.join('data/waiting/in', rel)
    return h if os.path.exists(h) else rel


def area_files(d):
    return sorted(f for f in os.listdir(d) if f.endswith('.json') and f[:-5].replace('-', '').isalnum() and f[:-5].upper() == f[:-5]) if os.path.isdir(d) else []


def approved(p): return isinstance(p, dict) and isinstance(p.get('approved'), dict) and bool(p.get('m'))


def labels_needed(root='.'):
    """{label: [refs]} the 'approved' joins of KPC-Data's world key files (live and held) point at."""
    need = collections.defaultdict(list)
    for d in (WK, HELD):
        for f in area_files(os.path.join(root, d)):
            for ref, p in ((load(os.path.join(root, d, f), {}) or {}).get('parks') or {}).items():
                if approved(p):
                    for x in p['m']:
                        if isinstance(x, list) and len(x) > 2 and isinstance(x[2], str): need[x[2]].append(ref)
    return need


DECIDED_BY = 'Brandon standing rule 2026-11-05 verify-then-fix'


def world_nos(root='.', links=None):
    """{ref: lowercased ids / names} from the VERIFIED world overrides 'no' lists (decided_by set; KPC-Data's copy + KPC-Links')."""
    out = {}
    for p in (os.path.join(root, WK, 'overrides.json'), os.path.join(links or os.environ.get('LINKS') or '../links', WK, 'overrides.json')):
        for r, v in ((load(p, {}) or {}).get('parks') or {}).items():
            # only a VERIFIED no (decided_by, verify-then-fix; AU-8945). An older name-only NO that chat 11 later answered YES on
            # another layer is a conflict for a person: listed by conflicts(), not taken out here
            if isinstance(v, dict) and v.get('no') and v.get('decided_by'): out.setdefault(r, set()).update(str(x).strip().lower() for x in v['no'])
    return out


def apply_no(root='.', links=None):
    """Approved joins a world 'no' names leave 'm' (kept in 'c'). Runs BEFORE the label restore. Returns {file: [refs]}."""
    NO, done = world_nos(root, links), {}
    for d in (WK, HELD):
        for f in area_files(os.path.join(root, d)):
            fp = os.path.join(root, d, f); K = load(fp, {}) or {}; hit = []
            for ref, p in (K.get('parks') or {}).items():
                if not (approved(p) and NO.get(ref)): continue
                bad = [x for x in p['m'] if isinstance(x, list) and x and ({str(x[0]).lower(), str(x[1] if len(x) > 1 else '').strip().lower()} & NO[ref])]
                if not bad: continue
                p['m'] = [x for x in p['m'] if x not in bad]
                p['c'] = [x[:3] + [f"no: world overrides 'no' ({DECIDED_BY})"] for x in bad] + list(p.get('c') or [])
                p['approved'] = dict(p['approved'], no=f"{len(bad)} record(s) taken out by the world overrides 'no' (kpc_key_reconcile.py)")
                hit.append(ref)
            if hit:
                json.dump(K, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':')); done[os.path.join(d, f)] = hit
    return done


def merge_layers(root='.', committed=None, links=None):
    """Apply the world 'no' list, then put back missing labels. Returns {file: n added} (+ '_no': {file: refs})."""
    nod = apply_no(root, links)
    need = labels_needed(root)
    if committed is None:
        try: committed = json.loads(subprocess.run(['git', 'show', f'HEAD:{WK}/layers.json'], cwd=root, capture_output=True, text=True, timeout=60).stdout or '{}')
        except Exception: committed = {}  # noqa: BLE001
    q = {}
    for f in glob_json_any(os.path.join(root, 'data/waiting/questions/*.json')):
        d = load(f, None); qs = d.get('questions') if isinstance(d, dict) else d
        for x in qs if isinstance(qs, list) else []:
            if isinstance(x, dict) and x.get('ref') and str(x.get('answer') or '').upper().startswith('YES'):
                q.setdefault(str(x['ref']), str(x.get('layer') or x.get('url') or '').rstrip('/'))
    done = {}
    for rel in (f'{WK}/layers.json', f'{HELD}/layers.json'):
        p = os.path.join(root, rel)
        if not os.path.exists(p): continue
        L = load(p, {}) or {}; n = 0
        for lab, refs in need.items():
            if lab in L: continue
            url = committed.get(lab) if isinstance(committed.get(lab), str) else None
            if not url:
                lid = lab.rsplit('(approved layer ', 1)[-1].rstrip(')') if '(approved layer ' in lab else ''
                url = next((q[r] for r in refs if q.get(r) and (not lid or q[r].rsplit('/', 1)[-1] == lid)), None)
            if url: L[lab] = url; n += 1
        if n:
            json.dump(L, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); done[rel] = n
    if nod: done['_no'] = nod
    return done


def compare(lp, dp, layers):
    """Per area file: (counts, [unexplained rows]) KPC-Links parks lp vs KPC-Data newest parks dp."""
    c = collections.Counter(); bad = []
    c['links_outlined'] = sum(1 for p in lp.values() if isinstance(p, dict) and p.get('m'))
    c['data_outlined'] = sum(1 for p in dp.values() if isinstance(p, dict) and p.get('m'))
    for ref in sorted(set(lp) | set(dp)):
        a, b = lp.get(ref), dp.get(ref)
        if a == b: continue
        if isinstance(b, dict) and not b.get('m') and not (a or {}).get('m'):
            c['pin_both'] += 1; continue   # a pin in both (e.g. a join the world 'no' took out): nothing to draw, nothing differs
        if approved(b) and not (a or {}).get('m'):
            c['approved_adds'] += 1
            miss = [x[2] for x in b['m'] if isinstance(x, list) and len(x) > 2 and isinstance(x[2], str) and x[2] not in layers]
            if miss: c['approved_label_missing'] += 1; bad.append({'park': ref, 'why': f'approved join points at a layer label missing from layers.json: {miss[0][:80]}'})
            continue
        if isinstance(a, dict) and isinstance(b, dict) and a.get('m') == b.get('m') and approved(b) is False:
            c['same_join_other_fields'] += 1; continue
        c['unexplained'] += 1
        bad.append({'park': ref, 'why': 'only in KPC-Data' if a is None else 'only in KPC-Links' if b is None else
                    f"joins differ (KPC-Links {len((a or {}).get('m') or [])} record(s), KPC-Data {len((b or {}).get('m') or [])})"})
    return c, bad


def check(root='.', links='../links', keys=('world-key', 'ca-key', 'us-key')):
    rep = {'about': 'KPC-Data key copy vs KPC-Links under the same build stamp (kpc_key_reconcile.py check; fails closed)', 'keys': {}}
    fail = []
    for k in keys:
        li, di = load(os.path.join(links, f'data/{k}/index.json'), {}) or {}, load(os.path.join(root, f'data/{k}/index.json'), {}) or {}
        lb, db = li.get('build'), di.get('build')
        kr = {'links_build': lb, 'data_build': db, 'same_stamp': bool(lb) and lb == db, 'files': {}, 'unexplained': 0}
        if kr['same_stamp']:
            layers = load(os.path.join(root, newest(f'data/{k}/layers.json')), {}) or {}
            for f in area_files(os.path.join(links, f'data/{k}')):
                lp = (load(os.path.join(links, f'data/{k}', f), {}) or {}).get('parks') or {}
                dp = (load(os.path.join(root, newest(f'data/{k}/{f}')), {}) or {}).get('parks') or {}
                c, bad = compare(lp, dp, layers)
                if bad or c['approved_adds']:
                    kr['files'][f] = dict(c) | {'rows': bad[:50]}
                    kr['unexplained'] += len(bad)
        if kr['unexplained']: fail.append(k)
        rep['keys'][k] = kr
    rep['failed'] = fail
    os.makedirs(os.path.join(root, OUT), exist_ok=True)
    json.dump(rep, open(os.path.join(root, OUT, 'reconcile.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    md = ['# Key copy reconcile (KPC-Data vs KPC-Links, same stamp)', '', rep['about'], '']
    for k, kr in rep['keys'].items():
        md.append(f"- {k}: build {kr['data_build']} (KPC-Links {kr['links_build']}): " + ('FAILED CLOSED, ' if k in fail else 'ok, ') + f"{kr['unexplained']} unexplained")
        for f, c in kr['files'].items():
            md.append(f"  - {f}: KPC-Links {c.get('links_outlined', 0)} outlined, KPC-Data {c.get('data_outlined', 0)}; approved adds {c.get('approved_adds', 0)} "
                      f"(label missing {c.get('approved_label_missing', 0)}); unexplained {c.get('unexplained', 0)}")
    open(os.path.join(root, OUT, 'reconcile.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    return rep


def selftest():
    import tempfile
    ok, n = True, 0
    def chk(name, got, want):
        nonlocal ok, n
        n += 1; good = got == want; ok &= good
        print(('PASS ' if good else 'FAIL ') + name + ('' if good else f'  got={got!r} want={want!r}'))
    A = lambda rid=1, lab='AU: X (approved layer 10)': {'n': 'P', 'm': [[rid, 'P', lab, 'name (chat 11 YES)']], 'c': [], 'approved': {'by': 'chat 11 YES'}}
    P = lambda m=None: {'n': 'P', 'm': m or [], 'c': []}
    L = {'AU: X (approved layer 10)': 'https://h/MapServer/10'}
    chk('identical files: nothing', compare({'AU-1': P()}, {'AU-1': P()}, L)[1], [])
    chk('approved add on a Links pin: explained', compare({'AU-1': P()}, {'AU-1': A()}, L)[0]['approved_adds'], 1)
    chk('approved add on a park Links lacks: explained', compare({}, {'AU-2': A()}, L)[1], [])
    chk('approved add whose label is missing: unexplained (undrawable)', len(compare({'AU-1': P()}, {'AU-1': A()}, {})[1]), 1)
    chk('a different join without approved field: unexplained', compare({'AU-1': P([[1, 'a', 'CAPAD', 'name']])}, {'AU-1': P([[2, 'b', 'CAPAD', 'name']])}, L)[0]['unexplained'], 1)
    chk('Links outlined, Data a pin: unexplained', compare({'AU-1': P([[1, 'a', 'CAPAD', 'name']])}, {'AU-1': P()}, L)[0]['unexplained'], 1)
    chk('approved field over a Links OUTLINE (a swap): unexplained', compare({'AU-1': P([[1, 'a', 'CAPAD', 'name']])}, {'AU-1': A()}, L)[0]['unexplained'], 1)
    chk('a park only in Links: unexplained', compare({'AU-1': P()}, {}, L)[0]['unexplained'], 1)
    td = pathlib.Path(tempfile.mkdtemp(prefix='kpc-reconcile-')); lk = td / 'links'; dk = td / 'data'
    for r in (lk, dk): (r / WK).mkdir(parents=True)
    (dk / 'data/waiting/questions').mkdir(parents=True)
    json.dump({'build': 'W-1'}, open(lk / WK / 'index.json', 'w')); json.dump({'build': 'W-1'}, open(dk / WK / 'index.json', 'w'))
    json.dump({'cc': 'AU', 'parks': {'AU-1': P(), 'AU-3': P([[5, 'c', 'CAPAD', 'name']])}}, open(lk / WK / 'AU.json', 'w'))
    json.dump({'cc': 'AU', 'parks': {'AU-1': A(7), 'AU-2': A(8), 'AU-3': P([[5, 'c', 'CAPAD', 'name']])}}, open(dk / WK / 'AU.json', 'w'))
    json.dump({'CAPAD': 'https://c/0'}, open(dk / WK / 'layers.json', 'w'))
    json.dump({'questions': [{'ref': 'AU-1', 'answer': 'YES', 'layer': 'https://h/MapServer/10', 'record': 7}]}, open(dk / 'data/waiting/questions/layers.json', 'w'))
    r1 = check(str(dk), str(lk), ('world-key',))
    chk('check: label missing -> FAILS CLOSED on world-key', (r1['failed'], r1['keys']['world-key']['files']['AU.json']['approved_label_missing']), (['world-key'], 2))
    chk('merge-layers: the label comes back from the YES question (committed copy has none)', merge_layers(str(dk), committed={}), {f'{WK}/layers.json': 1})
    chk('merge-layers: nothing removed', load(dk / WK / 'layers.json')['CAPAD'], 'https://c/0')
    r2 = check(str(dk), str(lk), ('world-key',))
    chk('check after merge: passes, 2 approved adds explained', (r2['failed'], r2['keys']['world-key']['files']['AU.json']['approved_adds']), ([], 2))
    json.dump({'build': 'W-2'}, open(lk / WK / 'index.json', 'w'))
    chk('different stamps: not compared (the waiting room handles a new build)', check(str(dk), str(lk), ('world-key',))['keys']['world-key']['same_stamp'], False)
    json.dump({'build': 'W-1'}, open(lk / WK / 'index.json', 'w'))
    json.dump({'cc': 'AU', 'parks': {'AU-1': A(7), 'AU-2': A(8), 'AU-3': P()}}, open(dk / WK / 'AU.json', 'w'))
    chk('an outline KPC-Data lost under the same stamp: FAILS CLOSED', check(str(dk), str(lk), ('world-key',))['failed'], ['world-key'])
    # v2.1: the world 'no' (AU-8945 vs record 805) is applied BEFORE the label restore, so the wrong join never draws
    json.dump({'cc': 'AU', 'parks': {'AU-1': A(7), 'AU-2': A(8), 'AU-3': P([[5, 'c', 'CAPAD', 'name']]), 'AU-8945': A(805, 'AU: Beach (approved layer 11)')}}, open(dk / WK / 'AU.json', 'w'))
    json.dump({'questions': [{'ref': 'AU-8945', 'answer': 'YES', 'layer': 'https://q/FeatureServer/11', 'record': 805}]}, open(dk / 'data/waiting/questions/b.json', 'w'))
    json.dump({'parks': {'AU-8945': {'no': ['805', 'Godwin Beach', 'Scarborough Beach'], 'decided_by': DECIDED_BY}, 'AU-1': {'no': ['P'], 'why': 'Oct 30 name-only NO'}}}, open(dk / WK / 'overrides.json', 'w'))
    d3 = merge_layers(str(dk), committed={}, links=str(lk))
    k3 = load(dk / WK / 'AU.json')['parks']['AU-8945']
    chk("merge-layers applies the world 'no' first: AU-8945 record 805 leaves m, kept in c", (d3.get('_no'), k3['m'], [x[0] for x in k3['c']]), ({f'{WK}/AU.json': ['AU-8945']}, [], [805]))
    chk("an older name-only 'no' (no decided_by) is NOT applied: AU-1's later YES join stays", bool(load(dk / WK / 'AU.json')['parks']['AU-1']['m']), True)
    chk("AU-8945's label is not needed any more (no label restored for it; nothing to draw)", 'AU: Beach (approved layer 11)' in load(dk / WK / 'layers.json'), False)
    chk('check after the no: AU-8945 is a pin in both (explained), key passes', check(str(dk), str(lk), ('world-key',))['failed'], [])
    chk('report files written', sorted(os.listdir(dk / OUT)), ['reconcile.json', 'reconcile.md'])
    print(f"SELFTEST {'PASS' if ok else 'FAIL'}: {n} cases")
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--selftest' in sys.argv: sys.exit(0 if selftest() else 1)
    if a[:1] == ['merge-layers']:
        d = merge_layers(); print(f"::notice title=Key reconcile::world 'no' applied first, then layer labels put back: {d or 'none needed'}"); sys.exit(0)
    keys = tuple(x for x in (os.environ.get('KEYS') or 'world-key,ca-key,us-key').split(',') if x)
    r = check('.', os.environ.get('LINKS') or '../links', keys)
    for k, kr in r['keys'].items():
        print(f"::{'error' if k in r['failed'] else 'notice'} title=Key reconcile::{k} build {kr['data_build']}: {kr['unexplained']} unexplained difference(s) vs KPC-Links"
              + (' - FAILS CLOSED: the stamp is not copied (data/status/key-copy/reconcile.md)' if k in r['failed'] else ''))
    print('FAILED=' + ' '.join(r['failed']))
    sys.exit(1 if r['failed'] else 0)
