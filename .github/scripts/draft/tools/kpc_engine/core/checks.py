"""Quality checks (PART 3.8, method §6) run on every plug-in's final rows before they are written:
  - every URL written opens (a cached polite GET; HEAD is not trusted by many agency servers);
  - identity columns (ref, park name, area) are compared with the club's files: 0 mismatches allowed;
  - boilerplate / other-site text is caught (the same text on many parks, cookie banners, 'page not found');
  - 20 random rows go in spot-check.md for chat 11."""
import json, random, re

BOILER = re.compile(r'(page not found|404 error|access denied|we use cookies|cookie (policy|settings)|javascript (is )?(required|disabled)|'
                    r'enable javascript|sign in to continue|skip to main content|this site can.t be reached|captcha)', re.I)
URL_KEYS = ('url', 'page', 'map', 'map_page', 'source_url', 'record_link', 'booking')


def urls_in(row):
    out = []
    for k, v in row.items():
        if k in URL_KEYS and isinstance(v, str) and v.startswith('http'): out.append((k, v))
        elif isinstance(v, dict) and k in ('map', 'page'):
            u = v.get('url')
            if isinstance(u, str) and u.startswith('http'): out.append((k, u))
    return out


def url_opens(P, u, ref_=''):
    r = P.get(u, ref_=ref_, kind='check', ttl_days=7, rng=(0, 65535))
    if r.blocked: return None, r.blocked          # unknown: blocked is not 'dead'
    return r.status in (200, 206), f'HTTP {r.status}'


def check_rows(P, rows, club_parks, text_keys=('text', 'hours', 'fees', 'notice'), check_urls=True):
    """Returns (rows kept, problems). Rows with a dead URL or an identity mismatch are dropped into problems, never written."""
    kept, problems, seen_text = [], [], {}
    for r in rows:
        for k in text_keys:
            v = r.get(k)
            if isinstance(v, str) and len(v) > 40: seen_text.setdefault(v.strip()[:200], []).append(r.get('ref'))
    common = {t for t, refs in seen_text.items() if len(set(refs)) >= 5}
    for r in rows:
        why = []
        p = (club_parks.get(r.get('area')) or {}).get(r.get('ref'))
        if p is None: why.append('identity: ref not in the club park list')
        elif r.get('park') and p.get('n') and r['park'] != p['n']: why.append(f"identity: park name '{r['park']}' != club '{p['n']}'")
        for k in text_keys:
            v = r.get(k)
            if isinstance(v, str) and (BOILER.search(v) or v.strip()[:200] in common): why.append(f'boilerplate in {k}')
        if check_urls and not why:
            for k, u in urls_in(r):
                ok, how = url_opens(P, u, r.get('ref', ''))
                if ok is False: why.append(f'{k} does not open ({how})')
                elif ok is None: r.setdefault('url_check', {})[k] = f'not checked: {how}'
        (problems if why else kept).append({**r, 'check_problem': why} if why else r)
    return kept, problems


def spot_check(rows, path, kind, n=20, seed=11):
    pool = [r for r in rows if r.get('status') in ('found', 'candidate')] or rows
    pick = random.Random(seed).sample(pool, min(n, len(pool)))
    L = [f'# Spot check: {kind} ({len(pick)} random rows of {len(rows)})', '',
         'For chat 11: open each link and say YES / NO. The engine decides nothing.', '']
    for r in pick:
        L.append(f"## {r.get('ref')} {r.get('park', '')} ({r.get('area')})")
        for k in ('status', 'tier', 'band', 'record_name', 'url', 'record_link', 'page', 'source_url', 'label', 'pin_m'):
            if r.get(k) not in (None, ''): L.append(f'- {k}: {r[k] if not isinstance(r[k], dict) else json.dumps(r[k], ensure_ascii=False)}')
        n_ = r.get('notes') or {}
        if n_: L.append(f"- why: {n_.get('why_this_record', '')}; confidence: {(n_.get('confidence') or {}).get('level')}")
        L += ['- answer: ', '']
    open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
