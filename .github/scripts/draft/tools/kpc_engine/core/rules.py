"""The club's switches (config/rules.json) and the LOCKED safety rules.

Defaults reproduce today's rules exactly. Overrides, in order: config/rules.json (or the file in env KPC_RULES), then the
command line: --enable a,b  --disable a,b  --scope hours=US-KY,US-TN  (repeat --scope per plug-in).
Switch names are dotted paths: 'hours' (a plug-in), 'hours_rules.reject_fragments', 'source_policy.wdpa_guard',
'source_policy.never_use.google', 'checks.containers'. Numbers: --set grader.rg12_m=150.

Anything off its default is (a) printed loudly at the start of a run and written to active-config.json, board.md and
grades.md, (b) stamped on every affected row as source_policy = 'non-official: <what>' with grade 'approx', so it can never
pass as official, and (c) covered by tests/test_rules.py.

LOCKED (no switch, ever): the honest User-Agent, no bypassing robots / Cloudflare / captchas / sign-in, no tokens found in
public web maps, no clicking through TLS warnings. A config file that tries to set them is refused."""
import copy, fnmatch, json, os, pathlib, re

HERE = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_FILE = HERE / 'config' / 'rules.json'
LOCKED = {
    'honest_user_agent': 'Every request names the engine and KPC_CONTACT. Never spoofed.',
    'no_bypass': 'Never get around robots.txt, Cloudflare / bot checks, captchas or sign-in walls. Blocked is not "not found".',
    'no_found_tokens': 'Never use an access token found inside a public web map. Token-only layers are "needs sign-in".',
    'tls_verified': 'Never click through or turn off certificate (TLS) checks.',
}
NEVER_USE = {   # source_policy.never_use.<name> -> what it matches in a link / layer text
    'openstreetmap': r'openstreetmap|overpass|geofabrik|\bosm\.org|\bosmfr\b',
    'google': r'google\.|googleapis\.com|goo\.gl',
    'alltrails': r'alltrails|gaiagps|strava',
    'wikidata': r'wikidata',
    'wikipedia': r'wikipedia|wikimedia',
    'tourism_app_pages': r'tripadvisor|yelp|visit[a-z]*\.(com|org)|tourism|travel\.|apps?\.apple|play\.google',
}
WDPA = r'wdpa|protected[\s_-]*planet|unep[\s_-]*wcmc|world database on protected areas'
# round 5: HDX (Humanitarian Data Exchange, data.humdata.org) protected-area datasets are WDPA copies -> same W-10 rule (never an
# ordinary source; last resort only, approx, labelled). The Mapping note says 'never WDPA (incl. HDX copies)': the user's newer
# W-10 (confirmed Nov 1) wins; the conflict is listed in TUNING.md and the round-5 report.
WDPA += r'|humdata\.org\S*(protected|wdpa|conservation[\s_-]*areas?|national[\s_-]*parks?)|\bhdx\b\S*\b(protected|wdpa)'


class RulesError(Exception):
    pass


def _load_defaults():
    return json.load(open(DEFAULT_FILE))


DEFAULTS = _load_defaults()
_cfg = copy.deepcopy(DEFAULTS)


LOCKED_WORDS = re.compile(r'user.?agent|\bua\b|tls|ssl|cert|verify|token|bypass|captcha|robots|cloudflare|sign.?in|login|cookie|spoof|'
                          + '|'.join(LOCKED), re.I)


def _check_locked(d, base=None, path=''):
    """Refuse any key naming a LOCKED safety rule, and any key that is not a known switch (old names are renamed)."""
    base = DEFAULTS if base is None else base
    for k in list((d or {}).keys()):
        new = RENAMED.get(path + k)
        if new and new.rsplit('.', 1)[0] + '.' == path: d[new.rsplit('.', 1)[1]] = d.pop(k)
    for k, v in (d or {}).items():
        if k == 'about': continue
        if LOCKED_WORDS.search(k): raise RulesError(f'{path}{k}: LOCKED safety rule, it has no switch')
        if not isinstance(base, dict) or k not in base: raise RulesError(f'unknown switch {path}{k!r}')
        if isinstance(v, dict): _check_locked(v, base[k], f'{path}{k}.')


def reset():
    global _cfg
    _cfg = copy.deepcopy(DEFAULTS)


def load(path=None, enable=(), disable=(), scope=(), set_=()):
    """Load the rules file (or env KPC_RULES) and apply command-line overrides. Returns the active config."""
    global _cfg
    p = path or os.environ.get('KPC_RULES')
    base = json.load(open(p)) if p else copy.deepcopy(DEFAULTS)
    _check_locked(base)
    _cfg = _merge(copy.deepcopy(DEFAULTS), base)
    for n in _split(enable): _set(n, True)
    for n in _split(disable): _set(n, False)
    for s in scope or ():
        k, _, v = s.partition('=')
        if k.strip() not in _cfg['plugins']: raise RulesError(f'--scope: unknown plug-in {k!r}')
        _cfg['plugins'][k.strip()]['areas'] = [x.strip() for x in v.split(',') if x.strip()]
    for s in set_ or ():
        k, _, v = s.partition('=')
        _set(k.strip(), float(v) if re.match(r'^-?\d+(\.\d+)?$', v.strip()) else v.strip())
    return _cfg


def _split(xs):
    out = []
    for x in xs or ():
        out += [y.strip() for y in str(x).split(',') if y.strip()]
    return out


def _merge(a, b):
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(a.get(k), dict): _merge(a[k], v)
        else: a[k] = v
    return a


RENAMED = {'checks.resolve_shared_facilities': 'checks.resolve_duplicate_facilities',      # round 4: never "shared"
           'grader.docs_shared_file_max': 'grader.docs_same_file_max'}


def _node(name):
    name = RENAMED.get(name, name)
    parts = name.split('.')
    if parts[0] in _cfg['plugins'] and len(parts) == 1: return _cfg['plugins'][parts[0]], 'enabled'
    d = _cfg
    for p in parts[:-1]:
        if not isinstance(d.get(p), dict): raise RulesError(f'unknown switch {name!r}')
        d = d[p]
    if parts[-1] not in d: raise RulesError(f'unknown switch {name!r}')
    return d, parts[-1]


def _set(name, v):
    if any(LOCKED_WORDS.search(p) for p in name.split('.')): raise RulesError(f'{name} is a LOCKED safety rule, it has no switch')
    d, k = _node(name)
    if isinstance(d[k], dict) and isinstance(v, bool):       # 'source_policy.never_use' false -> every item
        for kk in d[k]: d[k][kk] = v
    else:
        d[k] = v


def on(name):
    d, k = _node(name)
    return bool(d[k])


def num(name):
    d, k = _node('grader.' + name)
    return float(d[k])


def value(name):
    """Any switch's value by its full dotted name (v0.5.0: key_doctor.* lists and numbers)."""
    d, k = _node(name)
    return d[k]


def enabled(kind):
    p = _cfg['plugins'].get(kind)
    return bool(p and p.get('enabled'))


def areas(kind):
    return list((_cfg['plugins'].get(kind) or {}).get('areas') or [])


def area_ok(kind, area):
    area = area or ''
    return enabled(kind) and any(fnmatch.fnmatchcase(area, pat) or (pat == '*') for pat in areas(kind))


# ---------------------------------------------------------------- source policy
WDPA_LAST_RESORT = 'WDPA (last resort)'


def wdpa_last_resort_ok():
    """Club rule W-10 (Nov 1): with the WDPA guard on, WDPA is never an ordinary source; it may be asked only as a last
    resort (no official layer gave a usable record for the park), always g='approx' and labelled 'WDPA (last resort)'."""
    return on('source_policy.wdpa_guard') and on('source_policy.wdpa_last_resort')


def forbidden(text, allow_wdpa=False):
    """-> the name of an ON never-use / WDPA rule this link or layer text breaks, else ''. allow_wdpa: the W-10 last-resort path."""
    t = text or ''
    if on('source_policy.wdpa_guard') and not allow_wdpa and re.search(WDPA, t, re.I): return 'WDPA'
    for n, rx in NEVER_USE.items():
        if on(f'source_policy.never_use.{n}') and re.search(rx, t, re.I): return n
    return ''


def switched_off_hits(text):
    """-> names of OFF source rules this text would have broken (rows from them get stamped 'non-official: ...')."""
    t, out = text or '', []
    if not on('source_policy.wdpa_guard') and re.search(WDPA, t, re.I): out.append('WDPA')
    for n, rx in NEVER_USE.items():
        if not on(f'source_policy.never_use.{n}') and re.search(rx, t, re.I): out.append(n)
    return out


def _row_text(r):
    parts = [str(r.get(k) or '') for k in ('url', 'service_url', 'source_url', 'page', 'layer', 'agency', 'licence', 'record_link')]
    m = r.get('map'); parts.append(json.dumps(m) if isinstance(m, dict) else str(m or ''))
    for f in r.get('features') or []: parts += [str(f.get('record_link') or ''), str(f.get('source') or '')]
    return ' '.join(parts)


def stamp(r, why):
    """A row that only exists because a rule was switched off: never official, never STRONG, never 'found'. Idempotent."""
    tag = f'non-official: {why}'
    if tag not in (r.get('source_policy') or ''):
        r['source_policy'] = (r.get('source_policy') + '; ' if r.get('source_policy') else '') + tag
    r['grade'] = 'approx'; r['g'] = 'approx'
    if r.get('band') == 'STRONG': r['band'] = 'WEAK'
    if r.get('status') == 'found': r['status'] = 'candidate'
    return r


def stamp_rows(kind, rows):
    """Called on every plug-in's final rows (and by `grade`). Stamps rows touched by a switched-off rule."""
    n = 0
    for r in rows:
        if not isinstance(r, dict) or r.get('status') not in ('found', 'candidate'): continue
        hits = switched_off_hits(_row_text(r))
        if kind == 'outline' and not on('source_policy.eu_compilation_approximate') and (r.get('basis_note') == 'EU compilation' or re.search(r'eea\.europa\.eu|discomap', _row_text(r), re.I)):
            hits.append('EU compilation (approximate rule off)')
        if kind == 'outline' and not on('source_policy.parcels_approximate') and r.get('parcel_record') is not None:
            hits.append('parcel (approximate rule off)')
        if kind == 'docs' and not on('source_policy.unofficial_docs_kept_apart'):
            from core.agencies import official_domain
            import urllib.parse as up
            links = [r.get('page') or ''] + [(r['map'].get('url') if isinstance(r.get('map'), dict) else r.get('map')) or '']
            if any(u and not official_domain(up.urlsplit(u).netloc) for u in links): hits.append('unofficial doc (kept-apart rule off)')
        if hits: stamp(r, ', '.join(dict.fromkeys(hits))); n += 1
    return n


# ---------------------------------------------------------------- reporting
def changed(cfg=None, base=None, prefix=''):
    cfg = _cfg if cfg is None else cfg; base = DEFAULTS if base is None else base
    out = []
    for k, v in cfg.items():
        if k == 'about': continue
        b = base.get(k) if isinstance(base, dict) else None
        if isinstance(v, dict): out += changed(v, b or {}, f'{prefix}{k}.')
        elif v != b: out.append((f'{prefix}{k}', b, v))
    return out


def active_summary():
    return {'rules_file': os.environ.get('KPC_RULES') or str(DEFAULT_FILE.relative_to(HERE)),
            'changed_from_default': [{'switch': n, 'default': d, 'now': v} for n, d, v in changed()],
            'scope': {k: (areas(k) if enabled(k) else 'OFF') for k in _cfg['plugins']},
            'locked': list(LOCKED), 'active': {k: v for k, v in _cfg.items() if k != 'about'}}


def banner_md():
    ch = changed()
    if not ch: return '> Rules: all club defaults (config/rules.json). Locked safety rules: ' + ', '.join(LOCKED) + '.\n\n'
    L = ['> **WARNING: RULES CHANGED FROM THE CLUB DEFAULTS FOR THIS RUN.** Rows touched by a switched-off source rule are '
         'stamped `source_policy: non-official: ...` and graded approx; none can pass as official.', '>']
    L += [f'> - `{n}`: default **{d}**, now **{v}**' for n, d, v in ch]
    return '\n'.join(L) + '\n\n'


def banner_text():
    ch = changed()
    if not ch: return 'rules: club defaults (config/rules.json)'
    return '!' * 72 + '\n!! RULES CHANGED FROM THE CLUB DEFAULTS:\n' + '\n'.join(f'!!   {n}: default {d} -> now {v}' for n, d, v in ch) + '\n' + '!' * 72


def write_active(out_dir):
    p = pathlib.Path(out_dir); p.mkdir(parents=True, exist_ok=True)
    json.dump(active_summary(), open(p / 'active-config.json', 'w'), indent=1)
