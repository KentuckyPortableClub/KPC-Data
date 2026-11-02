"""The source registries the plug-ins read (registry/world_sources.json + registry/us_ca_sources.json), and found-layers.
A source is used when it is live-verified ('verified') or answers; 'blocked' / 'error' sources are listed in the report and
tried again when verify.py next marks them good. EU compilation entries are 'approximate' and never give a full YES."""
import json, pathlib
import re as _re

HERE = pathlib.Path(__file__).resolve().parent.parent / 'registry'
FILES = ['pack_sources.json', 'us_ca_sources.json', 'us_ca_trails.json', 'world_sources.json', 'parcel_sources.json']   # the club's approved pack first (registry/_seed_pack.py)
MASTER = 'master_nov1.json'      # round 5: read-only import of the Mapping agent's master workbook (registry/import_master.py); loaded last
RETRY = 'retry.json'             # round 5: hosts / files to retry from another network (registry/import_retry.py)
USABLE = ('approved', 'club', 'verified', 'answers', None, 'imported')   # 'imported' = master-workbook row (ranked after ours)


def norm_url(u):
    u = _re.sub(r'/query/?$', '', (u or '').strip().rstrip('/'), flags=_re.I)
    return _re.sub(r'^https?://', '', u, flags=_re.I).lower()


import re as _re
# layers that answer a pin but are not park land (found by discovery: staff directories, species ranges, county lines ...)
JUNK = _re.compile(r'staff|directory|office|species|swap|sgcn|range_?map|county_?bound|counties|parcel|zoning|road|census|district_?bound|'
                   r'shooting|hunting_?zone|elk_?zone|restrict', _re.I)


EU_COMPILATION = _re.compile(r'://[^/]*\beea\.europa\.eu/|://[^/]*discomap', _re.I)  # EEA / discomap = EU compilation
EU_EEA = set('AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE IS LI NO CH TR'.split())  # EEA data covers these only


class Registry:
    def __init__(self, files=None, extra_found_layers=None):
        self.sources, self.no_rows, self.yes_rows, self.words, self.failed_hosts, self.deny = [], set(), {}, {}, {}, []
        self.annotations, self.park_leads, self.pages, self.portals, self.picture_maps, self.master = {}, {}, [], [], [], {}
        for f in files or [HERE / x for x in FILES + [MASTER]]:
            try: d = json.load(open(f))
            except (OSError, ValueError): continue
            if pathlib.Path(f).name == MASTER:          # master workbook import: ours win on a duplicate; theirs keep wb_status / wb_notes
                self.master = {'workbook': d.get('workbook'), 'counts': d.get('counts')}
                self.annotations = d.get('annotations', {}); self.park_leads = d.get('park_leads', {})
                self.pages, self.portals, self.picture_maps = d.get('pages', []), d.get('portals', []), d.get('picture_maps', [])
                for h, v in d.get('failed_hosts', {}).items(): self.failed_hosts.setdefault(h, v)
                d = {k: v for k, v in d.items() if k in ('sources', 'yes_rows')}
                d['yes_rows'] = {k: v for k, v in d.get('yes_rows', {}).items() if k not in self.yes_rows}
            self.sources += d.get('sources', [])
            for r in d.get('no_rows', []): self.no_rows.add((r[0], r[1], str(r[2])))
            self.yes_rows.update(d.get('yes_rows', {})); self.words.update(d.get('words', {}))
            self.failed_hosts.update(d.get('failed_hosts', {})); self.deny += d.get('deny', [])
        if extra_found_layers: self.sources += extra_found_layers
        for s in self.sources:                          # our entry keeps winning; the workbook's status / notes ride along
            a = self.annotations.get(s.get('id')) or self.annotations.get(s.get('url'))
            if a: s['wb'] = a
        from core import rule_g, rules                  # club, round 3: WDPA / Protected Planet never, not even an official copy
        wd = rules.on('source_policy.wdpa_guard')
        bad = lambda s: (wd and rule_g.cites_wdpa(s)) or bool(rules.forbidden(' '.join(str(s.get(k) or '') for k in ('url', 'layer_name', 'name', 'agency'))))
        self.rejected = [s for s in self.sources if bad(s)]
        self.last_resort = []                           # club rule W-10 (Nov 1): WDPA only as a last resort, approx, labelled
        if rules.wdpa_last_resort_ok():
            try: lr = json.load(open(HERE / 'last_resort.json')).get('sources', [])
            except (OSError, ValueError): lr = []
            for s in lr:
                if rules.forbidden(' '.join(str(s.get(k) or '') for k in ('url', 'layer_name', 'name', 'agency')), allow_wdpa=True): continue
                self.last_resort.append({**s, 'grade': 'approximate', 'last_resort': rules.WDPA_LAST_RESORT, 'use': 'outline'})
        self.sources = [s for s in self.sources if not bad(s)]
        self.yes_rows = {k: [y for y in v if not (wd and rule_g.cites_wdpa(str(y)))] for k, v in self.yes_rows.items()}
        self.yes_rows = {k: v for k, v in self.yes_rows.items() if v}
        try: self.retry = json.load(open(HERE / RETRY)).get('items', [])    # round 5 retry list
        except (OSError, ValueError): self.retry = []
        try: self.rulings = json.load(open(HERE / 'rulings.json')).get('parks', {})
        except (OSError, ValueError): self.rulings = {}
        for s in self.sources:                          # the EU compilation stays approximate even when a club row said YES to it
            if EU_COMPILATION.search(s.get('url') or ''):    # rules: source_policy.eu_compilation_approximate (stays approximate even if off: rows are stamped)
                s['grade'] = 'approximate'; s.setdefault('basis_note', 'EU compilation')

    def status(self, s):
        live = (s.get('live') or {}).get('status')
        if s.get('pack') and live == 'error': return 'dead'          # the club approved it, but the address no longer answers: re-list the server
        return (s.get('verified') or {}).get('status')

    def for_area(self, area, use='outline', include_unverified=False):
        """Sources that cover an area for one use, national ones included: US-KY -> US-KY + US; CA-ON -> CA-ON + CA; CH -> CH;
        world countries also get the EU compilation (approximate)."""
        cc = area.split('-')[0]
        out = []
        for s in self.sources:
            if s.get('use', 'outline') != use and s.get('also') != use: continue
            a = s.get('area') or s.get('cc')
            ok_area = a == area or a == cc or area in (s.get('areas') or []) or (cc in EU_EEA and s.get('cc') == 'EU' and s.get('grade') == 'approximate')
            if not ok_area: continue
            if JUNK.search(s.get('id', '') + ' ' + (s.get('layer_name') or '')) and s.get('use', 'outline') == 'outline': continue
            st = self.status(s)
            if st in USABLE or include_unverified: out.append(s)
        seen, uniq = set(), []
        out.sort(key=lambda s: a_rank(s, area))          # round 5: the entry listed for this exact area wins a duplicate address
        for s in out:
            k = (norm_url(s['url']), s.get('layer'))
            if k not in seen: seen.add(k); uniq.append(s)
        out = uniq
        rank = {'approved': 0, 'verified': 1, 'club': 2, 'answers': 3, None: 4, 'imported': 5}
        out.sort(key=lambda s: (s.get('grade') != 'official', a_rank(s, area), rank.get(self.status(s), 5)))
        return out

    def last_resort_for(self, area):
        """W-10: WDPA layers that may be asked for this area once nothing official answered (country match)."""
        cc = area.split('-')[0]
        return [s for s in self.last_resort if area in (s.get('areas') or []) or cc in (s.get('areas') or []) or '*' in (s.get('areas') or [])]

    def not_usable(self, area):
        cc = area.split('-')[0]
        return [s for s in self.sources if (s.get('area') or s.get('cc')) in (area, cc) and self.status(s) in ('blocked', 'error', 'dead')]

    def is_no(self, ref, layer_url, record):
        """chat 11 said NO to this park + layer + record: never offer it again."""
        return (ref, norm_url(layer_url), str(record)) in self.no_rows

    def retry_for(self, area):
        """Retry-list items (tag 'retry from GitHub network') for a country / area code."""
        cc = area.split('-')[0]
        return [i for i in self.retry if i.get('cc') == cc]

    def leads_for(self, ref):
        """The Mapping agent's per-park matches (master workbook 'Outside agent help'): leads only; 'name only' ones carry a check note."""
        return self.park_leads.get(ref) or []

    def ruling(self, ref):
        """The club's ruling for one park (registry/rulings.json), or None."""
        return self.rulings.get(ref)

    def approved_for(self, ref):
        """[layer, record, record_name] rows a person already said YES to for this park (nothing left to find)."""
        return self.yes_rows.get(ref) or []


def a_rank(s, area):
    return 0 if (s.get('area') or s.get('cc')) == area else 1     # the state / province's own layer before the national one
