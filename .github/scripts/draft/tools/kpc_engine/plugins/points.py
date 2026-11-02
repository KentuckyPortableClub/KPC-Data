"""PARKING / CAMPING / TRAIL plug-ins (US + Canada; they share one engine).
For each park: the registry's use-specific layers for the area (state / province layer first, then national), queried around
the POTA pin; a feature is kept when
  how='name'  its name / any text field carries the park's name words (and it is within the search radius), or
  how='place' it sits inside the park's official outline (from this run's outline results or the club key envelope).
Club-made labels never appear; the agency goes in the label's last brackets (data/access shape)."""
import re
from core import geo, gis, names, rule_g
from core.notes import Notes
from .base import Plugin, dump, today

TYPE_WORDS = [(re.compile(r'boat|ramp|launch|access site|fishing access', re.I), 'Boat ramp / launch'),
              (re.compile(r'trail ?head|th\b', re.I), 'Trailhead'), (re.compile(r'parking|lot\b|car park', re.I), 'Parking'),
              (re.compile(r'entrance|gate', re.I), 'Entrance'), (re.compile(r'camp', re.I), 'Campground')]


class PointPlugin(Plugin):
    USE = 'parking'
    RADIUS = 3000
    MAX_ROWS = 25

    def work_row(self, agency, row, eng, pass_no):
        p = eng.park(row); nt = Notes()
        out = {'ref': row['ref'], 'area': row['area'], 'park': p.get('n'), 'kind': self.KIND, 'agency_group': agency, 'date': today()}
        if p.get('lat') in (None, ''): out.update(status='not found', whynot={'tag': 'no pin'}); return out
        lat, lon = float(p['lat']), float(p['lon'])
        words = names.core_words(p.get('n') or '')
        shape = eng.outline_shape(row)
        rad = self.RADIUS * (2 if pass_no == 2 else 1)
        feats, blocked, first_err = [], 0, ''
        srcs = eng.registry.for_area(row['area'], self.USE)
        if not srcs: nt.looked(f'{self.USE} layers for {row["area"]}', 'none verified in the registry')
        for src in srcs:
            hits, err = gis.point(eng.P, src, lat, lon, buffer_m=rad, ref_=p['ref'])
            if err:
                if err.startswith(('blocked', 'token', 'host resting')): blocked += 1; first_err = first_err or err; nt.looked(src['id'], f'blocked ({err[:60]})')
                else: nt.looked(src['id'], f'error ({err[:60]})')
                continue
            kept = 0
            for h in hits:
                g = h.get('geom')
                if g is None: continue
                c = g.representative_point() if g.geom_type != 'Point' else g
                txt = names.all_text(h['attrs'])
                how = None
                if shape is not None and shape.contains(c): how = 'place'
                elif words and names.words_in_text(words, txt): how = 'name'
                if not how: continue
                kept += 1
                feats.append(self.feature(src, h, c, how, lat, lon))
            nt.looked(src['id'], f'{kept} kept of {len(hits)} within {rad} m')
        seen, uniq = set(), []
        for f in sorted(feats, key=lambda f: (f['how'] != 'place', f['m'])):
            k = (round(f['lat'], 4), round(f['lon'], 4))
            if k in seen: continue
            bad = rule_g.point_problems([f['lat'], f['lon'], f.get('name') or ''], row['area'])
            if self.KIND == 'camping' and not rule_g.camp_feature_ok(f"{f.get('name') or ''} {f.get('type') or ''}"): bad.append('not a campground (picnic shelter / boat ramp / other business)')
            if bad: nt.looked(f['source'], f"dropped {f.get('name') or 'a point'}: {'; '.join(bad)}"); continue      # chat 11's parking / camp bars
            seen.add(k); uniq.append(f)
        uniq = uniq[:self.MAX_ROWS]
        if uniq:
            nt.because(f"{len(uniq)} official features ({', '.join(sorted({f['how'] for f in uniq}))})")
            nt.set_confidence('likely' if any(f['how'] == 'place' for f in uniq) else 'weak', 'name-only ties: check the feature is on the park')
            out.update(status='found', features=uniq)
        else:
            # blocked is not "not found": while any source went unread, the row stays blocked (retried next run)
            tag = (f'blocked: {blocked} of {len(srcs)} {self.USE} sources could not be read ({first_err[:50]})' + ('' if nt.blocked_only() else '; the others had nothing tied to the park')) if blocked \
                else (f'no official {self.USE} feature tied to the park by name or place' if srcs else f'no verified {self.USE} layer for this area yet')
            out.update(status='blocked' if blocked else 'not found', whynot={'tag': tag, 'date': today()})
        out['notes'] = nt.as_dict()
        return out

    def feature(self, src, h, c, how, lat, lon):
        nm = h.get('name') or ''
        a = h['attrs']
        typ = next((lab for rx, lab in TYPE_WORDS if rx.search(' '.join(str(v) for v in a.values() if isinstance(v, str))[:400] + ' ' + (src.get('layer_name') or src['id']))), 'Parking')
        return {'lat': round(c.y, 6), 'lon': round(c.x, 6), 'name': nm, 'type': typ, 'agency': src.get('agency_short') or src.get('agency'),
                'how': how, 'm': round(geo.haversine_m(lat, lon, c.y, c.x)), 'source': src['id'], 'record_link': gis.record_link(src, h)}


class Parking(PointPlugin):
    KIND = 'parking'; USE = 'parking'; GAP_KINDS = ('parking',); RADIUS = 3000

    def write(self, results, out_dir, eng=None):
        by = {}
        for r in results:
            if r.get('status') != 'found': continue
            a = by.setdefault(r['area'], {'st': r['area'][3:], 'src': 'kpc_engine parking plug-in (official agency layers)', 'credits': [], 'read': {}, 'parks': {}})
            a['read'][r['ref']] = r['date']
            a['parks'][r['ref']] = [[f['lat'], f['lon'], f"{f['type']}{': ' + f['name'] if f['name'] else ''} ({f['agency']})", f['how']] for f in r['features']]
            for f in r['features']:
                if f['source'] not in a['credits']: a['credits'].append(f['source'])
        for area, d in by.items(): dump(d, f'{out_dir}/access/{area}.json')


class Camping(PointPlugin):
    KIND = 'camping'; USE = 'camping'; GAP_KINDS = ('camping',); RADIUS = 5000

    def write(self, results, out_dir, eng=None):
        by = {}
        for r in results:
            if r.get('status') != 'found': continue
            a = by.setdefault(r['area'], {'area': r['area'], 'inside': {}, 'nearby': {}, 'dayuse': [], 'counts': {}})
            for f in r['features']:
                if f['how'] == 'place':
                    a['inside'].setdefault(r['ref'], []).append({'id': f['source'] + '#' + str(f.get('name')), 'name': f['name'], 'kind': 'campground',
                                                                  'lat': f['lat'], 'lon': f['lon'], 'agency': f['agency'], 'booking': '', 'm_inside': None,
                                                                  'outline': 'place', 'tier': 'inside', 'sites': None, 'notes': [f"source {f['source']}"]})
                else:
                    a['nearby'].setdefault(r['ref'], []).append({'id': f['source'], 'name': f['name'], 'kind': 'campground', 'miles': round(f['m'] / 1609.34, 1),
                                                                  'lat': f['lat'], 'lon': f['lon'], 'how': 'name'})
        for area, d in by.items():
            d['counts'] = {'inside': sum(len(v) for v in d['inside'].values()), 'nearby': sum(len(v) for v in d['nearby'].values())}
            dump(d, f'{out_dir}/campgrounds/{area}.json')


class Trail(PointPlugin):
    KIND = 'trail'; USE = 'trail'; GAP_KINDS = ('trail',); RADIUS = 1500

    def feature(self, src, h, c, how, lat, lon):
        f = super().feature(src, h, c, how, lat, lon)
        g = h['geom']
        f['type'] = 'Trail'
        try: f['pin_line_m'] = geo.pin_relation(lat, lon, g)[1]       # club trail bar: the POTA pin within 200 m of the line
        except Exception: f['pin_line_m'] = None  # noqa: BLE001
        txt = ' '.join(str(v) for v in h['attrs'].values() if isinstance(v, str))
        f['agency_marks_approx'] = bool(rule_g.APPROX_MARK.search(txt))     # national historic trails the agency marks approximate
        nf = (src.get('name_field') or '').lower()
        f['system_names'] = sorted({str(v).strip() for k, v in h['attrs'].items() if isinstance(v, str) and v.strip() and len(v) < 120
                                    and k.lower() != nf and rule_g.SYSTEM_FIELD.search(k)})[:5]      # official tie for a named piece
        if src.get('state_mapping_compilation'): f['state_mapping_compilation'] = True
        f['km_approx'] = (round(_length_km(g), 2) if _length_km(g) is not None else None) if g is not None else None
        f['envelope'] = geo.envelope(g)
        return f

    def write(self, results, out_dir, eng=None):
        by = {}
        for r in results:
            if r.get('status') != 'found': continue
            by.setdefault(r['area'], {})[r['ref']] = [{k: f.get(k) for k in ('name', 'agency', 'how', 'source', 'record_link', 'km_approx', 'envelope', 'pin_line_m', 'trail_bar', 'basis', 'name_tie', 'system_names', 'grade', 'overlap', 'overlap_refs') if f.get(k) is not None} for f in r['features']]
        for area, d in by.items(): dump({'area': area, 'trails': d}, f'{out_dir}/trails/{area}.json')


def _length_km(g):
    try:
        from pyproj import Geod
        return Geod(ellps='WGS84').geometry_length(g) / 1000
    except Exception: return None  # noqa: BLE001
