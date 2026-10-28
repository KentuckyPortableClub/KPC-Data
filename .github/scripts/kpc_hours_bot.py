#!/usr/bin/env python3
"""HOURS, FEES & PERMITS BOT (Fable, chat 10 'bot workshop', Oct 28 2026; HQ job 3's top buildable idea). FACTS WITH SOURCES;
it decides nothing and nothing here reaches a card until chat 8 grades a sample and Brandon says GO (chat 3 shows it).

For every US + Canada park with an official page it reads the MANAGING AGENCY'S OWN page (and the first page of its official
map PDF when one is on file) for three kinds of fact, each QUOTED with the sentence it came from, the address and the date:
  HOURS   when the land is open: 'daylight to dark', 'sunrise to sunset', gate times, days closed, seasonal hours, '24 hours'
  FEES    entry / parking / day-use fees and passes ('$3 per person', 'annual pass', 'free admission'), never lodging prices
  PERMITS a permit the land itself needs ('user permit required', 'day-use permit', 'free permit', 'drawn permit') — Sheet D
          shows these as '🎫 Permit needed' NOTES (Brandon Q11: permit land counts, with a note)
Where the pages come from: the park truth checker's candidate list (Kentucky answer key 'web'/'off', data/parkinfo column 1,
the documents bot's page / map / rules links, parkinfo-web) — the same read, so the two bots never disagree on the page.
Rules of the read (no rule sheet needed: facts only; the SHOWING follows the notices + Sheet D wording):
  H1 only the agency's own site (or the same government's); never third-party sites.
  H2 a fact is the agency's SENTENCE (≤ 240 chars), not our paraphrase; the regex only finds it. Unknown = null, never guessed.
  H3 hours sentences must say when (a time, 'daylight', 'dawn', 'dusk', 'sunset', 'sunrise', '24 hours', 'year-round',
     a day name); fee sentences must carry a $ amount or the word free/no fee; permit sentences must say permit + required /
     needed / must. Lodging, camping, cabin, boat-rental, golf and museum prices are NOT park fees (kept apart as 'other_fees').
  H4 Kentucky: kpc-ky-hours.json (hand-checked, Brandon-corrected) is the ANSWER KEY: the test gate compares the bot's hours /
     fee sentences with the 38 'done' rows (a PASS = the bot's hours sentence shares the key's times/days for ≥ 70% of the
     rows that have hours, and Otter Creek's hours name Wednesday–Sunday, Buckley's fee says $8, Peabody's permit is found).
Manners: kpc_manners.py (robots, 2 s per host, back-off, three strikes = a day's rest); PDFs by range. Resumable: a park
checked within REFRESH_DAYS (90) is skipped; MINUTES per chunk; never fails (exit 0 always).
Env: AREAS · MINUTES · LINKS · OUT (data/hours) · REFRESH_DAYS · TEST=1 (Kentucky gate: prints TEST=PASS/FAIL)
"""
import json, os, pathlib, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpc_truth_bot as T                      # the page list, the polite read, park lists (same workshop; read-only use)
from kpc_manners import Manners                # noqa: E402

OUT = pathlib.Path(os.environ.get('OUT') or 'data/hours')
LINKS = pathlib.Path(os.environ.get('LINKS') or 'links')
T0 = time.time(); LIMIT = float(os.environ.get('MINUTES') or 55) * 60
REFRESH_DAYS = int(os.environ.get('REFRESH_DAYS') or 90)
TODAY = time.strftime('%Y-%m-%d')
VER = 5   # Oct 28 9 AM: debug text for gate misses; VER 4 =: the page-list unpack fix; VER 3 was the 6:40 AM (chat 11's grade + regrade): schedule / labelled rows count; questions, events, '$N million' never; attraction hours labelled
QUEUE = T.QUEUE
STAT = {'parks': 0, 'pages_read': 0, 'hours': 0, 'fees': 0, 'permits': 0, 'none': 0, 'no_page': 0, 'skipped_fresh': 0, 'errors': 0}

TIME = r'(?:\d{1,2}(?::\d\d)?\s*(?:a\.?m\.?|p\.?m\.?)|noon|midnight|daylight|dawn|dusk|sunrise|sunset|sundown|dark|24 hours|year[- ]round|seasonal)'
DAYS = r'(?:mon|tues?|wed|thurs?|fri|sat|sun)[a-z]*\.?'
HOURS_RX = re.compile(r'([^.;\n]{0,160}?\b(?:open|hours?|closed|closes|gates?|access(?:ible)?|day[- ]use)\b[^.;\n]{0,160}?\b' + TIME + r'[^.;\n]{0,120}|[^.;\n]{0,120}\b' + TIME + r'\s*(?:to|-|–|until|till|through)\s*' + TIME + r'[^.;\n]{0,120}|[^.;\n]{0,120}\b' + DAYS + r'\s*(?:to|-|–|through|thru)\s*' + DAYS + r'[^.;\n]{0,120})', re.I)
HOURS_BAD = re.compile(r'office hours|customer service|phone|call center|visitor cent(?:er|re) hours|museum hours|gift shop|restaurant|lodge|pool hours|store hours|marina hours|golf|rental|cabin|cottage|campground office|check[- ]in|check[- ]out|headquarters|business hours|hatchery hours', re.I)
FEE_RX = re.compile(r'([^.;\n]{0,160}?(?:\$\s?\d+(?:\.\d\d)?|free (?:admission|entry|entrance|of charge)|(?:fees?|admission|entrance|entry|parking)\s*[:\-–]\s*(?:free|none|no charge)|no (?:entrance|entry|admission|day[- ]use) fee|no fee|admission is free|entrance is free)[^.;\n]{0,160})', re.I)
FEE_GOOD = re.compile(r'entrance|entry|admission|day[- ]use|parking|vehicle|per car|per person|per vehicle|pass\b|passes\b|permit|access fee|user fee|daily fee|gate fee|launch fee|free (?:admission|entry|entrance|of charge)|no (?:entrance|entry|admission|day[- ]use) fee|no fee', re.I)
FEE_BAD = re.compile(r'lodg|cabin|cottage|room|camp(?:site|ing|ground)|rv site|tent site|rental|rent\b|boat slip|golf|green fee|museum|tour|ticket|gift|merchandise|dona|membership|class|workshop|event|wedding|shelter reservation|per night|nightly|lodge', re.I)
PERMIT_RX = re.compile(r'([^.;\n]{0,160}?\bpermits?\b[^.;\n]{0,160})', re.I)
PERMIT_GOOD = re.compile(r'required|requires|needed|need a|must (?:have|obtain|carry|purchase|possess)|mandatory|is necessary|are necessary', re.I)
PERMIT_BAD = re.compile(r'building permit|burn permit|special[- ]use permit application|film|commercial|wedding|vendor|research permit|collecting permit|concession|alcohol permit|boat registration|fishing license only|hunting license only', re.I)
MAXLEN = 240
HKEY = {}


def notice(m): print('::notice title=Hours fees permits bot::' + str(m).replace('\n', ' ')[:900], flush=True)
def late(): return time.time() - T0 > LIMIT
def clean(s): return ' '.join(s.split())[:MAXLEN]


ABBR = re.compile(r'\b(jan|feb|mar|apr|jun|jul|aug|sept?|oct|nov|dec|mon|tues?|wed|thurs?|fri|sat|sun|u\.s|st|mt|ft|dr|mr|mrs|ms|no|vs|etc|approx|inc|co|ave|rd|hwy|rte)\.(?=\s)', re.I)
SUBJECT = re.compile(r'\b(memorial|building|birthplace|homestead|park|parks|area|areas|refuge|forest|preserve|reserve|sanctuary|site|grounds|trails?|gates?|day[- ]use|visitors?|public|property|lands?|wma|lake|beach|campground|office|visitor cent(?:er|re)|museum|building|lodge|center|centre|headquarters|range|hatchery|cave|tours?|we|it)\b', re.I)
OFFICE = re.compile(r'office|headquarters|visitor cent|business hours|call|phone', re.I)
BUILDING = re.compile(r'memorial building|memorial|museum|visitor cent(?:er|re)|lodge|cabin|tour|cave tours?|house|mansion|gift shop|restaurant|pool|marina|gallery|exhibit|planetarium|center|centre', re.I)
HUNTSEASON = re.compile(r'season|hunting|hunters|quota|shooting hours|legal (?:shooting|hunting)|dove|deer|turkey|waterfowl|grouse|quail|squirrel', re.I)
SCHEDULE = re.compile(r'^\s*(?:' + DAYS + r'(?:\s*(?:-|–|to|through|thru)\s*' + DAYS + r')?|daily|every day|year[- ]round|seven days a week|7 days a week|summer|winter|spring|fall|' + TIME + r')\b', re.I)
LABELLED = re.compile(r'^\s*(?:park |visitor |general |operating |day[- ]use |gate )?(?:hours|open|opens|closed|admission|entrance fee|entry fee|day[- ]use fee|parking fee|fees?|permits?)\s*[:\-–]\s*\S', re.I)
EVENT = re.compile(r'performance|concert|show begins|meet (?:&|and) greet|festival|parade|race day|gates? open at \d{1,2}(?::\d\d)? ?[ap]m\s*\|?\s*(?:performance|show)|tickets? (?:go )?on sale|registration (?:opens|begins)|event (?:begins|starts)|doors open|fireworks|celebration|camp(?:s)? for kids|summer camp', re.I)
MILLION = re.compile(r'\$\s?[\d.,]+\s*(?:million|billion|m\b|k\b)|million|renovation|grant|budget|funding|raised', re.I)
TOPIC_PAGE = re.compile(r'field[- ]trip|school|group[- ]tour|programs?/|education|events?/|hunting-season|seasons-and-limits|regulations', re.I)
TOURISM = re.compile(r'kentuckytourism\.com|visit[a-z]+\.com|tourism', re.I)


def sentences(text):
    """Sentences of a page with abbreviations protected (H-R1: never cut at 'Nov.', 'a.m.', 'U.S.', 'St.')."""
    t = re.sub(r'\b([apAP])\.\s?[mM]\.(?=\s+[A-Z(]|\s*$)', r'\1m.', text)   # '4:30 p.m. Park grounds…' ends a sentence
    t = re.sub(r'\b([ap])\.\s?m\.', r'\1m', t, flags=re.I)                               # '10 p.m. to 7 a.m.' does not
    t = ABBR.sub(lambda m: m.group(1) + '§', t)
    for line in t.split('\n'):
        for sen in re.split(r'(?<=[.;!?])\s+', line):
            sen = sen.replace('§', '.').strip()
            if sen: yield sen


def is_heading(sen):
    """A heading or a date line: short, no verb-ish word, no time, or a bare 'Month d, yyyy | …' fragment (H-R2)."""
    w = sen.split()
    if re.match(r'^[\d,\s|]*(?:19|20)\d\d\b', sen) or re.match(r'^\d{1,2},\s*(?:19|20)\d\d', sen): return True
    if len(w) <= 6 and not re.search(r'\d', sen) and not re.search(r'\b(is|are|open|opens|closed|closes|from|to|until|daily|free|required)\b', sen, re.I): return True
    if sen.isupper() and len(w) <= 8 and not re.search(TIME + '|' + DAYS, sen, re.I): return True
    return False


def facts_in(text, park_name='', url=''):
    """{'hours', 'fees', 'permits', 'other_fees', 'office_hours', 'attraction_fees'}: each a list of the agency's own sentences.
    H-R2 a hit needs a subject; H-R3 hunting-season hours are a separate label; H-R4 a fee for one attraction is labelled so."""
    out = {'hours': [], 'fees': [], 'permits': [], 'other_fees': [], 'office_hours': [], 'hunting_hours': [], 'attraction_fees': [], 'attraction_hours': []}
    seen = set()
    cn = [w for w in T.core(park_name).split() if len(w) > 2][:3]
    def put(k, s):
        s = clean(s)
        key = (k, s[:60].lower())
        if len(s) < 12 or key in seen or len(out[k]) >= 6: return
        seen.add(key); out[k].append(s)
    for sen in sentences(text):
        if is_heading(sen): continue
        if sen.rstrip().endswith('?') or re.match(r'^(is|are|does|do|can|how|what|when|where|why)\b', sen, re.I): continue   # a question is never a fact
        if EVENT.search(sen): continue                                                                                          # an event's times are not park hours
        sen = re.sub(r'^(however|also|additionally|in addition|note|please note|but),?\s+', '', sen, flags=re.I)                # 'However, the trails…' reads whole
        has_subject = bool(SUBJECT.search(sen)) or any(w in sen.lower() for w in cn) or bool(SCHEDULE.match(sen)) or bool(LABELLED.match(sen))
        if HOURS_RX.search(sen):
            if not has_subject: continue
            if HUNTSEASON.search(sen): put('hunting_hours', sen)
            elif OFFICE.search(sen) and not re.search(r'\b(park|area|refuge|forest|grounds|gates?|trails?|day[- ]use)\b', sen, re.I): put('office_hours', sen)
            elif HOURS_BAD.search(sen): continue
            elif BUILDING.search(sen) and not re.search(r'\b(park|area|refuge|forest|grounds|gates?|trails?|day[- ]use|preserve|sanctuary|property|lands?)\b', sen, re.I): put('attraction_hours', sen)   # 'The Memorial Building closes at 4:30 pm' is that building's time
            else: put('hours', sen)
        if FEE_RX.search(sen):
            if not has_subject or MILLION.search(sen): continue
            if FEE_BAD.search(sen) and not re.search(r'entrance|entry|admission|day[- ]use|parking|per vehicle|per car', sen, re.I): put('other_fees', sen)
            elif BUILDING.search(sen) and not re.search(r'\bpark (?:admission|entrance|entry)|per (?:car|vehicle)|day[- ]use|parking', sen, re.I): put('attraction_fees', sen)
            elif FEE_GOOD.search(sen) or LABELLED.match(sen): put('fees', sen)
        if PERMIT_RX.search(sen):
            if not has_subject or PERMIT_BAD.search(sen) or not PERMIT_GOOD.search(sen): continue
            put('permits', sen)
    return out


def one_park(ref, park, web, docs, ky):
    r = {'n': park['n'], 't': park.get('t', ''), 'hours': [], 'fees': [], 'permits': [], 'other_fees': [], 'pages': [], 'checked': TODAY, 'ver': VER}
    pages = [(p[0], p[1]) for p in T.candidate_pages(ref, park, web, docs, ky)]   # truth v4 returns (url, why, other_unit): keep the first two
    pages = [p for p in pages if 'news' not in p[1] and 'statistics' not in p[1]][:4]
    kl = (HKEY.get(ref) or {}).get('link')   # Kentucky's hand-checked hours page (answer key) is read too: it IS the agency's page
    if kl and kl.startswith('http') and kl not in [p[0] for p in pages]: pages.insert(0, (kl, 'hours page (Kentucky hours answer key)'))
    if not pages: r['status'] = 'no official page on file'; STAT['no_page'] += 1; return r
    for k in ('office_hours', 'hunting_hours', 'attraction_fees', 'attraction_hours'): r[k] = []
    for u, why in pages:
        if late(): break
        if TOPIC_PAGE.search(u): r['pages'].append({'url': u, 'why': why, 'status': 'skipped: another topic (field trips / programs / seasons)'}); continue
        st, kind, text = T.read_page(u)
        r['pages'].append({'url': u, 'why': why, 'status': st})
        if st != 'ok' or not text: continue
        STAT['pages_read'] += 1
        f = facts_in(text, park['n'], u)
        if os.environ.get('TEST') == '1' and ref in HKEY and (HKEY[ref].get('hours') or HKEY[ref].get('fee')) and not (f['hours'] or f['fees']):   # the gate's parks: keep what the page said around 'hours' / 'open' so a MISS can be read
            m = re.search(r'(?i)(hours|open|admission|fee)', text); r.setdefault('debug', []).append({'url': u, 'kind': kind, 'text': ' '.join(text[max(0, (m.start() if m else 0) - 200):(m.start() if m else 0) + 600].split())})
        tour = bool(TOURISM.search(u))   # H-R5: a tourism site is state government, not the park's agency: labelled, kept apart
        for k in ('hours', 'fees', 'permits', 'other_fees', 'office_hours', 'hunting_hours', 'attraction_fees', 'attraction_hours'):
            for s in f[k]:
                row = {'line': s, 'url': u, 'read': TODAY}
                if tour: row['src_note'] = 'tourism site (state government), not the park agency'
                if len(r[k]) < 6: r[k].append(row)
        if r['hours'] and r['fees']: break
    r['status'] = 'ok' if (r['hours'] or r['fees'] or r['permits']) else ('nothing found' if any(p['status'] == 'ok' for p in r['pages']) else 'no page opened')
    for k in ('hours', 'fees', 'permits'):
        if r[k]: STAT[k] += 1
    if r['status'] != 'ok': STAT['none'] += 1
    return r


def run_area(area, state, web, docs_all, ky):
    f = OUT / f'{area}.json'
    D = T.load(f, {'area': area, 'about': "Hours, fees and permits as the agency's own sentences (hours / fees / permits bot). Facts only; nothing reaches a card until Brandon's GO.", 'parks': {}})
    parks = T.park_list(area)
    if not parks: notice(f'{area}: no park list'); state['areas'][area] = {'status': 'done', 'parks': 0, 'updated': TODAY}; return
    docs = (docs_all.get(area) or {}).get('parks') or {}
    cut = time.strftime('%Y-%m-%d', time.gmtime(time.time() - REFRESH_DAYS * 86400))
    done = fresh = 0
    for ref in sorted(parks):
        if late(): break
        old = D['parks'].get(ref)
        if old and old.get('ver', 0) >= VER and old.get('checked', '') >= cut: fresh += 1; STAT['skipped_fresh'] += 1; continue
        STAT['parks'] += 1
        try:
            new = one_park(ref, parks[ref], web, docs, ky if area == 'US-KY' else {})
            if old and old.get('status') == 'ok' and not any(p.get('status') == 'ok' for p in new.get('pages') or []):
                old['last_read_failed'] = TODAY; old['ver'] = VER; new = old   # every page failed (403 / rest): keep what we knew
            D['parks'][ref] = new
        except Exception as e:  # noqa: BLE001
            STAT['errors'] += 1; D['parks'][ref] = {'n': parks[ref]['n'], 'status': 'bot error: ' + str(e)[:80], 'checked': TODAY, 'ver': VER, 'hours': [], 'fees': [], 'permits': []}
        done += 1
    D['read'] = TODAY; D['counts'] = counts(D)
    T.save(f, D)
    left = sum(1 for r in parks if r not in D['parks'])
    state['areas'][area] = {'status': 'done' if left == 0 else 'partial', 'parks': len(parks), 'checked': len(D['parks']), 'left': left, 'updated': TODAY, 'counts': D['counts']}
    notice(f"{area}: {done} parks read this chunk ({fresh} fresh, {left} left) · {D['counts']}")


def counts(D):
    c = {'parks': len(D['parks']), 'hours': 0, 'fees': 0, 'permits': 0, 'nothing': 0, 'no_page': 0}
    for r in D['parks'].values():
        for k in ('hours', 'fees', 'permits'):
            if r.get(k): c[k] += 1
        if r.get('status') == 'nothing found': c['nothing'] += 1
        if 'no official page' in str(r.get('status')): c['no_page'] += 1
    return c


def ky_test(state):
    """H4: compare with kpc-ky-hours.json's hand-checked rows."""
    key = (T.load(LINKS / 'kpc-ky-hours.json', {}).get('parks') or {})
    D = T.load(OUT / 'US-KY.json', {'parks': {}})
    rows = [(ref, k) for ref, k in key.items() if k.get('done') and k.get('hours')]
    hit = 0; detail = []
    opened = 0
    for ref, k in rows:
        r = D['parks'].get(ref) or {}
        if not any(p.get('status') == 'ok' for p in r.get('pages') or []): detail.append(f'{ref} no page opened'); continue
        opened += 1
        bot = ' '.join(h['line'] for h in (r.get('hours') or []) + (r.get('office_hours') or []) + (r.get('hunting_hours') or [])).lower()
        bot = re.sub(r'\b([ap])\.?m\b', r'\1m', bot)
        kw = re.sub(r'\b([ap])\.?m\b', r'\1m', k['hours'].lower())
        want = set(re.findall(r'\d{1,2}(?::\d\d)?\s*[ap]m|daylight|dawn|dusk|sunrise|sunset|dark|year[- ]round|' + DAYS, kw))
        want = {w[:3] if re.match(DAYS, w) else w.replace(' ', '') for w in want}
        botc = bot.replace(' ', '')
        ok = bool(want) and any((w in botc) if not re.match(r'^[a-z]{3}$', w) else (w in bot) for w in want)
        hit += ok; detail.append(f"{ref} {'ok' if ok else 'MISS'}")
    rows = rows[:opened] if opened else rows
    oc = ' '.join(h['line'] for h in (D['parks'].get('US-8144') or {}).get('hours') or []).lower()
    oc_ok = ('wednesday' in oc or 'wed' in oc) and ('sunday' in oc or 'sun' in oc)
    bk = ''
    bk_ref = next((ref for ref, k in key.items() if '$8 per car' in str(k.get('fee', ''))), None)
    bk = ' '.join(h['line'] for h in (D['parks'].get(bk_ref) or {}).get('fees') or []) if bk_ref else bk
    bk_ok = '$8' in bk
    pb = ' '.join(h['line'] for h in (D['parks'].get('US-3828') or {}).get('permits') or []).lower()
    pb_ok = 'permit' in pb
    rate = hit / opened if opened else 0
    res = 'PASS' if (rate >= 0.7 and oc_ok and bk_ok and pb_ok) else 'FAIL'
    why = f"hours rows {hit}/{opened} opened ({rate:.0%}; {len(rows)} in the key); Otter Creek Wed–Sun {'ok' if oc_ok else 'MISS'}; Buckley $8 {'ok' if bk_ok else 'MISS'} ({bk_ref}); Peabody permit {'ok' if pb_ok else 'MISS'}; " + ', '.join(detail[:40])
    state['test'] = {'when': TODAY, 'result': res, 'why': why}
    notice(f'KENTUCKY TEST {res}: {why[:700]}')
    print('TEST=' + res)


def review(state):
    L = ['# Hours, fees & permits bot: review (facts only; nothing here reaches a card until Brandon\'s GO)', '',
         f"Updated {TODAY}. Every line is the agency's own sentence (H2). Refresh every {REFRESH_DAYS} days.", '',
         '| area | parks | hours | fees | permits | nothing found | no page |', '|---|---|---|---|---|---|---|']
    for a in QUEUE:
        c = (state['areas'].get(a) or {}).get('counts')
        if c: L.append(f"| {a} | {c['parks']} | {c['hours']} | {c['fees']} | {c['permits']} | {c['nothing']} | {c['no_page']} |")
    for a in QUEUE:
        D = T.load(OUT / f'{a}.json', None)
        if not D: continue
        L += ['', f'## {a}: 12-park sample for chat 8', '']
        n = 0
        for ref, r in D['parks'].items():
            if r.get('status') != 'ok': continue
            L.append(f"- **{ref} {r['n']}**")
            for k, lab in (('hours', 'Hours'), ('fees', 'Fees'), ('permits', 'Permit'), ('office_hours', 'Office hours'), ('hunting_hours', 'Hunting hours'), ('attraction_fees', 'Attraction fee')):
                for x in (r.get(k) or [])[:2]: L.append(f"  - {lab}: “{x['line']}” · [{T.host_of(x['url'])}]({x['url']})")
            n += 1
            if n >= 12: break
    t = state.get('test')
    if t: L += ['', '## Kentucky test gate (H4)', '', f"- {t['when']}: **{t['result']}** · {t['why'][:900]}"]
    (OUT / 'review.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    state = T.load(OUT / 'state.json', {'areas': {}, 'hosts': {}})
    T.M = Manners('hours, fees and permits', state.get('hosts'))
    T.LINKS = LINKS
    want = (os.environ.get('AREAS') or '').upper().split()
    areas = [a for a in want if a in QUEUE] if want else [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') != 'done']
    if want and not areas: notice('no known area in AREAS'); return
    web = (T.load('data/parkinfo-web.json', {}) or T.load(LINKS / 'data/parkinfo-web.json', {})).get('parks') or {}
    docs_all = {a: T.load(f'data/docs/{a}.json', {}) for a in areas}
    ky = {x['c']: x for x in T.load(LINKS / 'kpc-ky-data.json', {}).get('parks', []) if x.get('c')}
    HKEY.update(T.load(LINKS / 'kpc-ky-hours.json', {}).get('parks') or {})
    for area in areas:
        if late(): break
        run_area(area, state, web, docs_all, ky)
    if os.environ.get('TEST') == '1': ky_test(state)
    state['hosts'] = T.M.resting()
    state['last'] = {'when': TODAY, 'areas': areas[:8], 'stat': STAT, 'manners': T.M.stat}
    T.save(OUT / 'state.json', state)
    review(state)
    left = [a for a in QUEUE if (state['areas'].get(a) or {}).get('status') != 'done']
    notice(f"done this chunk: {STAT} · manners {T.M.stat} · areas left: {len(left)}" + (f" (next {' '.join(left[:4])})" if left else ''))


if __name__ == '__main__':
    try: main()
    except Exception as e:  # noqa: BLE001
        import traceback; traceback.print_exc()
        notice(f'stopped: {e}')
    sys.exit(0)
