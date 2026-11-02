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


KEY_KINDS = {'us-key', 'ca-key', 'world-key'}


def held_build(kind):
    """The build id stamped into the held key folder (kpc_key_freeze.py stamp), or ''."""
    return str((W.load(W.W / 'in' / 'data' / kind / 'index.json', {}) or {}).get('build') or '')


def build_mismatch(it, rel):
    """Brandon Nov 2 7:11 AM: 'the YES is tied to that id'. A key item releases only when its 'build' is the held build's id.
    -> '' when fine, else the reason. Held folders built before the stamp existed (no id) keep the old rule."""
    kind = str(it.get('what') or '')
    if kind not in KEY_KINDS: return ''
    hb = held_build(kind)
    if not hb: return ''
    ib = str(it.get('build') or '')
    if not ib and hb in str(it.get('chat11') or ''): ib = hb   # Nov 2: chat 11 wrote the id in its verdict text ('KEY NO US-f3d48d30899 ...'): that counts
    if not ib: return f'the YES has no build id; the waiting room holds build {hb} (write "build": "{hb}" on the item)'
    if ib != hb: return f'the YES is for build {ib}, the waiting room holds build {hb}'
    return ''


def verdict_ok(v):
    """Oct 31 (Fable review #6): chat 11's field decides, whoever created the item (chat 2 creates the 2-fer items: MN + IA were skipped
    twice). Markup is ignored ('**YES**', '"YES', 'KEY: YES', double spaces); a verdict that ALSO says NO / FAIL / HOLD / NOT SURE /
    a question mark is never a release ('YES but NO to 3', 'YES/NO', 'PASS? No.')."""
    t = re.sub(r'[*_`"\'“”‘’✅✔️👍]+', ' ', str(v or ''))
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub(r'^(?:(?:KEY|LAYER|FILE|VERDICT|CHAT ?11)\s*:?\s*)+', '', t, flags=re.I)
    if not re.match(r'^(YES|PASS)\b', t, re.I): return False, 'no YES / PASS from chat 11'
    head = re.split(r'[(;]', t, 1)[0][:60]   # Nov 1 (chat 11): only the verdict itself counts ('YES (no Maryland rows)' is a YES; 'YES/NO', 'YES but NO to 3', 'PASS? No.' are not)
    if re.search(r'\b(NO|FAIL(ED)?|HOLD|NOT SURE|REJECT)\b|\?|\b(YES|PASS)\s*/\s*\w', head, re.I) or re.match(r'^(YES|PASS)\s+(but|except|apart)\b', t, re.I): return False, 'chat 11\'s verdict is mixed (YES/NO, YES but ..., ?): ask chat 11'
    return True, ''


TRUST_KINDS = {'campinfo', 'access', 'docs', 'truth', 'campfed', 'campstate', 'trails', 'leads', 'hours', 'campsites', 'cell', 'acres'}   # never 2-fers, keys, POTA, closures
TRUST_RUN = 3   # Brandon Oct 31 10:00 PM ('I agree to all'): a bot kind whose last 3 chat-11 grades all passed is released by the bot, chat 11 samples 1 in 10


def item_kind(it):
    pth = str(it.get('path') or '').replace('data/waiting/in/', '')
    k = W.kind_of(pth if pth.endswith('.json') else pth.rstrip('/') + '/US-KY.json')[0] if pth else None
    if not k:
        m = re.match(r'([a-z-]+?)(?:-(?:US|CA)-[A-Z]{2})?$', str(it.get('kind') or it.get('what') or ''))
        k = m.group(1) if m else None
    return {'fers': 'fers', 'us-key': 'key', 'ca-key': 'key', 'world-key': 'key'}.get(k, k)


def trusted_kinds(items):
    """kind -> True when its last TRUST_RUN graded items (chat 11's field, newest last) all say YES / PASS and none says NO."""
    hist = {}
    for it in items:
        k = item_kind(it); v = str(it.get('chat11') or '').strip()
        if not k or not v: continue
        hist.setdefault(k, []).append(verdict_ok(v)[0])
    return {k for k, h in hist.items() if k in TRUST_KINDS and len(h) >= TRUST_RUN and all(h[-TRUST_RUN:])}


def auto_trusted(items, log):
    """Held files of a trusted kind whose waiting-room verdict is PASS go live by themselves; 1 in 10 is listed for chat 11's sample
    (data/waiting/sample-for-chat11.json). A chat-11 NO on any sample ends the trust at once (the next run sees it)."""
    import hashlib
    T = trusted_kinds(items)
    if not T: print('::notice title=Release approved (trusted)::no bot kind has 3 passed grades in a row yet'); return
    V = {r['path']: r for r in (W.load(W.W / 'verdicts.json', {}) or {}).get('results') or []}
    S = W.load(W.W / 'sample-for-chat11.json', {'about': 'files a trusted bot released by itself: chat 11 checks these (1 in 10); a NO item in approved.json ends that kind\'s trust', 'files': []}) or {}
    n = 0
    for rel, r in V.items():
        if r.get('kind') not in T or r.get('verdict') not in ('PASS', 'LIVE-FILTERED') or not (W.W / 'in' / rel).exists(): continue
        if not DRY: W.mode_release(rel)
        n += 1; log.append({'item': rel, 'result': f"released (trusted kind {r['kind']}: last {TRUST_RUN} chat-11 grades passed)"})
        if int(hashlib.md5((rel + time.strftime('%Y-%m-%d')).encode()).hexdigest(), 16) % 10 == 0:
            S.setdefault('files', []).append({'path': rel, 'kind': r['kind'], 'date': time.strftime('%Y-%m-%d')})
    if not DRY: json.dump(S, open(W.W / 'sample-for-chat11.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f"::notice title=Release approved (trusted)::trusted kinds {', '.join(sorted(T))}: {n} files released by themselves")


# ---- PER-PARK KEY RELEASE (chat 10, Nov 2 2026; Brandon OK'd the outside review 6:34 AM: 'good parks go live, the few bad ones
# stay pins with the reason'). Chat 11 still grades every build (the file verdict stays). When the LATEST verdict on the held
# US key is a KEY NO, the build no longer waits whole: each held state file is split by the key doctor (engine v0.5.0
# release_split: a park named in the NO, a person's NO that came back, a broken entry or a pin far outside its land keeps the
# LIVE version, or a pin when there is none) and, because a NO names a sample only, every park whose join CHANGED by a weak
# way (alias / partial words) also keeps its live version until a later YES. Strong new joins (exact name, official,
# reviewed) go live. Never on a build that changed after the verdict. Switch KPC_PER_PARK=0 = the old whole-file wait.
WEAK_HOW = ('alias', 'words')


def per_park_release(A, log, U):
    if os.environ.get('KPC_PER_PARK', '1') == '0': return
    eng = pathlib.Path(__file__).parent / 'draft/tools/kpc_engine'
    sys.path.insert(0, str(eng))
    from core import key_doctor as KD   # noqa: E402
    import copy, gzip
    its = [x for x in (A.get('items') or []) if isinstance(x, dict) and x.get('what') == 'us-key' and str(x.get('chat11') or '').strip()]
    it = its[-1] if its else None   # Nov 2: the NEWEST item in the file (the doctor's date sort picked an older one when the newest had no date in its text)
    if not it or KD.first_word(it.get('chat11')) != 'NO':
        print('::notice title=Per-park release::the latest US key verdict is not a KEY NO: nothing to split'); return
    k = json.dumps(it, sort_keys=True, ensure_ascii=False)
    if k in U: print('::notice title=Per-park release::this KEY NO was already used for a per-park release'); return
    held_dir = W.W / 'in' / 'data/us-key'
    if not held_dir.is_dir(): return
    bwhy = build_mismatch(it, 'data/us-key/')
    if bwhy: print(f'::notice title=Per-park release::{bwhy}'); return
    if not it.get('build') and changed_since_yes(it, 'data/us-key/'):
        print('::notice title=Per-park release::the held US key changed after the KEY NO: waits for chat 11 to grade the new build'); return
    fail = set(KD.REF_RX.findall(str(it.get('chat11'))))
    ovr = ((W.load(W.LINKS / 'data/us-key/overrides.json', {}) or {}).get('parks') or {})
    n_go, n_held, files, why_all = 0, 0, [], {}
    for f in KD.key_files(held_dir):
        new = W.load(f, None)
        if not isinstance(new, dict) or not isinstance(new.get('parks'), dict): continue
        live = W.load(W.DATA / 'data/us-key' / f.name.replace('.gz', ''), None)
        lp = ((live or {}).get('parks') or {}) if isinstance(live, dict) else {}
        weak = set()
        for r, pk in new['parks'].items():
            m = (pk or {}).get('m') if isinstance(pk, dict) else None
            if json.dumps(m) == json.dumps((lp.get(r) or {}).get('m')): continue
            if any(len(x) > 3 and str(x[3]).split(' ')[0].rstrip(':') in WEAK_HOW for x in m or [] if isinstance(x, (list, tuple))): weak.add(r)
        out, held = KD.release_split(new, live, fail | weak, ovr)
        for r in (weak - fail) & set(held):
            held[r] = [w if w != 'named in the latest KEY NO' else 'a new alias / partial-name join: waits for a KEY YES' for w in held[r]]
            if r in out['parks'] and isinstance(out['parks'][r], dict) and 'held' in out['parks'][r]:
                out['parks'][r]['held'] = 'per-park release: ' + '; '.join(held[r])
        out['release'] = {**(out.get('release') or {}), 'verdict': str(it.get('chat11'))[:120], 'held_refs': {r: w for r, w in sorted(held.items())}}
        n_go += len(new['parks']) - len(held); n_held += len(held); why_all.update(held)
        if DRY: continue
        txt = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
        if f.name.endswith('.gz'): f.write_bytes(gzip.compress(txt.encode('utf-8'), 6))
        else: f.write_text(txt, encoding='utf-8')
        rel = str(f.relative_to(W.W / 'in'))
        W.mode_release(rel); files.append(rel)
        log.append({'item': rel, 'result': f'released per park ({len(new["parks"]) - len(held)} parks go, {len(held)} keep the live version / a pin)'})
    if not DRY:
        U[k] = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())
        json.dump({'about': 'Parks kept back by the per-park key release (kpc_release_approved.py), with the reason; they go with a later KEY YES',
                   'verdict': str(it.get('chat11'))[:300], 'date': time.strftime('%Y-%m-%d'), 'parks': why_all},
                  open(W.W / 'per-park-held.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'::notice title=Per-park release::{"(dry) " if DRY else ""}{n_go} parks pass (go live) in {len(files)} state files; {n_held} kept their live version or a pin '
          f'(named in the KEY NO, a NO that came back, a broken entry, or a new alias / partial-name join); the list: data/waiting/per-park-held.json')


def main():
    A = W.load(W.W / 'approved.json', {}) or {}
    items = A.get('items') or []
    log = []
    U = W.load(W.W / 'approved-used.json', {}) or {}   # Oct 29 11:25 PM (nightly timer): a YES is used ONCE, so an old YES never lets out a LATER rebuild
    for it in items:
        key = json.dumps(it, sort_keys=True, ensure_ascii=False)
        if key in U: continue
        ok, why = verdict_ok(it.get('chat11'))   # Brandon Oct 29 5:16 PM 'Waiting Room 11 has to approve' = chat 11's own field
        if not ok:
            log.append({'item': it, 'result': f'skipped: {why}'}); print(f"::notice title=Release approved::skipped {it.get('what') or it.get('path')}: {why}"); continue
        if it.get('what') == 'keyed-parking':
            files, n = keyed_parking()
            for rel, new, k in files:
                dst = W.W / 'in' / rel; dst.parent.mkdir(parents=True, exist_ok=True)
                if not DRY: json.dump(new, open(dst, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
                log.append({'item': 'keyed-parking', 'file': rel, 'points_added': k})
            print(f'::notice title=Release approved::keyed parking: {n} new points in {len(files)} state files sent through the waiting room')
        elif it.get('path'):
            if item_kind(it) in ('key', 'fers') and not str(it.get('chat2') or '').strip(): log.append({'item': it, 'result': "skipped: no chat 2 recheck (Rule G-4: keys + 2-fers only)"}); continue   # Nov 1 (chats 2 + 11): campinfo / hours / truth / docs need chat 11's YES only
            rel = str(it['path']).replace('data/waiting/in/', '')
            bwhy = build_mismatch(it, rel)
            if bwhy: log.append({'item': it, 'result': 'skipped: ' + bwhy}); print(f"::notice title=Release approved::skipped {it.get('what')}: {bwhy}"); continue
            if rel.endswith('/') and (W.W / 'in' / rel).is_dir() and not it.get('build') and changed_since_yes(it, rel):
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
    try: per_park_release(A, log, U)
    except Exception as e: print(f'::notice title=Per-park release::skipped ({type(e).__name__}: {e})')  # noqa: BLE001
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
    try: auto_trusted(items, log)
    except Exception as e: print(f'::notice title=Release approved (trusted)::skipped ({type(e).__name__}: {e})')  # noqa: BLE001
    if not DRY and any(l.get('item') == 'keyed-parking' for l in log):
        os.environ['WAITING_ON'] = '1'; os.environ['PROMOTE_KINDS'] = 'access'; W.mode_check(True)   # the keyed files pass the same checks as any bot file
    with open(W.W / 'released.jsonl', 'a', encoding='utf-8') as fh:
        for l in log: fh.write(json.dumps({'date': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), 'dry': DRY, **l}, ensure_ascii=False) + '\n')
    print(f'::notice title=Release approved::{len(items)} approvals read, {len(log)} actions' + (' (DRY: nothing moved)' if DRY else ''))


if __name__ == '__main__':
    try: main()
    except Exception as e: print(f'::notice title=Release approved::stopped ({type(e).__name__}: {e}): nothing more moved')  # noqa: BLE001
    sys.exit(0)
