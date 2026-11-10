#!/usr/bin/env python3
"""KPC engine (KPC_10_Engine_Spec.md + KPC_10_Finder3_Spec.md). One command, many plug-ins, the engine decides nothing.

  python kpc_engine.py gaps   --data D --links L --pota P --out OUT [--areas US-KY,CA-ON,GB]
  python kpc_engine.py run    --data D --links L --pota P --out OUT [--areas ..] [--kinds outline,docs,parking,camping,trail,hours,fees,closures]
                              [--max-minutes 52] [--resume] [--limit N] [--workers 8] [--steps L0,L1,L2,L3,L4,L5] [--offline]
  python kpc_engine.py selftest            (offline: fixtures only, no network)
  python kpc_engine.py doctor --links L --data D --out OUT [--tasks nos,release,approvals,fers-ids,line,stuck,storage]
                                           (v0.5.0 key doctor: read-only check-up of the answer-key line)
  python kpc_engine.py verify-registry ... (runs registry/verify.py)

Exit 0 = done; 3 = stopped at --max-minutes (run again with --resume). Writes ONLY inside --out."""
import argparse, collections, csv, json, os, pathlib, sys, threading, time

VERSION = '0.5.0'
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core import adapters, agencies, board, checks, gaps as gaps_mod, gis, geo, names, passes, priority, grading, scope, workers   # noqa: E402
from core import rules as scope_cfg                                                                             # noqa: E402
from core.findings import Findings                                                                               # noqa: E402
from core.polite import Polite                                                                                   # noqa: E402
from core.registry import Registry                                                                               # noqa: E402
from plugins.outline import Outline                                                                              # noqa: E402
from plugins.docs import Docs                                                                                    # noqa: E402
from plugins.points import Parking, Camping, Trail                                                               # noqa: E402
from plugins.ky_info import Hours, Fees, Closures                                                                # noqa: E402
from plugins import stubs                                                                                        # noqa: E402

ORDER = ['outline', 'docs', 'parking', 'camping', 'trail', 'hours', 'fees', 'closures']   # outline first: its shapes feed 'place' ties


class Engine:
    def __init__(self, a):
        self.a = a
        self.out = pathlib.Path(a.out).resolve(); self.out.mkdir(parents=True, exist_ok=True)
        self.P = Polite(cache_dir=a.cache or str(self.out / '.cache'), offline=a.offline)
        self.club = adapters.Club(a.data, a.links, a.pota)
        self.findings = Findings(self.out)
        regs = [HERE / 'registry' / 'pack_sources.json', HERE / 'registry' / 'us_ca_sources.json', HERE / 'registry' / 'us_ca_trails.json', HERE / 'registry' / 'world_sources.json', HERE / 'registry' / 'parcel_sources.json', HERE / 'registry' / 'master_nov1.json']   # the club pack first; the master-workbook import last (round 5)
        self.found_layers = self._load('found-layers.json', {'layers': []})
        self.registry = Registry(regs)
        self.agencies = agencies.AgencyBook(self.out, regs, (pathlib.Path(a.links) / '.claude/build/research/agency-atlas') if a.links else None)
        self.deadline = time.time() + a.max_minutes * 60 if a.max_minutes else None
        self.P.deadline = self.deadline   # Nov 10: no request past the budget (rows), then POST_GRACE more for the checks and writes
        self.n_workers, self.resume = a.workers, a.resume
        self.steps = set((a.steps or 'L0,L1,L2,L3,L4,L5').split(','))
        self.org_cache, self.picture_maps, self.parcels, self.typos, self.fixes = {}, [], [], [], []
        self._lk = threading.Lock(); self._walk = {}; self._shapes = {}; self._pages = {}
        self.docs = Docs()
        self.parks_all = {}

    def _load(self, name, default):
        p = self.out / name
        try: return json.load(open(p)) if p.exists() else default
        except ValueError: return default

    # ---- what plug-ins ask the engine for
    def park(self, row): return {**(self.parks_all.get(row['area']) or {}).get(row['ref'], {}), 'ref': row['ref']}
    def step_off(self, step, area): return step not in self.steps

    def found_layers_for(self, area):
        return [L for L in self.found_layers['layers'] if L.get('area') in (area, area.split('-')[0])]

    def add_found_layer(self, src, area, how):
        with self._lk:
            if any(L['url'] == src['url'] for L in self.found_layers['layers']): return
            self.found_layers['layers'].append({**{k: v for k, v in src.items() if k != 'verified'}, 'area': area, 'how': how, 'date': time.strftime('%Y-%m-%d'),
                                                'id': f"found {src['url']}"})
        self.findings.add(by='outline', kind='found-layer', url=src['url'], agency=src.get('agency'), note=f'{how} ({area})')

    def agency_roots(self, agency):
        if not agency: return []
        e = self.agencies.d.get(agency) or {}
        return [r for r in e.get('roots', []) if '/rest/services' in r]

    def walk(self, root):
        with self._lk:
            if root in self._walk: return self._walk[root]
        lays = gis.arcgis_walk(self.P, root, depth=1)
        with self._lk: self._walk[root] = lays
        return lays

    def discover_mod(self):
        from registry import discover_usca
        return discover_usca

    def official_page(self, row):
        k = (row['area'], row['ref'])
        if k not in self._pages:
            from core.notes import Notes
            pg, how = self.docs.find_page(self, row, self.park(row), Notes(), deep=False)
            self._pages[k] = (pg.final_url or pg.url) if pg else None
        return self._pages[k]

    def picture_map(self, row, p, u, page):
        with self._lk:
            if not any(m['url'] == u and m['ref'] == row['ref'] for m in self.picture_maps):
                self.picture_maps.append({'ref': row['ref'], 'area': row['area'], 'park': p.get('n'), 'url': u, 'page': page, 'date': time.strftime('%Y-%m-%d'),
                                          'note': 'picture map: listed for the picture-map saver, never traced by the engine'})

    def parcels_note(self, row, msg):
        with self._lk: self.parcels.append({'ref': row['ref'], 'area': row['area'], 'status': 'not run', 'why': msg, 'grade': 'approximate'})

    def fix(self, row, p, link, msg):
        with self._lk:
            if not any(f['ref'] == row['ref'] and f['link'] == link and f['problem'] == msg for f in self.fixes):
                self.fixes.append({'ref': row['ref'], 'area': row['area'], 'park': p.get('n'), 'link': link, 'problem': msg, 'date': time.strftime('%Y-%m-%d')})

    def pin_typo_check(self, row, p, best):
        """R-G13: a name match far from the pin is a pin typo only when an official POINT with the park's name sits on the record."""
        g = best['hit'].get('geom')
        if g is None or not row['area'].startswith(('US-', 'CA-')): return None
        words = names.core_words(p.get('n') or '')
        for use in ('parking', 'camping'):
            for src in self.registry.for_area(row['area'], use):
                if not src.get('name_field') or src['kind'] != 'arcgis': continue
                hits, err = gis.by_name(self.P, src, words, ref_=p['ref'])
                for h in hits or []:
                    pt = h.get('geom')
                    if pt is None or not names.words_in_text(words, names.all_text(h['attrs'])): continue
                    if g.buffer(0.005).contains(pt):
                        km = round(geo.haversine_m(float(p['lat']), float(p['lon']), pt.y, pt.x) / 1000, 1)
                        t = {'ref': row['ref'], 'area': row['area'], 'park': p.get('n'), 'pota_pin': [p['lat'], p['lon']], 'official_point': [round(pt.y, 6), round(pt.x, 6)],
                             'km': km, 'source': src['id'], 'point_name': h.get('name'), 'record': best['name'], 'record_layer': best['src'].get('id'),
                             'rule': 'R-G13', 'pin_moves': False, 'note': 'POTA pins never move: this is a question for the club, not a pin change'}
                        from core import rule_g
                        slip = rule_g.pin_typo((float(p['lat']), float(p['lon'])), (pt.y, pt.x))
                        if slip: t['looks_like'] = slip['why']
                        with self._lk: self.typos.append(t)
                        return t
        return None

    def outline_shape(self, row):
        k = (row['area'], row['ref'])
        if k in self._shapes: return self._shapes[k]
        p = self.park(row)
        shp = None
        if p.get('lat') not in (None, ''):
            o = Outline()
            from core.notes import Notes
            words = names.core_words(p.get('n') or '')
            for src in self.registry.for_area(row['area'], 'outline')[:4]:
                got = o._ask(self, src, p, float(p['lat']), float(p['lon']), words, Notes(), [], 'L0', by_name=False)
                good = [c for c in got if c['tier'] in ('T-1', 'T-2') and c['inside'] and c['hit'].get('geom') is not None]
                if good: shp = good[0]['hit']['geom']; break
        self._shapes[k] = shp
        return shp


PLUGINS = {'outline': Outline, 'docs': Docs, 'parking': Parking, 'camping': Camping, 'trail': Trail, 'hours': Hours, 'fees': Fees, 'closures': Closures}


def gap_rows(G):
    rows = []
    for area, parks in G.items():
        for ref, r in parks.items(): rows.append({'area': area, 'ref': ref, **r})
    return rows


def cmd_gaps(a, eng=None):
    eng = eng or Engine(a)
    areas = workers.areas_from_env([x.strip() for x in (a.areas or '').split(',') if x.strip()])
    if not areas:   # blank --areas / AREAS = every area in the club order, never 'do nothing'
        areas = eng.club.all_areas()
        print(f'areas: none given, running all {len(areas)} areas in the club order', file=sys.stderr)
    prev = eng._load('gaps.json', {})
    G, parks_all = gaps_mod.build(eng.club, areas, eng.out, a.limit)
    eng.parks_all = parks_all
    return eng, G, prev


def cmd_run(a):
    eng, G, prev = cmd_gaps(a)
    kinds = [k for k in (a.kinds.split(',') if a.kinds else ORDER) if k in PLUGINS]
    rows = gap_rows(G)
    results, stats, timed = {}, {}, False
    for k in ORDER:
        if k not in kinds: continue
        pl = PLUGINS[k]() if k != 'docs' else eng.docs
        mine = [r for r in rows if pl.wants(r)]
        # the scope guard: a row outside the plug-in's scope never reaches it
        for r in mine: scope.guard('docs' if k == 'docs' else k, r)
        if not mine: continue
        groups = priority.order_groups(agencies.group(mine), k)   # seeded gaps first (round 5), then the US/CA club order
        for r in mine:
            r.setdefault('park_class', priority.park_class(r)[1])
            sd = priority.seed_of(r, k)[1]
            if sd: r.setdefault('work_order_seed', sd)
        print(f'[{k}] {len(mine)} rows in {len(groups)} agency groups', flush=True)
        eng.P.deadline = eng.deadline   # Nov 10: the rows' own budget (the checks below get POST_GRACE_S more)
        final, st = passes.two_passes(eng, pl, groups)
        final = [r for r in final if r]
        postprocess(k, final)
        if k == 'trail': write_fers(eng.out)
        if eng.deadline: eng.P.deadline = max(eng.deadline, time.time()) + POST_GRACE_S   # Nov 10: the URL checks get a short, fixed grace past the budget
        kept, problems = checks.check_rows(eng.P, [dict(r, park=r.get('park')) for r in final if r.get('status') in ('found', 'candidate')], eng.parks_all,
                                           check_urls=not a.offline)
        rest = [r for r in final if r.get('status') not in ('found', 'candidate')]
        for pr in problems: pr['status'] = 'check failed'
        json.dump(problems, open(eng.out / f'check-problems-{k}.json', 'w'), indent=1, ensure_ascii=False)
        final = kept + rest + problems
        pl.write(final, str(eng.out), eng) if k in ('outline', 'docs', 'parking', 'camping', 'trail') else pl.write(final, str(eng.out))
        checks.spot_check(final, eng.out / f'spot-check-{k}.md', k)
        results[k] = final; stats[k] = {**st, 'grade': grading.report(k, final, pl.grade(final, eng))}
        timed = timed or st.get('timed_out')
        if timed: break
    finish(eng, G, prev, results, stats)
    return 3 if timed else 0


POST_GRACE_S = 300   # Nov 10: after the rows' budget, at most 5 min of URL checks per kind (a check not made is 'not checked', never 'dead')


FER_WAITING = []      # 2-fer / 3-fer suggestions from the last postprocess('trail'): waiting room only, never automatic


def write_fers(out):
    """fers-waiting-room.json: suggestions for chat 8 + chat 11 (Overlapping boundaries). The engine never adds a 2-fer."""
    from core import fers
    if not FER_WAITING: return
    json.dump({'about': 'Possible 2-fers / 3-fers (label: ' + fers.LABEL + '). Never automatic: chat 8 + chat 11 check each by hand. '
               'Rules: trails with no land boundary count within 100 ft of the line (water trails: 100 ft of the water\'s edge); a wild / '
               'scenic river corridor uses its own boundary; parks that only touch do not count; a 3-fer needs a spot within 100 ft of the '
               'trail inside the overlap patch.', 'rows': FER_WAITING}, open(pathlib.Path(out) / 'fers-waiting-room.json', 'w'), indent=1)


def postprocess(k, final):
    """Whole-run rules applied after both passes (also by `grade` on saved output)."""
    from core import rules
    if k in ('parking', 'camping') and rules.on('checks.resolve_duplicate_facilities'):   # chat 11: 0 duplicate facilities -> one facility under 2+ parks stays only with the nearest pin
        from core import rule_g
        rule_g.resolve_duplicates(final)
    if k == 'trail':                # club, round 4: the trail bar; a trail in 2+ parks is "Overlapping boundaries" -> waiting room only
        from core import rule_g, fers
        rule_g.apply_trail_bar(final)
        FER_WAITING[:] = fers.from_trail_rows(final)
    if k == 'outline' and rules.on('checks.containers'):          # Rule G: one record under several parks' pins is a container -> evidence, never a question
        from core import rule_g
        live = [r for r in final if r.get('status') in ('found', 'candidate')]
        for (lay, rec), refs in rule_g.containers(live).items():
            same_park = len({(r.get('park') or '').lower() for r in live if r.get('layer') == lay and str(r.get('record')) == rec}) == 1
            if same_park: continue            # one park filed under 2+ states (Cumberland Gap KY / TN / VA) is not a container
            for r in live:
                if r.get('layer') == lay and str(r.get('record')) == rec:
                    r.update(status='evidence', rule_g='UNLIKELY', rule_g_why=f'container: record under {len(refs)} parks ({", ".join(refs[:5])})',
                             whynot={'tag': f'UNLIKELY only (evidence, never a question): container under {len(refs)} parks', 'date': r.get('date')})
    rules.stamp_rows(k, final)       # rows that exist only because a source rule was switched off: 'non-official: ...', grade approx
    return final


def cmd_grade(a):
    """Re-run only the graders on saved output (<out>/work/<kind>/results-*.jsonl): no web requests.
    Writes grades-regrade.md / .json next to the run's own grades.md (which is left as it was)."""
    from core import export
    out = pathlib.Path(a.out); grades = {}
    kinds = [k for k in (a.kinds.split(',') if a.kinds else ORDER) if k in PLUGINS]
    for k in kinds:
        final = export._rows(out, k, post=False)
        if not final: continue
        postprocess(k, final)
        if k == 'trail': write_fers(out)
        pl = PLUGINS[k]()
        grades[k] = grading.report(k, final, pl.grade(final, None))
    json.dump({'grades': grades, 'config': scope_cfg.active_summary()}, open(out / 'grades-regrade.json', 'w'), indent=1)
    (out / 'grades-regrade.md').write_text(scope_cfg.banner_md() + grading.to_markdown(grades), encoding='utf-8')
    for k, g in grades.items(): print(f"{k}: {g.get('verdict')}")
    return 0


def finish(eng, G, prev, results, stats):
    eng.P.write_blocked(eng.out)
    with open(eng.out / 'fixes.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, ['ref', 'area', 'park', 'link', 'problem', 'date']); w.writeheader(); w.writerows(eng.fixes)
    json.dump({'typos': eng.typos}, open(eng.out / 'pin-typos.json', 'w'), indent=1, ensure_ascii=False)
    json.dump(eng.found_layers, open(eng.out / 'found-layers.json', 'w'), indent=1, ensure_ascii=False)
    eng.agencies.save()
    # round 5: the retry list (tag 'retry from GitHub network') and the seeded work order travel with every run
    json.dump({'about': 'Retry list: the same honest request once from this network; never bypass a 403 / robot check / sign-in.',
               'items': eng.registry.retry}, open(eng.out / 'retry-list.json', 'w'), indent=1, ensure_ascii=False)
    json.dump({'seeds': priority.seeds(), 'seeded_rows': collections.Counter(r.get('work_order_seed') for rs in results.values() for r in rs if r and r.get('work_order_seed'))},
              open(eng.out / 'work-order.json', 'w'), indent=1, ensure_ascii=False)
    # one spot-check.md: 20 rows over all kinds
    allrows = [r for rs in results.values() for r in rs]
    checks.spot_check(allrows, eng.out / 'spot-check.md', 'all kinds', n=20)
    grades = {k: s.get('grade') for k, s in stats.items()}
    json.dump({'grades': grades, 'config': scope_cfg.active_summary(), 'passes': {k: {x: s.get(x) for x in ('pass1', 'pass2', 'pass2_solved', 'timed_out')} for k, s in stats.items()},
               'stubs': {s.KIND: s.WHY for s in stubs.ALL}}, open(eng.out / 'grades.json', 'w'), indent=1)
    (eng.out / 'grades.md').write_text(scope_cfg.banner_md() + grading.to_markdown(grades), encoding='utf-8')
    extra = '## Rules for this run\n\n' + scope_cfg.banner_md() + '## Stubs\n\n' + '\n'.join(f'- {s.KIND}: {s.WHY}' for s in stubs.ALL)
    board.write(eng.out, G, prev, results, stats, eng.P.blocked, extra)


def cmd_doctor(a):
    """v0.5.0 key doctor: reads --links / --data, writes ONLY <out>/key-doctor/. Exit 1 when something is red."""
    from core import key_doctor
    if a.data:   # KPC-Data is read here too: never write inside it
        dd, o = pathlib.Path(a.data).resolve(), pathlib.Path(a.out).resolve()
        if o == dd or dd in o.parents: print(f'refused: --out {o} is inside the --data checkout (the doctor only reads it)'); return 2
    tasks = [t.strip() for t in a.tasks.split(',') if t.strip()] or None
    for nm, d in (('--links', a.links), ('--data', a.data)):
        if d and not pathlib.Path(d).is_dir(): print(f'::warning title=Key doctor::{nm} {d} is not a folder: its checks are skipped')
    res = key_doctor.run(a.links or None, a.data or None, a.out, tasks)
    for line in key_doctor.lines(res): print(line)
    print(f"key doctor (engine {VERSION}): wrote {pathlib.Path(a.out).resolve() / 'key-doctor'}")
    return key_doctor.exit_code(res)


def cmd_selftest(a):
    import subprocess
    return subprocess.call([sys.executable, '-m', 'pytest', '-q', str(HERE / 'tests')], cwd=str(HERE))


def main(argv=None):
    from core import config
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['gaps', 'run', 'selftest', 'verify-registry', 'export', 'grade', 'doctor'])
    ap.add_argument('--data', default=os.environ.get('KPC_DATA', '')); ap.add_argument('--links', default=os.environ.get('KPC_LINKS', ''))
    ap.add_argument('--pota', default=os.environ.get('KPC_POTA', '')); ap.add_argument('--out', default='engine-out')
    ap.add_argument('--cache', default=os.environ.get('KPC_CACHE', '')); ap.add_argument('--areas', default='', help='comma list; leave blank for EVERY area in the club order')
    ap.add_argument('--kinds', default=''); ap.add_argument('--max-minutes', type=float, default=0)
    ap.add_argument('--resume', action='store_true'); ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--workers', type=int, default=8); ap.add_argument('--steps', default='')
    ap.add_argument('--offline', action='store_true'); ap.add_argument('--name', default='engine')
    ap.add_argument('--rules', default='', help='rules file (default config/rules.json)')
    ap.add_argument('--enable', action='append', default=[], help='switches to turn on, e.g. hours_rules.reject_fragments')
    ap.add_argument('--disable', action='append', default=[], help='switches to turn off, e.g. closures or source_policy.never_use.google')
    ap.add_argument('--scope', action='append', default=[], help='plug-in areas, e.g. hours=US-KY,US-TN (US-* / CA-* / * allowed)')
    ap.add_argument('--set', action='append', default=[], dest='set_', help='grader numbers, e.g. grader.rg12_m=150')
    ap.add_argument('--tasks', default='', help='doctor: comma list of nos,release,approvals,fers-ids,line,stuck,storage (default all)')
    ap.add_argument('--check-all', default='', help='kinds to check on EVERY park in scope, not only gap rows (audit / sample runs)')
    a, rest = ap.parse_known_args(argv)
    if a.links and a.cmd != 'selftest':   # KPC-Links is read-only (club, round 3): never write results inside it
        lk, o = pathlib.Path(a.links).resolve(), pathlib.Path(a.out).resolve()
        if o == lk or lk in o.parents:
            print(f'refused: --out {o} is inside the read-only KPC-Links checkout ({config.KPC_LINKS_REPO})'); return 2
    if a.cmd == 'selftest': return cmd_selftest(a)
    scope_cfg.load(a.rules or None, a.enable, a.disable, a.scope, a.set_)
    if a.cmd in ('run', 'grade', 'gaps', 'export', 'doctor'):
        print(scope_cfg.banner_text(), flush=True)
        scope_cfg.write_active(a.out)
    if a.check_all:
        from core import gaps as _g; _g.CHECK_ALL.update(k.strip() for k in a.check_all.split(',') if k.strip())
    if a.cmd == 'export':       # hand-back files in the club's intake shapes -> <out>/handback/
        from core import export
        wrote, flags = export.export(a.out, a.name)
        print('handback:', ', '.join(f'{k} {v}' for k, v in wrote.items()) + (' | closest shapes (no sample): ' + ', '.join(flags) if flags else '')); return 0
    if a.cmd == 'grade': return cmd_grade(a)
    if a.cmd == 'doctor': return cmd_doctor(a)
    if a.cmd == 'verify-registry':
        import subprocess
        return subprocess.call([sys.executable, str(HERE / 'registry' / 'verify.py')] + rest)
    if a.cmd == 'gaps':
        eng, G, prev = cmd_gaps(a); print(f"gaps: {sum(len(v) for v in G.values())} parks with a gap -> {eng.out / 'gaps.json'}"); return 0
    return cmd_run(a)


if __name__ == '__main__':
    sys.exit(main())
