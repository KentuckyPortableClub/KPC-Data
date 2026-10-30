#!/usr/bin/env python3
"""RELEASE WHAT IS APPROVED (chat 10, Oct 29 2026; Brandon 3:02 PM: 'Soon as it gets done with 8 and 11 approves release it and
whatever has been approved to leave waiting room'; 3:04 PM: the waiting room releases ONLY items with a Rule G verdict).
ONE batch, run by hand (waiting-room workflow, mode 'release-approved') on the day chat 8 + chat 11 have written PASS:
  data/waiting/approved.json  {"items": [
      {"what": "keyed-parking", "chat11": "PASS v3b (Oct 29)", "by": "HQ", "date": "2026-10-30"},
      {"path": "data/waiting/in/data/access/US-NY.json", "chat11": "YES", "chat2": "rechecked", "date": "..."}]}
  - an item needs a chat 11 verdict (YES / PASS ...); a waiting-room file also needs chat 2's recheck (Rule G-4);
  - 'keyed-parking' = chat 9's HOLD file data/access-leads/keyed-pull-hold.json: its points are merged into each state's access
    file (a point within 30 m of one we have is skipped), credited 'Recreation.gov / National Park Service data', and every changed
    state file goes through the waiting room's own checks (kpc_waiting_room.py) like any bot file: a file that fails is HELD;
  - nothing without an approval moves. Writes data/waiting/released.jsonl (what went out). Never fails.
  python3 kpc_release_approved.py [--dry]"""
import json, math, os, pathlib, re, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import kpc_waiting_room as W  # noqa: E402

DRY = '--dry' in sys.argv
CREDIT = 'Recreation.gov / National Park Service data'


def km(a, b, c, d): return W.km(a, b, c, d)


def keyed_parking():
    H = W.load(W.DATA / 'data' / 'access-leads' / 'keyed-pull-hold.json', {}) or {}
    by_st, added = {}, 0
    for ref, p in (H.get('parks') or {}).items():
        st = p.get('st')
        if not st: continue
        for q in p.get('pts') or []:   # a multi-state park: each point goes to the state it sits in (Sawtooth NF points are in Idaho)
            s2 = st
            if q.get('la') is not None and (W.pin_of(ref) or (0, 0, '', ''))[3] == 'multi':
                for s in [st] + [a for a in W.STATE_NAMES if a != st]:
                    try:
                        if ref in W.parks(s) and W.in_state(s, q['la'], q['lo'], 0): s2 = s; break
                    except W.Unsure: continue
            by_st.setdefault(s2, {}).setdefault(ref, []).append(q)
    by_st = {s: list(v.items()) for s, v in by_st.items()}
    out = []
    for st, rows in sorted(by_st.items()):
        rel = f'data/access/US-{st}.json'
        live = W.load(W.DATA / rel) or {'note': 'Official parking / entrance points, tied to POTA parks.', 'parks': {}, 'read': {}, 'src': '', 'st': st}
        new = json.loads(json.dumps(live)); n = 0
        for ref, pts in rows:
            have = new['parks'].setdefault(ref, [])
            for q in pts:
                if q.get('la') is None: continue
                if any(km(q['la'], q['lo'], h[0], h[1]) < .03 for h in have): continue
                have.append([q['la'], q['lo'], f"{q.get('label') or 'Parking'} ({CREDIT})", 'place']); n += 1
            if not have: new['parks'].pop(ref, None)
        if not n: continue
        new.setdefault('credits', []); CREDIT in new['credits'] or new['credits'].append(CREDIT)
        added += n; out.append((rel, new, n))
    return out, added


def changed_since_yes(it, rel):
    """Oct 30: a folder YES is for the build chat 11 sampled. Find the commit that wrote this YES into approved.json and compare the held
    folder then and now (git tree ids). Different = a newer rebuild came in after the YES: never released on an old YES."""
    import subprocess
    g = lambda *a: subprocess.run(['git', '-C', str(W.DATA)] + list(a), capture_output=True, text=True).stdout.strip()
    snip = str(it.get('chat11') or '')[:40]
    c = g('log', '-1', '--format=%H', '-S', snip, '--', 'data/waiting/approved.json')
    if not c: return False   # no history to compare (shallow checkout): trust the YES as before
    path = f'data/waiting/in/{rel}'.rstrip('/')
    then, now = g('rev-parse', f'{c}:{path}'), g('rev-parse', f'HEAD:{path}')
    return bool(then and now and then != now and not then.startswith(c[:0] + 'fatal'))


def main():
    A = W.load(W.W / 'approved.json', {}) or {}
    items = A.get('items') or []
    log = []
    U = W.load(W.W / 'approved-used.json', {}) or {}   # Oct 29 11:25 PM (nightly timer): a YES is used ONCE, so an old YES never lets out a LATER rebuild
    for it in items:
        key = json.dumps(it, sort_keys=True, ensure_ascii=False)
        if key in U: continue
        v = str(it.get('chat11') or '').strip()
        if not (re.match(r'^(?:KEY |LAYER )?(YES|PASS)\b', v, re.I) and str(it.get('by') or '').strip().lower() == 'chat 11'):   # Oct 30: chat 11 writes 'KEY YES ...' for keys   # Brandon 5:16 PM: 'Waiting Room 11 has to approve': only chat 11's own written YES / PASS
            log.append({'item': it, 'result': 'skipped: no YES / PASS written by chat 11'}); continue
        if it.get('what') == 'keyed-parking':
            files, n = keyed_parking()
            for rel, new, k in files:
                dst = W.W / 'in' / rel; dst.parent.mkdir(parents=True, exist_ok=True)
                if not DRY: json.dump(new, open(dst, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
                log.append({'item': 'keyed-parking', 'file': rel, 'points_added': k})
            print(f'::notice title=Release approved::keyed parking: {n} new points in {len(files)} state files sent through the waiting room')
        elif it.get('path'):
            if not str(it.get('chat2') or '').strip(): log.append({'item': it, 'result': "skipped: no chat 2 recheck (Rule G-4)"}); continue
            rel = str(it['path']).replace('data/waiting/in/', '')
            if rel.endswith('/') and (W.W / 'in' / rel).is_dir() and changed_since_yes(it, rel):
                log.append({'item': it, 'result': 'skipped: the held build changed after the YES (a newer rebuild was copied in): chat 11 re-samples (data/waiting/preview/)'}); continue
            if rel.endswith('/') and (W.W / 'in' / rel).is_dir():   # a whole folder approved (a key rebuild: data/us-key/)
                for f in sorted((W.W / 'in' / rel).rglob('*.json*')):
                    r2 = str(f.relative_to(W.W / 'in'))
                    if not DRY: W.mode_release(r2)
                    log.append({'item': r2, 'result': 'released (approved folder)'})
                continue
            if (W.W / 'in' / rel).exists():
                if not DRY: W.mode_release(rel)
                log.append({'item': rel, 'result': 'released (approved)'})
            else: log.append({'item': rel, 'result': 'nothing waiting there'})
    if not DRY:
        for it in items:
            k = json.dumps(it, sort_keys=True, ensure_ascii=False)
            if k not in U and any(l.get('item') == it.get('what') or (it.get('path') and str(l.get('item', '')).startswith(str(it['path']).replace('data/waiting/in/', '').rstrip('/'))) for l in log if 'result' not in l or l['result'].startswith('released')):
                U[k] = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())
        json.dump(U, open(W.W / 'approved-used.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        keys = sorted({str(l['item']) for l in log if str(l.get('result', '')).startswith('released') and re.match(r'^data/(us|ca)-key/', str(l.get('item', '')))})
        if keys:   # chat 2 BOT E (11:20 PM): which states' outlines just went live, so the 2-fers rerun only there
            sha = os.popen(f'git -C "{W.DATA}" rev-parse HEAD 2>/dev/null').read().strip()
            sts = sorted({m.group(1) for k in keys for m in [re.search(r'/((?:US|CA)-[A-Z]{2})\.json', k)] if m})
            json.dump({'date': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), 'sha_before': sha, 'files': keys, 'states': sts,
                       'previous': 'data/waiting/previous/ (the live copies just replaced)'}, open(W.W / 'released-key.json', 'w', encoding='utf-8'), indent=1)
            open('/tmp/kpc-key-released', 'w').write(' '.join(sts))
            print(f'::notice title=Release approved::key released for {len(sts)} areas: data/waiting/released-key.json written for the 2-fer rerun')
    if not DRY and any(l.get('item') == 'keyed-parking' for l in log):
        os.environ['WAITING_ON'] = '1'; os.environ['PROMOTE_KINDS'] = 'access'; W.mode_check(True)   # the keyed files pass the same checks as any bot file
    with open(W.W / 'released.jsonl', 'a', encoding='utf-8') as fh:
        for l in log: fh.write(json.dumps({'date': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), 'dry': DRY, **l}, ensure_ascii=False) + '\n')
    print(f'::notice title=Release approved::{len(items)} approvals read, {len(log)} actions' + (' (DRY: nothing moved)' if DRY else ''))


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Release approved::stopped ({type(e).__name__}: {e}): nothing more moved')  # noqa: BLE001
    sys.exit(0)
