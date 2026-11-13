#!/usr/bin/env python3
"""Nov 13 (KPC owner): promote 2-fer files one area (state or province) at a time.

  python3 kpc_fers_release_areas.py --areas 'US-KY CA-AB' --grade path/to/verdicts.json [--dry]
Each area is judged on its own. Green + Quality RELEASE-READY: YES + no worse than live (and never 0 pairs
replacing live pairs, never a world 2-fer, never US-42797939226) is promoted; a held or failed area keeps
its live data and does not block the others. data/fers/LIVE.json records the build each area came from.
Owner-run: started from the waiting-room workflow (mode release-areas). Does not merge itself.
"""
import json, os, pathlib, re, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import kpc_waiting_room as W  # noqa: E402
import kpc_fers_annotate as A  # noqa: E402

DRY = '--dry' in sys.argv
BLOCKED_BUILDS = frozenset({'US-42797939226'})
LIVE_FILE = W.DATA / 'data' / 'fers' / 'LIVE.json'
LIVE_ST = ('candidate', 'very tight', 'water only')


def parse_areas(text):
    out = []
    for tok in (text or '').replace(',', ' ').split():
        t = tok.strip().upper()
        if re.fullmatch(r'(?:US|CA)-[A-Z]{2}', t): out.append(t)
        elif re.fullmatch(r'W-[A-Z]{2}', t):
            raise SystemExit(f'::error title=2-fer release::{t} is a world 2-fer: world 2-fers are never public')
        else:
            raise SystemExit(f"::error title=2-fer release::not an area name: {tok!r} (use US-KY or CA-AB)")
    if not out: raise SystemExit('::error title=2-fer release::areas is empty')
    return out


def load_grade(path):
    if not path: return None
    f = pathlib.Path(path)
    if not f.is_file(): return None
    try:
        d = json.loads(f.read_text(encoding='utf-8'))
        return d if isinstance(d, dict) else None
    except ValueError: return None


def grade_allows(grade, unit):
    if not isinstance(grade, dict): return False, 'no Quality grade (need RELEASE-READY: YES)'
    if grade.get('build') in BLOCKED_BUILDS: return False, f"{grade.get('build')} is never released"
    per = (grade.get('areas') or {}).get(unit) or (grade.get('per_area') or {}).get(unit)
    if isinstance(per, dict):
        ready = str(per.get('RELEASE-READY') or per.get('release_ready') or '').strip().upper()
        if ready != 'YES': return False, 'Quality did not mark this area RELEASE-READY: YES'
        if per.get('no_worse_than_live') is False: return False, 'Quality: worse than live'
        return True, ''
    top = str(grade.get('RELEASE-READY') or grade.get('release_ready') or '').strip().upper()
    if top != 'YES': return False, f"Quality RELEASE-READY is {top or 'missing'}, not YES"
    return True, ''


def live_pairs(doc):
    n = 0
    for s in (doc or {}).get('spots') or []:
        if isinstance(s, dict) and str(s.get('status') or '').startswith(LIVE_ST):
            n += 1
    return n


def hidden_path(unit):
    for f in (W.W / 'in' / 'data' / 'fers' / f'{unit}.json', W.W / 'in' / 'data' / 'fers' / f'{unit}.json.gz'):
        if f.is_file(): return f
    return None


def stamp_path(unit):
    return W.DATA / 'data' / 'fers' / 'stamps' / f'{unit}.json'


def _links_root():
    env = os.environ.get('LINKS') or os.environ.get('RELEASED_KEYS') or ''
    return pathlib.Path(env) if env else None


def _park_key_unit(ref, links):
    """US-4558 / CA-0110 -> US-XX / CA-XX using the key files at LINKS, or None."""
    if not links: return None
    kind = 'us-key' if ref.startswith('US-') else 'ca-key' if ref.startswith('CA-') else None
    if not kind: return None
    folder = links / 'data' / kind
    if not folder.is_dir():
        folder = links / 'data' / 'released' / kind
    if not folder.is_dir(): return None
    for fp in folder.glob('US-??.json' if kind == 'us-key' else 'CA-??.json'):
        try:
            if ref in ((json.loads(fp.read_text()) or {}).get('parks') or {}):
                return fp.stem
        except (ValueError, OSError):
            continue
    return None


def keys_not_ready(unit, doc):
    """A 2-fer area releases only if both (all) of its key areas are released and current. Cross-border needs both."""
    links = _links_root()
    if links is None or not pathlib.Path(links).exists():
        return 'no Links tree: key areas are not proven released and current (2-fers keep live)'
    need = {unit}
    for pr in A.pairs_of(doc or {}, live_only=False):
        for ref in pr.replace('+', ' ').split():
            u = _park_key_unit(ref, links)
            if u: need.add(u)
    stamp = W.load(stamp_path(unit)) or {}
    fers_key_build = str(stamp.get('key_source') or '')
    missing = []
    live_idx = pathlib.Path(links) / 'data' / 'released' / 'RELEASED.json'
    try:
        idx = json.loads(live_idx.read_text()) if live_idx.is_file() else None
    except (ValueError, OSError):
        idx = 'unreadable'
    for u in sorted(need):
        if u.startswith('W-'):
            missing.append(f'{u} (world key, 2-fers stay live)')
            continue
        kind = 'us-key' if u.startswith('US-') else 'ca-key' if u.startswith('CA-') else None
        if not kind:
            continue
        rel = pathlib.Path(links) / 'data' / 'released' / kind / f'{u}.json'
        if not rel.is_file():
            missing.append(f'{u} key is not released')
            continue
        if idx == 'unreadable':
            missing.append(f'{u} key: RELEASED.json is unreadable')
            continue
        if not isinstance(idx, dict):
            missing.append(f'{u} key is not proven current (no RELEASED.json live ledger)')
            continue
        rec = ((idx.get('live') or {}).get(u) or {})
        build = str(rec.get('build') or '')
        if not build:
            missing.append(f'{u} key live record has no build id (not current)')
            continue
        # current: the 2-fer was made from the same build id as the released key
        if fers_key_build and fers_key_build != build:
            missing.append(f'{u} key is build {build}, 2-fer was made from {fers_key_build}')
    if missing:
        return 'key areas not released and current: ' + '; '.join(missing) + ' (2-fers keep live)'
    return ''


def why_not(unit, grade):

    if unit.startswith('W-'): return 'world 2-fers are never public'
    src = hidden_path(unit)
    if src is None: return 'no hidden file waiting for this area (live stays as it is)'
    new = W.load(src)
    live = W.load(W.DATA / 'data' / 'fers' / f'{unit}.json') or W.load(W.DATA / 'data' / 'fers' / f'{unit}.json.gz')
    if (stamp := W.load(stamp_path(unit)) or {}) and str(stamp.get('run') or stamp.get('key_source') or '') in BLOCKED_BUILDS:
        return f"{stamp.get('run')} is never released"
    if str((stamp or {}).get('build') or '') in BLOCKED_BUILDS:
        return f"{stamp.get('build')} is never released"
    ok, why = grade_allows(grade, unit)
    if not ok: return why
    n_live, n_new = live_pairs(live), live_pairs(new)
    if live and n_live > 0 and n_new == 0:
        return f'hidden file has 0 pairs, live has {n_live}: never replace live with 0 pairs'
    if live and n_new < n_live and (grade.get('areas') or {}).get(unit, {}).get('no_worse_than_live') is not True:
        # Quality regrade: any drop, not only >20%, needs the no_worse_than_live mark
        return f'live pairs {n_live} -> {n_new}: worse than live'
    why = keys_not_ready(unit, new)
    if why: return why
    return ''


def record_live(unit, meta):
    doc = W.load(LIVE_FILE, {}) or {}
    if not isinstance(doc, dict): doc = {}
    live = doc.get('areas') if isinstance(doc.get('areas'), dict) else {}
    live[unit] = meta
    doc = {'about': 'Which build each area\'s live 2-fer file came from. Written only by kpc_fers_release_areas.py.',
           'areas': live}
    if not DRY:
        LIVE_FILE.parent.mkdir(parents=True, exist_ok=True)
        LIVE_FILE.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    argv = [x for x in sys.argv[1:] if x != '--dry']
    areas, grade_path = '', ''
    i = 0
    while i < len(argv):
        if argv[i] == '--areas' and i + 1 < len(argv): areas = argv[i + 1]; i += 2
        elif argv[i] == '--grade' and i + 1 < len(argv): grade_path = argv[i + 1]; i += 2
        else: i += 1
    units = parse_areas(areas or os.environ.get('AREAS') or '')
    grade = load_grade(grade_path or os.environ.get('GRADE') or (W.DATA / 'data/status/quality/verdicts.json'))
    promoted, kept = [], []
    t = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    for unit in units:
        try:
            why = why_not(unit, grade)
            if why:
                kept.append((unit, why))
                print(f'::notice title=2-fer release::{unit} kept live ({why})')
                continue
            rel = hidden_path(unit)
            rel_posix = rel.relative_to(W.W / 'in').as_posix() if rel else f'data/fers/{unit}.json'
            if DRY:
                promoted.append(unit)
                print(f'::notice title=2-fer release::{unit} would be promoted (dry run)')
                continue
            # refuse world / 0-pair already checked; still go through waiting-room promote so previous/ undo is kept
            if W.promote_file(rel_posix, None, raw=rel) is False:
                kept.append((unit, 'waiting room refused the promote'))
                print(f'::notice title=2-fer release::{unit} kept live (waiting room refused the promote)')
                continue
            if rel: rel.unlink(missing_ok=True)
            stamp = W.load(stamp_path(unit)) or {}
            record_live(unit, {'build': str(stamp.get('run') or stamp.get('build') or ''),
                               'rules': str(stamp.get('rules') or ''),
                               'sha': str(stamp.get('built_sha') or ''),
                               'time': t, 'key_source': str(stamp.get('key_source') or '')})
            promoted.append(unit)
            print(f'::notice title=2-fer release::{unit} promoted')
        except Exception as e:  # noqa: BLE001  a broken hidden file or judge error on one area must not abort the others
            kept.append((unit, f'cannot promote this area ({type(e).__name__}: {str(e)[:160]})'))
            print(f'::notice title=2-fer release::{unit} kept live (cannot promote this area: {type(e).__name__})')
            continue
    print(f"::notice title=2-fer release::{len(promoted)} area(s) promoted, {len(kept)} kept live")
    if not promoted:
        print('::error title=2-fer release::no area was promoted. Nothing was released.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
