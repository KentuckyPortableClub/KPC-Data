"""OUTLINE plug-in: the new finder (KPC_10_Finder3_Spec.md), ladder L0-L5, by agency, two passes.

L0 layers we already know: the live-verified registries (US+CA: PAD-US, NPS, USFS, FWS, BLM, state/province layers; world:
   national layers in hunt order) + found-layers.json from earlier runs. Pin query with a 150 m distance (R-G12) AND a
   Title-Case LIKE name search (lesson 1), every text field scanned (lesson 2), distance pin -> edge measured.
L1 the agency's own servers (agencies.json roots, walked two folders deep, cached 30 days).
L2 open-data portals: catalog.data.gov (US federal), open.canada.ca (CA) CKAN search; resources that are ArcGIS REST layers.
L3 ArcGIS Online search by park name; only items owned by an official organisation are kept.
L4 the park's official page: KML / KMZ / shapefile / GeoJSON links are read near the pin; PDF / image maps go to
   picture-maps.json (never traced here).
L5 county parcels (US, small parks): kpc_parcels is not in this folder; the step writes its why-not ('L5 not wired').
Every hit gets a tier (T-1..T-6), a band (STRONG / WEAK / CONFLICT), the notes standard, and goes out as a QUESTION row
(answer '' / checked_by ''): the engine decides nothing."""
import re, urllib.parse
from core import geo, gis, names, rule_g
from core.agencies import official_domain
from core.notes import Notes, confidence_of
from .base import Plugin, dump, today

BIG_KIND = re.compile(r'\b(national (forest|park|grassland|wildlife refuge|recreation area|preserve)|wilderness|wma|wildlife management|'
                      r'state (park|forest)|provincial park|rma|recreation management|refuge)\b', re.I)
POINT_TAG = {'blocked': 'blocked', 'token-only (needs sign-in)': 'token-only'}
DL_EXT = re.compile(r'\.(kmz|kml|geojson|zip)(\?|$)', re.I)
MAP_EXT = re.compile(r'\.(pdf|jpe?g|png|gif)(\?|$)', re.I)
MAP_WORD = re.compile(r'\bmaps?\b|carte|karte|mapa|kaart|地図', re.I)


class Outline(Plugin):
    KIND = 'outline'
    GAP_KINDS = ('outline',)

    def work_row(self, agency, row, eng, pass_no):
        p = eng.park(row)
        out = {'ref': row['ref'], 'area': row['area'], 'park': p.get('n'), 'agency_group': agency, 'kind': 'outline', 'date': today()}
        nt = Notes()
        done = eng.registry.approved_for(row['ref'])
        if done:                                      # a person already said YES (chat 11): nothing to find, never re-ask
            nt.looked('approved list (chat 11 YES rows)', f'already approved: {done[0][2]} in {done[0][0]}')
            out.update(status='already approved', approved=done, notes=nt.as_dict()); return out
        if p.get('lat') in (None, '') or p.get('lon') in (None, ''):
            nt.looked('POTA pin', 'no pin'); out.update(status='not found', whynot={'tag': 'no pin', 'step_reached': 'L0'}, notes=nt.as_dict()); return out
        lat, lon = float(p['lat']), float(p['lon'])
        if abs(lat) < 0.01 and abs(lon) < 0.01: nt.solve('PIN OFF: POTA pin is 0,0 (name search only)')
        words = names.core_words(p.get('n') or '')
        cands, blocked = [], []
        steps = ['L0', 'L1', 'L4', 'L5'] if pass_no == 1 else ['L0', 'L1', 'L2', 'L3', 'L4', 'L5']   # pass 2 adds the portal + AGOL searches
        reached = None
        for step in steps:
            if eng.step_off(step, row['area']): continue
            reached = step
            got = getattr(self, '_' + step)(eng, row, p, lat, lon, words, nt, blocked, pass_no)
            cands += got or []
            good = [c for c in cands if c['tier'] in ('T-1', 'T-2', 'T-3')]
            if good: break
        cands += self._last_resort(eng, row, p, lat, lon, words, nt, blocked, cands)
        return apply_ruling(eng.registry.ruling(row['ref']), self._finish(eng, row, p, lat, lon, out, nt, cands, blocked, reached))

    def _last_resort(self, eng, row, p, lat, lon, words, nt, blocked, cands):
        """Club rule W-10 (Nov 1): WDPA is rejected when an official layer exists for the park (any T-1..T-3 record from an
        official ladder layer: the area's own layers incl. Florida's conservation lands, PAD-US by pin and by name, federal
        layers). Only when nothing official answered, and nothing was blocked (blocked is not 'not found'), WDPA is asked,
        always approx and labelled 'WDPA (last resort)'."""
        from core import rules
        if not rules.wdpa_last_resort_ok(): return []
        srcs = eng.registry.last_resort_for(row['area']) if hasattr(eng.registry, 'last_resort_for') else []
        if not srcs: return []
        if any(c['tier'] in ('T-1', 'T-2', 'T-3') for c in cands):
            nt.looked('WDPA (last resort)', 'not asked: an official layer has a record for this park (W-10)'); return []
        if blocked:
            nt.looked('WDPA (last resort)', 'not asked: an official source was blocked (blocked is not not-found; retry first)'); return []
        out = []
        for src in srcs:
            got = self._ask(eng, src, p, lat, lon, words, nt, blocked, 'W-10', last_resort=True)
            for c in got: c['last_resort'] = True
            out += got
        if out: nt.double_check('WDPA (last resort): no official layer had a record; approximate only, a person must check (W-10)')
        return out

    # ------------------------------------------------------------------ the ladder
    def _ask(self, eng, src, p, lat, lon, words, nt, blocked, step, by_name=True, last_resort=False):
        """Pin query (150 m) + name search on one source. Returns candidate dicts."""
        ref = p['ref']; out = []
        bad = '' if last_resort else gis.cites_wdpa(eng.P, src, ref_=ref)      # WDPA: only through the W-10 last-resort path
        if bad:
            nt.looked(src.get('id') or src['url'], f'skipped: {bad}'); return out
        hits, err = gis.point(eng.P, src, lat, lon, buffer_m=150 if src.get('geometry', 'polygon') == 'polygon' else 200, ref_=ref)
        if err:
            if err.startswith(('blocked', 'token', 'host resting')): blocked.append((src.get('id') or src['url'], err)); nt.looked(src.get('id') or src['url'], f'blocked ({err[:80]})')
            else: nt.looked(src.get('id') or src['url'], f'error ({err[:80]})')
            return out
        nm_hits = []
        if by_name and words and not any(names.tier(p['n'], h.get('name') or '', h['attrs'], *self._rel(lat, lon, h))[0] in ('T-1', 'T-2') for h in hits):
            nm_hits, err2 = gis.by_name(eng.P, src, words, ref_=ref)
            if err2 and err2.startswith(('blocked', 'token')): blocked.append((src.get('id') or src['url'], err2))
        seen = set()
        for h in hits + (nm_hits or []):
            key = (h.get('id'), h.get('name'))
            if key in seen: continue
            seen.add(key)
            if eng.registry.is_no(ref, src['url'], h.get('id')):
                nt.looked(src.get('id') or src['url'], f"skipped record {h.get('id')} ({h.get('name')}): chat 11 said NO"); continue
            inside, d = self._rel(lat, lon, h)
            nm = h.get('name') or ''
            if not nm or names.similarity(p['n'], nm) < 0.4:
                s, k, v = _best_field(p['n'], h['attrs'])
                if s >= 0.5: nm = v; eng.findings.add(by='outline', host=eng.P.host(src['url']), agency=src.get('agency'), kind='name-field', value=k,
                                                     note=f"layer {src.get('id') or src['url']}: the name is in {k}")
            t, sim = names.tier(p['n'], nm, h['attrs'], inside, d)
            if t is None: continue
            out.append({'src': src, 'hit': h, 'name': nm, 'tier': t, 'sim': sim, 'inside': inside, 'pin_m': None if inside else (round(d) if d is not None else None),
                        'step': step, 'acres': _acres(h.get('geom'))})
        nt.looked(src.get('id') or src['url'], f"{'hit' if out else 'no hit'} ({len(hits)} at pin, {len(nm_hits or [])} by name)")
        return out

    @staticmethod
    def _rel(lat, lon, h):
        if h.get('geom') is None: return True, 0.0
        inside, d = geo.pin_relation(lat, lon, h['geom'])
        return (inside if inside is not None else True), d

    def _L0(self, eng, row, p, lat, lon, words, nt, blocked, pass_no):
        out = []
        srcs = eng.registry.for_area(row['area'], 'outline') + eng.found_layers_for(row['area'])
        for src in srcs:
            got = self._ask(eng, src, p, lat, lon, words, nt, blocked, 'L0', by_name=(pass_no == 2 or src.get('kind') in ('arcgis', 'wfs', 'geoadmin')))
            out += got
            if any(c['tier'] in ('T-1', 'T-2') and c['src'].get('grade', 'official') == 'official' for c in got): break
        return out

    def _L1(self, eng, row, p, lat, lon, words, nt, blocked, pass_no):
        roots = eng.agency_roots(row.get('agency'))
        out = []
        for root in roots[:3]:
            lays = eng.walk(root)
            pick = [L for L in lays if re.search(r'park|preserve|reserve|wildlife|forest|protected|boundar|conserv|natur|recreat|land|refuge|trail', L.get('layer_name') or '', re.I)]
            for L in pick[:6]:
                src = {'id': f"L1 {L['url']}", 'kind': 'arcgis', 'url': L['url'], 'name_field': L.get('name_field'), 'agency': row.get('agency'),
                       'grade': 'official', 'geometry': 'polygon' if 'Polygon' in (L.get('geometry') or '') else 'line'}
                got = self._ask(eng, src, p, lat, lon, words, nt, blocked, 'L1')
                out += got
                if got: eng.add_found_layer(src, row['area'], 'L1 agency server walk')
        if not roots: nt.looked('L1 agency servers', 'none known for this agency (agencies.json)')
        return out

    def _L2(self, eng, row, p, lat, lon, words, nt, blocked, pass_no):
        cc = row['area'].split('-')[0]
        cats = {'US': 'https://catalog.data.gov/api/3/action/package_search', 'CA': 'https://open.canada.ca/data/api/3/action/package_search'}
        if cc not in cats or not words: return []
        q = ' '.join(words[:3]) + (' boundary' if cc == 'US' else '')
        r, j = eng.P.get_json(cats[cc] + '?' + urllib.parse.urlencode({'q': q, 'rows': 10}), ref_=p['ref'], kind='portal', ttl_days=30)
        if r.blocked: blocked.append((cats[cc], r.blocked)); nt.looked('L2 ' + cats[cc], f'blocked ({r.blocked[:60]})'); return []
        out = []
        for pkg in ((j or {}).get('result') or {}).get('results', [])[:10]:
            org = ((pkg.get('organization') or {}).get('title') or '')
            for res in pkg.get('resources', []):
                u = res.get('url') or ''
                m = re.match(r'(https?://[^?#]+/rest/services/[^?#]+/(MapServer|FeatureServer))(/\d+)?', u)
                if not m: continue
                lays = [m.group(0)] if m.group(3) else [L['url'] for L in _layers(eng, m.group(1))]
                for lu in lays[:4]:
                    src = {'id': f'L2 {lu}', 'kind': 'arcgis', 'url': lu, 'name_field': None, 'agency': org, 'grade': 'official', 'geometry': 'polygon'}
                    got = self._ask(eng, src, p, lat, lon, words, nt, blocked, 'L2', by_name=False)
                    out += got
                    if got: eng.add_found_layer(src, row['area'], f'L2 {cats[cc]}')
        nt.looked('L2 ' + cats[cc], f'{len(out)} candidates')
        return out

    def _L3(self, eng, row, p, lat, lon, words, nt, blocked, pass_no):
        if not words: return []
        disc = eng.discover_mod()
        items = disc.search(eng.P, '"' + ' '.join(words[:3]) + '"', n=15)
        out = []
        for it in items[:8]:
            basis, why = disc.official(eng.P, it, eng.org_cache, '*world*' if row['area'][:2] not in ('US', 'CA') else row['area'])
            if not basis: continue
            for L in disc.layers(eng.P, it.get('url') or '', 'polygon')[:3]:
                src = {'id': f"L3 {L['url']}", 'kind': 'arcgis', 'url': L['url'], 'name_field': L.get('name_field'), 'agency': basis, 'grade': 'official',
                       'geometry': 'polygon', 'official_basis': basis}
                got = self._ask(eng, src, p, lat, lon, words, nt, blocked, 'L3', by_name=False)
                out += got
                if got: eng.add_found_layer(src, row['area'], 'L3 ArcGIS Online search')
        nt.looked('L3 ArcGIS Online search', f'{len(items)} items, {len(out)} candidates')
        return out

    def _L4(self, eng, row, p, lat, lon, words, nt, blocked, pass_no):
        page_url = eng.official_page(row)
        if not page_url: nt.looked('L4 park page', 'no official page known'); return []
        from core import read as rd
        pg = rd.read(eng.P, page_url, ref_=p['ref'], kind='outline-page')
        if pg.blocked: blocked.append((page_url, pg.blocked)); nt.looked(page_url, f'blocked ({pg.blocked[:60]})'); return []
        from core.polite import links_in
        links = links_in(pg.html or '', pg.final_url or page_url) if pg.html else []
        out = []
        for L in links:
            u = L[0] if isinstance(L, (list, tuple)) else L
            txt = (L[1] if isinstance(L, (list, tuple)) and len(L) > 1 else '') or ''
            host = urllib.parse.urlsplit(u).netloc
            if DL_EXT.search(u) and official_domain(host):
                src = {'id': f'L4 {u}', 'kind': 'download', 'url': u, 'agency': row.get('agency'), 'grade': 'official', 'geometry': 'polygon', 'max_mb': 50}
                got = self._ask(eng, src, p, lat, lon, words, nt, blocked, 'L4', by_name=False)
                out += got
            elif MAP_EXT.search(u) and (MAP_WORD.search(u) or MAP_WORD.search(txt)) and official_domain(host):
                eng.picture_map(row, p, u, page_url)
        nt.looked(page_url, f'page read ({pg.how}); {len(out)} file candidates')
        return out

    def _L5(self, eng, row, p, lat, lon, words, nt, blocked, pass_no):
        """Parcels (Hard Look 'record-number and parcel tricks'): the parcel under the pin from an official statewide /
        provincial parcel layer in the registry (use='parcel', from the club's agency atlas). Never an outline: a WEAK
        PARCEL lead with its record (parcel) number and owner, for a person to confirm. Worth most for historic sites and
        small county / city parks (club priority 3 and 5)."""
        if row['area'][:2] not in ('US', 'CA'): return []
        srcs = [s for s in eng.registry.for_area(row['area'], 'parcel') if s.get('area') == row['area'] or s.get('area') == row['area'][:2]]
        if not srcs:
            nt.looked('L5 parcels', f"no official parcel layer for {row['area']} in the registry yet (kpc_parcels county finder not wired)")
            eng.parcels_note(row, 'L5: no statewide parcel layer known'); return []
        out = []
        for src in srcs:
            hits, err = gis.point(eng.P, src, lat, lon, buffer_m=0, ref_=p['ref'])
            if err:
                if err.startswith(('blocked', 'token', 'host resting')): blocked.append((src.get('id') or src['url'], err))
                nt.looked(src.get('id') or src['url'], f'parcel layer: {err[:80]}'); continue
            for h in hits[:1]:
                a = h.get('attrs') or {}
                rec = next((f'{k}={v}' for k, v in a.items() if v not in (None, '') and re.search(r'parcel|^pin$|apn|roll|^lot|prop_?id|record|account|tax_?id', k, re.I)), f"id={h.get('id')}")
                owner = next((str(v) for k, v in a.items() if v not in (None, '') and re.search(r'owner|ownership', k, re.I)), '')
                nm = owner or rec
                out.append({'src': src, 'hit': h, 'name': nm, 'tier': 'T-6', 'sim': names.similarity(p['n'], owner) if owner else 0.0, 'inside': True,
                            'pin_m': 0, 'step': 'L5', 'acres': _acres(h.get('geom')), 'parcel_record': rec, 'parcel_owner': owner})
                eng.parcels.append({'ref': row['ref'], 'area': row['area'], 'status': 'parcel lead', 'record': rec, 'owner': owner,
                                    'layer': src['url'], 'grade': 'parcel', 'why': 'parcel under the POTA pin; a person should confirm'})
            nt.looked(src.get('id') or src['url'], f"parcel layer: {len(hits)} parcel(s) under the pin")
        return out

    # ------------------------------------------------------------------ scoring + the row
    def _finish(self, eng, row, p, lat, lon, out, nt, cands, blocked, reached):
        out.setdefault('kind', 'outline')
        good = sorted(cands, key=lambda c: (not rule_g.layer_kind_ok(p.get('n') or '', _layer_text(c['src']))[0], TIER_ORDER[c['tier']], not rule_g.kinds_match(p.get('n') or '', c['name'] or ''), c['src'].get('grade', 'official') != 'official', 0 if c['inside'] else 1, c.get('pin_m') or 0))   # round 5: same kind first (a WSR park -> the river line, not a state trail)
        if not good:
            if blocked:          # blocked is not "not found": an unread source keeps the park open as blocked (retried next run)
                n = len({b[0] for b in blocked})
                out.update(status='blocked', whynot={'tag': f'blocked ({n} source{"s" if n > 1 else ""} could not be read, e.g. {blocked[0][1][:60]})'
                                                     + ('' if nt.blocked_only() else '; the sources that answered had no record'), 'step_reached': reached, 'date': today()})
            else:
                tag = ('no-layer: no official record at the pin or by name' + (f' ({len(blocked)} sources blocked)' if blocked else '')) if nt.where_looked \
                    else f"no verified layer for {row['area']} in the registry yet (nothing asked)"
                out.update(status='not found', whynot={'tag': tag, 'step_reached': reached, 'date': today()})
            out['notes'] = nt.as_dict(); return out
        best = good[0]
        # size + kind check (US-OR Monument RMA vs a 1-acre GS)
        size_flag = best.get('acres') is not None and best['acres'] < 5 and BIG_KIND.search(p.get('n') or '')
        clash = names.kind_clash(p.get('n') or '', best['name'] or '')
        others = {names.norm(c['name']) for c in good[1:4] if c['tier'] in ('T-1', 'T-2', 'T-3')} - {names.norm(best['name'])}
        other_far = [c for c in good[1:6] if c['tier'] in ('T-1', 'T-2', 'T-3') and c['src'].get('grade', 'official') == 'official'
                     and names.norm(c['name']) not in {names.norm(best['name'])} and not _overlap(c, best)]
        grade = best['src'].get('grade', 'official')
        if other_far: band = 'CONFLICT'
        elif best['tier'] in ('T-1', 'T-2') and best['inside'] and grade == 'official' and not size_flag and not clash: band = 'STRONG'
        else: band = 'WEAK'
        bg = best['hit'].get('geom')        # Big South Fork lesson: a copy of the same land is merged, not counted twice
        copies = [c for c in good[1:6] if bg is not None and c['hit'].get('geom') is not None and rule_g.same_land(bg, c['hit']['geom'])]
        if copies: nt.because('same land also in ' + ', '.join(f"{c['src'].get('id')} '{c['name']}'" for c in copies[:3]) + ': merged, counted once')
        rule = None
        if not best['inside'] and best.get('pin_m') is not None and best['pin_m'] <= rule_g.rules.num('rg12_m') and best['tier'] in ('T-2', 'T-3'):
            rule = 'R-G12'; nt.solve(f"pin just outside ({best['pin_m']} m): candidate only (G-F1)")
        if best['tier'] == 'T-4':
            typo = eng.pin_typo_check(row, p, best)
            if typo: rule = 'R-G13'; nt.solve(f"PIN OFF: {typo['official_point'][0]},{typo['official_point'][1]}, {typo['km']} km, {typo['source']}")
        if names.norm(best['name']) != names.norm(p.get('n') or '') and best['tier'] in ('T-1', 'T-2', 'T-3'):
            nt.solve(f"NAME SOLVED: agency calls it {best['name']}") if names.similarity(p.get('n'), best['name']) < 0.9 else None
        if clash: nt.solve(f"WRONG KIND?: park is a {names.kind_of(p.get('n'))}, record is a {names.kind_of(best['name'])}")
        if size_flag: nt.double_check(f"record is only {best['acres']} acres for a big kind of park")
        nt.because(f"record '{best['name']}' ({best['src'].get('id') or best['src']['url']}); "
                   + ('pin inside' if best['inside'] else f"pin {best.get('pin_m')} m from the edge") + (f"; about {best['acres']} acres" if best.get('acres') is not None else ''))
        if others: nt.double_check('other names at the pin: ' + '; '.join(sorted(others))[:200])
        # Rule G (chat 11's bar): SURE / LIKELY / UNLIKELY. UNLIKELY is evidence only, never a question.
        want_ac = _num(p.get('acres') or row.get('acres'))
        ratio = (best['acres'] / want_ac) if (want_ac and best.get('acres')) else None
        hg = best['hit'].get('geom')
        rec_line = rule_g.is_line(hg) if hg is not None else best['src'].get('geometry') == 'line'
        lr = bool(best.get('last_resort') or best['src'].get('last_resort'))
        if lr: band = 'WEAK' if band == 'STRONG' else band
        g_tier, g_why = rule_g.tier_g(p.get('n') or '', best['name'] or '', best['inside'], best.get('pin_m'),
                                      rec_line=rec_line, size_ratio=ratio, layer=_layer_text(best['src']), last_resort=lr)
        if g_tier != 'SURE' and band == 'STRONG': band = 'WEAK'
        nt.because(f'Rule G: {g_tier} ({g_why})' + (f'; size {rule_g.size_band(ratio)} ({ratio:.2f}x of {want_ac} ac)' if ratio else '; size unknown'))
        conf, chk = confidence_of(best['tier'], band, grade)
        nt.set_confidence(conf, chk)
        src, h = best['src'], best['hit']
        st = 'candidate' if band != 'STRONG' or rule or grade != 'official' else 'found'
        if g_tier == 'UNLIKELY': st = 'evidence'
        out.update({
            'status': st, 'st': row['area'], 'url': gis.layer_url(src), 'service_url': src['url'], 'name_field': src.get('name_field'), 'agency': src.get('agency'),
            'licence': src.get('licence') or 'see the publisher', 'answer': '', 'checked_by': '',
            'tier': best['tier'], 'band': band, 'step': best['step'], 'record': h.get('id'), 'record_name': best['name'],
            'layer': src.get('id') or src['url'], 'record_link': gis.record_link(src, h), 'where': _where(src, h),
            'pin_m': 0 if best['inside'] else best.get('pin_m'), 'acres_approx': best.get('acres'), 'grade': grade,
            'envelope': geo.envelope(h['geom']) if h.get('geom') is not None else None, 'rule': rule,
            'others': [{'record_name': c['name'], 'layer': c['src'].get('id'), 'tier': c['tier'], 'pin_m': c.get('pin_m')} for c in good[1:5]],
            'source_url': h.get('source_url'), 'read_date': today(),
            'rule_g': g_tier, 'rule_g_why': g_why, 'size_band': rule_g.size_band(ratio),
            'why': f"{best['tier']} {band}: '{best['name']}' at the POTA pin" + (' (approximate source)' if grade != 'official' else ''),
            'notes': nt.as_dict()})
        if lr:          # W-10: always approx, labelled, never found / STRONG
            from core import rules as _r
            out.update(grade='approx', g='approx', source_policy=_r.WDPA_LAST_RESORT, label=_r.WDPA_LAST_RESORT,
                       why=out['why'] + ' [WDPA (last resort): no official layer had a record]')
            if out['status'] == 'found': out['status'] = 'candidate'
        if best['inside'] and best['tier'] in ('T-1', 'T-2') and band != 'CONFLICT' and h.get('geom') is not None and not lr:
            eng._shapes[(row['area'], row['ref'])] = h['geom']          # the parking / camping plug-ins tie points by 'place'
        if g_tier == 'UNLIKELY':
            out['whynot'] = {'tag': f'UNLIKELY only (evidence, never a question): {g_why}', 'step_reached': reached, 'date': today()}
        elif grade == 'parcel':
            out['parcel_record'], out['parcel_owner'] = best.get('parcel_record'), best.get('parcel_owner')
            out['whynot'] = {'tag': f"PARCEL lead only ({best.get('parcel_record')}{', owner ' + best['parcel_owner'] if best.get('parcel_owner') else ''}): "
                                    "a parcel is not the park's line; a person should confirm", 'step_reached': reached, 'date': today()}
        elif lr:
            out['whynot'] = {'tag': 'WDPA (last resort): approximate only; no official layer had a record for this park (club rule W-10)', 'step_reached': 'W-10', 'date': today()}
        elif grade != 'official':
            out['whynot'] = {'tag': f"approximate only ({best['src'].get('id') or best['src']['url']} is graded approximate: " + ('EU compilation' if best['src'].get('cc') == 'EU' or best['src'].get('basis_note') == 'EU compilation' else best['src'].get('official_basis') or 'general area, not a legal line')[:80] + ')', 'step_reached': reached, 'date': today()}
        return out

    # ------------------------------------------------------------------ output
    def write(self, results, out_dir, eng=None):
        q = [r for r in results if r.get('status') in ('found', 'candidate') and r.get('rule_g') != 'UNLIKELY']   # UNLIKELY: never a question
        dump({'questions': q}, f'{out_dir}/questions.json')
        dump({'evidence': [r for r in results if r.get('status') == 'evidence']}, f'{out_dir}/evidence.json')
        dump({r['ref']: r['whynot'] for r in results if r.get('whynot')}, f'{out_dir}/whynot.json')
        if eng:
            dump(eng.found_layers, f'{out_dir}/found-layers.json')
            dump({'maps': eng.picture_maps}, f'{out_dir}/picture-maps.json')
            dump({'parcels': eng.parcels}, f'{out_dir}/parcels.json')
        L = ['# Outline summary', '', '| area | open before | found | candidate | not found | blocked |', '|---|---|---|---|---|---|']
        areas = sorted({r['area'] for r in results})
        for a in areas:
            rs = [r for r in results if r['area'] == a]
            c = lambda s: sum(1 for r in rs if r.get('status') == s)
            L.append(f"| {a} | {len(rs)} | {c('found')} | {c('candidate')} | {c('not found')} | {c('blocked')} |")
        steps = {}
        for r in q: steps[r.get('step')] = steps.get(r.get('step'), 0) + 1
        L += ['', 'Finds per step: ' + ', '.join(f'{k} {v}' for k, v in sorted(steps.items(), key=lambda x: str(x[0])))]
        open(f'{out_dir}/summary.md', 'w').write('\n'.join(L) + '\n')

    def grade(self, results, eng):
        g = super().grade(results, eng)
        q = [r for r in results if r.get('status') in ('found', 'candidate')]
        g['bands'] = {b: sum(1 for r in q if r.get('band') == b) for b in ('STRONG', 'WEAK', 'CONFLICT')}
        g['tiers'] = {t: sum(1 for r in q if r.get('tier') == t) for t in ('T-1', 'T-2', 'T-3', 'T-4', 'T-6')}
        g['every_open_park_has_whynot'] = all(r.get('whynot') for r in results if r.get('status') not in ('found', 'already approved'))
        g['non_official_publishers'] = sorted({r.get('url') for r in q if any(x in (r.get('url') or '') for x in ('openstreetmap', 'overpass', 'protectedplanet', 'wdpa', 'google', 'wikidata'))})
        return g


def _layer_text(src):
    """Everything that names the layer: address, id, layer name, agency, licence (for the WDPA and forestry kind guards)."""
    return ' '.join(str(src.get(k) or '') for k in ('url', 'id', 'layer_name', 'name', 'agency', 'licence', 'description'))


def apply_ruling(rl, out):
    """Club rulings per park (registry/rulings.json). 'pin only': no official layer yet: keep looking; a new find is only
    ever a candidate for chat 11, and nothing found = pin only + the ruling's tag. 'hold': nothing is offered as a question."""
    if not rl: return out
    out['ruling'] = rl
    if rl.get('ruling') == 'pin only':
        if out.get('status') in ('found', 'candidate'):
            out['status'] = 'candidate'
            if out.get('band') == 'STRONG': out['band'] = 'WEAK'
            out.setdefault('whynot', {})['ruling'] = f"club ruling: pin only until a person accepts this new layer ({rl.get('why', '')[:120]})"
        else:
            out['status'] = 'pin only'
            out['whynot'] = {**(out.get('whynot') or {}), 'tag': rl.get('tag') or 'no official layer found yet',
                             'ruling': rl.get('why', ''), 'date': today()}
    elif rl.get('ruling') == 'hold':
        if out.get('status') in ('found', 'candidate'): out['held_find'] = {k: out.get(k) for k in ('layer', 'record', 'record_name', 'rule_g', 'rule_g_why')}
        out['status'] = 'held'
        out['whynot'] = {**(out.get('whynot') or {}), 'tag': rl.get('tag') or 'held by the club', 'ruling': rl.get('why', ''), 'date': today()}
    return out


TIER_ORDER = {'T-1': 0, 'T-2': 1, 'T-3': 2, 'T-4': 3, 'T-5': 5, 'T-6': 4}


DESC_FIELD = re.compile(r'desc|comment|note|remark|summary|narrative|abstract|text|blurb|info|detail|purpose|history', re.I)


def _best_field(park_name, attrs):
    best = (0.0, None, None)
    for k, v in (attrs or {}).items():
        if not isinstance(v, str) or len(v) < 3 or re.match(r'^(shape|globalid|guid|uuid|wkt|geom)', k, re.I): continue
        # round 5 (US-6281): a description / comment sentence is not a name ('... river swamp on the Loxahatchee River ...' gave
        # Jonathan Dickinson State Park a Wild and Scenic River name match)
        if DESC_FIELD.search(k) or len(v) > 120 or re.search(r'[a-z]\. [A-Z]|[a-z], [a-z]', v): continue
        s = names.similarity(park_name, v)
        if s > best[0]: best = (s, k, v)
    return best


def _overlap(a, b):
    ga, gb = a['hit'].get('geom'), b['hit'].get('geom')
    if ga is None or gb is None: return True
    try: return ga.intersects(gb)
    except Exception: return True  # noqa: BLE001


def _where(src, h):
    if src.get('kind') == 'arcgis' and h.get('id') is not None: return f"{src.get('id_field') or 'OBJECTID'}={h['id']}"
    return f"id={h.get('id')}"


def _layers(eng, svc):
    r, j = eng.P.get_json(svc.rstrip('/') + '/layers?f=json', kind='layers', ttl_days=30)
    out = []
    for L in (j or {}).get('layers', []):
        if L.get('geometryType') == 'esriGeometryPolygon': out.append({'url': f"{svc.rstrip('/')}/{L['id']}", 'name': L.get('name')})
    return out


def _acres(g):
    """Rough acres, or None for a line / point / bad geometry (never crashes a row)."""
    if g is None: return None
    try:
        a = geo.acres(g)
        return round(a, 1) if a is not None else None
    except Exception:  # noqa: BLE001
        return None


def _num(x):
    try: return float(str(x).replace(',', '')) if x not in (None, '') else None
    except ValueError: return None
