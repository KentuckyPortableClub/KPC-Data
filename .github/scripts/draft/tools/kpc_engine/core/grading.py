"""One grade report per kind, in the shape chat 11 grades in (club, Nov 1):
  verdict (PASS / FAIL against the bar in the instructions, or NEEDS CHAT 11 when the bar needs a person or a side-by-side run),
  the bar, what was measured, the top reasons for misses, and 5 example parks.
The bars come from KPC_10_Engine_Spec.md (Acceptance) and KPC_10_Finder3_Spec.md (Acceptance). The engine still decides
nothing: this is a self-check for chat 11 to read, not a YES."""
import collections, re
from core import rules

HIT = ('found', 'candidate')
BARS = {   # chat 11's bars (GRADING_BAR_chat11.md, Nov 1) + the engine spec's "finds more" bars
    'outline': 'Rule G: SURE only when pin inside (or <= 150 m with a name match, R-G12), names equal once kind words are stripped, '
               'kinds match, not line vs polygon, not a container, size within 1.5x or unknown; LIKELY goes to chat 11; UNLIKELY is '
               'evidence only, never a question. Whole key file: chat 11 samples 30 joins, needs 30/30. Finder: >= 95% of past YES '
               're-found, >= 25% more parks, >= 85% YES in a sample of 40; every open park has a why-not.',
    'docs': 'Each link opens (HTTP 200), names the park, is not one file used by more than 3 parks, is not a sign / logo / letterhead, '
            'never replaces a map marked status: ok, is never Wikipedia / tourism / app. Engine: a page or map for >= 20% of the missing KY + TN parks.',
    'parking': 'Chat 11 samples about 30 points: 27-28/30 right, with 0 on the wrong park, 0 west longitudes written as positive, '
               '0 duplicate facilities (one facility listed under 2+ parks), no wilderness / office / hotel / road-number labels. Engine: new points in >= 10% of the KY + TN parks without any.',
    'camping': 'Campinfo: about 97% of sampled facts match the agency page; a fact from another business (golf, marina, pool, picnic '
               'shelter) is a FAIL row. Camp layers: >= 95% of kept features really campgrounds, 0 picnic shelters, 0 boat ramps.',
    'trail': "Club trail bar (Nov 1, round 4): a trail passes when it is the managing agency's own line, its name matches the trail, and "
             'the POTA pin is within 200 m of it (grader.trail_pin_m). National historic trails the agency marks approximate stay approximate. '
             'A trail inside two parks is "Overlapping boundaries", not a failure: it goes to the 2-fer / 3-fer waiting room. Plus the '
             'point rules: no positive west longitudes, no bad labels.',
    'hours': 'Kentucky only. A 12-row sample, 12/12 to pass: no marina / scuba hours as park hours, no bare "10 AM - 4 PM" fragments, '
             'no "Open seasonally" under hunting hours; every value word for word from an official page.',
    'fees': 'Kentucky only. A 12-row sample, 12/12 to pass (same rules as hours); word for word from an official page.',
    'closures': 'Kentucky only; word for word from an official page.',
    '2fers': 'Never automatic: chat 8 + chat 11 by hand. Label "Overlapping boundaries". Overlap patch >= 50 yards; parks that only touch '
             "do not count; a trail with no land boundary counts within 100 ft of its line (water trails: 100 ft of the water's edge); a "
             'wild / scenic river corridor uses its own boundary (no 100 ft rule); a trail inside an overlap patch can make a 3-fer when a spot '
             'within 100 ft of the trail sits in the patch.',
}
def bar(kind):
    """The bar text, with the club's switches applied (2-fers never automatic unless switched off)."""
    if kind == '2fers' and not rules.on('source_policy.two_fers_never_auto'):
        return ('SWITCHED OFF (club): the grader may auto-suggest 2-fers, but every suggestion still goes to the waiting room for '
                'chat 8 + chat 11; nothing is written as a 2-fer automatically. (No 2-fer finder is built yet: stub.)')
    return BARS.get(kind, '')


BAD_PUB = re.compile(r'openstreetmap|overpass|geofabrik|protectedplanet|wdpa|unep-wcmc|google\.|wikipedia|wikidata|alltrails|gaia|strava|tripadvisor|yelp', re.I)


def _reason(r):
    if r.get('error') and not r.get('status'): return 'engine error: ' + str(r['error']).split(':')[0]
    st = r.get('status') or 'no status'
    w0 = r.get('whynot'); t0 = str((w0.get('tag') if isinstance(w0, dict) else w0) or '')
    if st == 'blocked':      # group refusals by their kind, not by the park
        m = re.search(r'offline|robots|403|401|429|TLS|certificate|token|sign-in|host resting|timeout|captcha|5\d\d|refused', t0, re.I)
        return f"blocked: {m.group(0).lower() if m else 'source could not be read'}"
    if st in HIT: return None
    w = r.get('whynot')
    tag = (w.get('tag') if isinstance(w, dict) else w) or r.get('why') or r.get('reason') or st
    tag = re.sub(r'\(.*?\)|\'[^\']*\'|"[^"]*"|https?://\S+|\b[A-Z]{2}-\d{4,5}\b|\d+(\.\d+)?', '', str(tag))   # drop the park-specific bits
    return f"{st}: {re.sub(r'\s+', ' ', tag).strip(' :;,-')[:90]}"


def _example(r):
    return {'ref': r.get('ref'), 'area': r.get('area') or r.get('st'), 'park': r.get('park') or r.get('name'), 'park_class': r.get('park_class'),
            'status': r.get('status'), 'band': r.get('band'), 'tier': r.get('tier'),
            'link': r.get('url') or r.get('page') or r.get('map') or r.get('source_url'),
            'why': r.get('why') or (r['whynot'].get('tag') if isinstance(r.get('whynot'), dict) else r.get('whynot'))}


def _ky_tn(r): return (r.get('area') or r.get('st') or '') in ('US-KY', 'US-TN')


def _sample(rows, n, seed=11):
    import random
    rows = list(rows); random.Random(seed).shuffle(rows)
    return rows[:n]


def report(kind, results, details=None):
    from core import rule_g as G
    rows = [r for r in results if r]
    parks = {r.get('ref') for r in rows}
    hit = [r for r in rows if r.get('status') in HIT]
    misses = collections.Counter(x for x in (_reason(r) for r in rows) if x)
    measured, fails, open_items = {'rows': len(rows), 'parks': len(parks), 'parks_with_hit': len({r['ref'] for r in hit})}, [], []
    if kind == 'outline':
        need = [r for r in rows if r.get('status') not in ('found', 'already approved', 'candidate')]   # a candidate's why is its question
        no_tag = [r.get('ref') for r in need if not r.get('whynot')]
        bad = sorted({r.get('url') for r in hit if BAD_PUB.search(r.get('url') or '')})
        tiers = collections.Counter(r.get('rule_g') for r in rows if r.get('rule_g'))
        q_unlikely = [r['ref'] for r in hit if r.get('rule_g') == 'UNLIKELY']
        strong_not_sure = [r['ref'] for r in hit if r.get('band') == 'STRONG' and r.get('rule_g') not in (None, 'SURE')]
        rg12_far = [r['ref'] for r in hit if not r.get('pin_m') in (None, 0) and (r.get('pin_m') or 0) > rules.num('rg12_m')]
        measured.update(SURE=tiers.get('SURE', 0), LIKELY=tiers.get('LIKELY', 0), UNLIKELY_evidence=tiers.get('UNLIKELY', 0),
                        strong=sum(1 for r in hit if r.get('band') == 'STRONG'), already_approved=sum(1 for r in rows if r.get('status') == 'already approved'),
                        open_without_whynot=len(no_tag), non_official_candidates=len(bad), unlikely_as_questions=len(q_unlikely),
                        strong_but_not_sure=len(strong_not_sure), questions_beyond_150m=len(rg12_far),
                        size_way_off_questions=sum(1 for r in hit if r.get('size_band') == 'WAY OFF'))
        for cond, msg in ((no_tag, 'open parks without a why-not'), (bad, 'non-official publishers'), (q_unlikely, 'UNLIKELY rows offered as questions'),
                          (strong_not_sure, 'STRONG rows that are not SURE'), (rg12_far, 'questions with the pin > 150 m outside')):
            if cond: fails.append(f'{msg}: {len(cond)}')
        open_items = ['chat 11: 30 sampled joins per key file (30/30)', 'the finder bars need the side-by-side run (95% re-found, +25% parks) and a 40-row sample (85% YES)']
    elif kind == 'docs':
        maps = collections.Counter(G.link_of(r.get('map')) for r in hit if r.get('map'))
        probs = {r['ref']: G.doc_problems(r, maps.get(G.link_of(r.get('map')), 1)) for r in hit}
        probs = {k: v for k, v in probs.items() if v}
        base = [r for r in rows if _ky_tn(r)]
        got = {r['ref'] for r in base if r.get('status') in HIT}
        share = len(got) / len({r['ref'] for r in base}) if base else None
        measured.update(rows_breaking_doc_rules=len(probs), ky_tn_parks=len({r['ref'] for r in base}), ky_tn_parks_with_hit=len(got),
                        ky_tn_share=round(share, 3) if share is not None else None)
        if probs: fails.append(f'{len(probs)} rows break the document rules: ' + '; '.join(f'{k} {v[0]}' for k, v in list(probs.items())[:3]))
        if share is not None and share < rules.num('docs_ky_tn_share'): fails.append(f"KY + TN share {share:.0%} < {rules.num('docs_ky_tn_share'):.0%}")
        open_items = ['"opens and names the park" is checked live by checks.check_rows; chat 11 reads the spot-check']
    elif kind in ('parking', 'camping', 'trail'):
        pts = [(r, f) for r in hit for f in (r.get('features') or [])]
        smp = _sample(pts, 30)
        bad = []
        for r, f in smp:
            pb = G.point_problems([f['lat'], f['lon'], f.get('name') or ''], r.get('area') or '')
            if kind == 'camping' and not G.camp_feature_ok(f"{f.get('name') or ''} {f.get('type') or ''}"): pb.append('not a campground')
            if pb: bad.append((r['ref'], pb))
        same = G.same_points(hit)
        pos_lon = sum(1 for r, f in pts if (r.get('area') or '')[:2] in ('US', 'CA') and f['lon'] > 0)
        right = len(smp) - len(bad)
        base = [r for r in rows if _ky_tn(r)]
        got = {r['ref'] for r in base if r.get('status') in HIT}
        share = len(got) / len({r['ref'] for r in base}) if base else None
        measured.update(points=len(pts), sample=len(smp), sample_right_by_auto_checks=right, positive_west_longitudes=pos_lon,
                        **({'overlapping_boundaries': len(same)} if kind == 'trail' else {'duplicate_facilities': len(same)}), ky_tn_share=round(share, 3) if share is not None else None)
        if kind == 'parking':
            if smp and right < min(rules.num('parking_right_of_30'), len(smp)) * len(smp) / 30: fails.append(f"{right}/{len(smp)} right by the auto checks (bar {rules.num('parking_right_of_30'):.0f}/30)")
            if share is not None and share < rules.num('parking_ky_tn_share'): fails.append(f"KY + TN share {share:.0%} < {rules.num('parking_ky_tn_share'):.0%}")
            open_items = ['"0 on the wrong park" needs chat 11\'s sample of 30']
        if kind == 'camping':
            ok = right / len(smp) if smp else None
            measured['share_really_campgrounds'] = round(ok, 3) if ok is not None else None
            if ok is not None and ok < rules.num('camp_layer_ok'): fails.append(f"only {ok:.0%} really campgrounds (bar {rules.num('camp_layer_ok'):.0%})")
            open_items = ['campinfo facts (~97% match) need chat 11\'s read of the agency pages']
        if pos_lon: fails.append(f'{pos_lon} west longitudes written as positive')
        if same and kind != 'trail': fails.append(f'{len(same)} duplicate facilities (one facility listed under 2+ parks)')
        if kind == 'trail':
            G.apply_trail_bar(hit)
            passed = [r for r in hit if r.get('trail_bar') == 'PASS']
            held = [r for r in hit if r.get('trail_bar') != 'PASS']
            measured.update(rows_meeting_trail_bar=len(passed), rows_held_as_candidates=len(held),
                            approx_nht=sum(1 for r in passed if r.get('grade') == 'approx'), trail_pin_m=rules.num('trail_pin_m'))
            bad_found = [r['ref'] for r in hit if r.get('status') == 'found' and r.get('trail_bar') != 'PASS']
            if bad_found: fails.append(f"{len(bad_found)} rows marked found without meeting the trail bar")
            open_items = ['Overlapping boundaries go to fers-waiting-room.json (chat 8 + chat 11), never automatic']
        if bad: fails.append(f'{len(bad)} sampled points break a rule: ' + '; '.join(f'{a} {b[0]}' for a, b in bad[:3]))
    else:
        non_ky = [r.get('ref') for r in rows if (r.get('area') or '') != 'US-KY']
        if non_ky: fails.append(f'{len(non_ky)} non-KY rows')
        measured.update(non_ky_rows=len(non_ky))
        if kind in ('hours', 'fees'):
            smp = _sample([r for r in hit], 12)
            bad = []
            for r in smp:
                txt = r.get(kind) or ''
                for ln in txt.split(' | '):
                    ok, why = G.hours_line_ok(ln, kind)
                    if not ok: bad.append((r['ref'], why)); break
                if not r.get('url'): bad.append((r['ref'], 'no official page link'))
            measured.update(sample=len(smp), sample_right_by_auto_checks=len(smp) - len(bad))
            if bad: fails.append(f'{len(smp) - len(bad)}/{len(smp)} (needs 12/12): ' + '; '.join(f'{a} {b}' for a, b in bad[:3]))
            if len(smp) < 12: open_items.append(f'only {len(smp)} rows found: the 12-row sample is short')
        open_items.append('word-for-word quotes: chat 11 reads the sample')
    verdict = 'FAIL' if fails else ('NO ROWS' if not rows else 'NO HITS (nothing to grade)' if not hit else 'PASS (auto checks; chat 11 still samples)')
    ex = hit[:3] + [r for r in rows if r.get('status') not in HIT][:5]
    ex = (ex + hit[3:])[:5]
    return {'kind': kind, 'verdict': verdict, 'bar': bar(kind) or 'no bar in the specs', 'measured': measured, 'fails': fails,
            'top_miss_reasons': [{'reason': k, 'parks': v} for k, v in misses.most_common(5)],
            'examples': [_example(r) for r in ex], 'still_needs': open_items, 'details': details or {}}


def to_markdown(reports):
    out = ['# Grades, one per kind (for chat 11)', '', 'The engine decides nothing; this is its self-check against the bar.', '']
    for k, g in reports.items():
        if not isinstance(g, dict) or 'verdict' not in g: continue
        out += [f"## {k}: {g['verdict']}", '', f"**Bar:** {g['bar']}", '',
                '**Measured:** ' + ', '.join(f'{a} {b}' for a, b in g['measured'].items()), '', '**Top reasons for misses:**']
        out += [f"- {m['reason']} ({m['parks']})" for m in g['top_miss_reasons']] or ['- none']
        if g.get('fails'): out += ['', '**Why it fails:**'] + [f'- {x}' for x in g['fails']]
        out += ['', '**5 example parks:**', '', '| ref | park | status | band | link / why |', '|---|---|---|---|---|']
        for e in g['examples']:
            out.append(f"| {e['ref']} | {e['park'] or ''} | {e['status']} | {e.get('band') or ''} | {(e.get('link') or e.get('why') or '')[:110]} |")
        if g['still_needs']: out += ['', '**Still needs:** ' + '; '.join(g['still_needs'])]
        out.append('')
    return '\n'.join(out)
