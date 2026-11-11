#!/usr/bin/env python3
"""Picture tracer: every web host a run can contact, and why (KPC owner, 2026-11-11). Standard library only; it never makes a request.

The tracer (kpc_trace_picture.py) reads basemaps only from ALLOWED_BASEMAP_HOSTS (its own allow list, checked before every request
and every robots.txt redirect: PoliteHttp.check_host). Each host's robots.txt is read once per run and obeyed on every path.
The workflow step before it (kpc_picture_geo.py) downloads each map's own source_url (the agency PDF) once, through kpc_manners,
which asks kpc_host_rules.host_ok first (never-contact and saved-only hosts get no request, robots.txt included).

  python3 kpc_trace_hosts.py <fixtures folder> [--offline]     (the same as: kpc_trace_picture.py --list-hosts --base <folder>)
prints, per host: what it is fetched for, for how many maps, whether robots.txt is read first, and what the guards say.
"""
import importlib.util, json, os, sys
from urllib.parse import urlparse

# ---- the basemap sources (the tracer imports these; one place only)
TIGER = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer"
TIGER_HYDRO = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Hydro/MapServer"
NHD = "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer"
PLSS = "https://gis.blm.gov/arcgis/rest/services/Cadastral/BLM_Natl_PLSS_CadNSDI/MapServer"
NRN = "https://geo.statcan.gc.ca/geo_wa/rest/services/NRN-RRN/nrn_rrn/MapServer"
ALLOWED_BASEMAP_HOSTS = {
    "tigerweb.geo.census.gov",   # US Census TIGERweb (roads; Nov 11: also its hydrography, the water lines and shores)
    "hydro.nationalmap.gov",     # USGS NHD
    "gis.blm.gov",               # BLM CadNSDI PLSS
    "geo.statcan.gc.ca",         # Canada National Road Network (NRN)
}
FORBIDDEN_HOST_WORDS = ("openstreetmap", "osm", "overpass", "google", "googleapis",
                        "mapbox", "bing", "here.com", "arcgisonline")

SOURCES = {   # prefix -> [(host, what it is fetched for)]
    "US": [("tigerweb.geo.census.gov", "roads (TIGERweb Transportation layers 2, 6, 8) and water lines / lake shores (TIGERweb Hydro, "
                                       "layers found by name from its layer list)"),
           ("hydro.nationalmap.gov", "USGS NHD flowlines: only its robots.txt is read; it answers 403 today (= Disallow), so no data "
                                     "request follows and water comes from TIGERweb"),
           ("gis.blm.gov", "BLM PLSS section corners (land survey)")],
    "CA": [("geo.statcan.gc.ca", "Canada National Road Network: a feature count per province, then the road layers of the provinces "
                                 "that have roads in the box")],
}


def host_rules():
    """kpc_host_rules.py (two folders up, in .github/scripts) when it is there; None otherwise."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kpc_host_rules.py')
    if not os.path.exists(p):
        return None
    spec = importlib.util.spec_from_file_location('kpc_host_rules_th', p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def tracer_allows(host):
    """The tracer's own rule (PoliteHttp.check_host): only the allow list, never a forbidden word."""
    h = (host or '').lower()
    return h in ALLOWED_BASEMAP_HOSTS and not any(w in h for w in FORBIDDEN_HOST_WORDS)


def is_never_contact(host):
    h = (host or '').lower().rstrip('.')
    return (h.startswith('services') and h.endswith('.arcgis.com')) or h in ('apps.fs.usda.gov', 'ncnhde.natureserve.org')


def _load(p, d):
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return d


def plan(base, offline=False):
    """Which hosts a run on this fixtures folder would contact. Reads index.json, pins.json and cache/ only. Returns
    {'hosts': {host: {...}}, 'maps': n, 'geopdf': n, 'cached': n, 'no_pin': n, 'other_prefix': n}."""
    idx = _load(os.path.join(base, 'index.json'), {}) or {}
    if isinstance(idx, dict) and isinstance(idx.get('maps'), list):
        idx = {r.get('ref'): r for r in idx['maps'] if isinstance(r, dict)}
    elif isinstance(idx, list):
        idx = {r.get('ref'): r for r in idx if isinstance(r, dict)}
    pins = _load(os.path.join(base, 'pins.json'), {}) or {}
    out = {'hosts': {}, 'maps': 0, 'geopdf': 0, 'cached': 0, 'no_pin': 0, 'other_prefix': 0}
    HR = host_rules()

    def add(host, what, ref, kind):
        e = out['hosts'].setdefault(host, {'what': what, 'kind': kind, 'refs': [], 'robots': True})
        if ref not in e['refs']:
            e['refs'].append(ref)
    for ref, row in sorted((k, v) for k, v in idx.items() if k):
        row = row if isinstance(row, dict) else {}
        out['maps'] += 1
        su = str(row.get('source_url') or '')
        if su.startswith('http'):   # kpc_picture_geo.py, the step BEFORE the tracer (not part of the tracer run itself)
            add((urlparse(su).hostname or '').lower(), "the map's own source file (kpc_picture_geo.py, before the tracer: PDF page "
                "drawn sharp + GeoPDF coordinates)", ref, 'geo')
        if ref not in pins:
            out['no_pin'] += 1
            continue
        if (row.get('geo') or {}).get('affine'):
            out['geopdf'] += 1           # placed by its own coordinates: no basemap request
            continue
        cache = os.path.join(base, 'cache', ''.join(c if c.isalnum() or c in '-_' else '_' for c in ref) + '_basemap.json')
        if os.path.exists(cache):
            d = _load(cache, {}) or {}
            if offline or not d.get('skipped'):
                out['cached'] += 1       # read from the saved basemap (a normal run still asks again when it is partial)
                continue
        if offline:
            continue                     # --offline: no request; the map becomes an 'offline:' ERROR row
        pre = ref.split('-')[0].upper()
        if pre not in SOURCES:
            out['other_prefix'] += 1
            continue
        for host, what in SOURCES[pre]:
            add(host, what, ref, 'basemap')
    for host, e in out['hosts'].items():
        e['tracer_allow_list'] = tracer_allows(host) if e['kind'] == 'basemap' else None
        e['never_contact'] = is_never_contact(host)
        if HR is not None:
            ok, why = HR.host_ok('https://' + host + '/')
            e['host_rules'] = 'allowed' if ok else f'REFUSED ({why})'
        else:
            e['host_rules'] = 'kpc_host_rules.py not found here'
    return out


def report(base, offline=False):
    p = plan(base, offline)
    L = [f"hosts a {'--offline ' if offline else ''}run on {base} can contact (no request was made to find this out)",
         f"maps: {p['maps']}; placed by their own GeoPDF coordinates (no basemap): {p['geopdf']}; basemap read from cache/: {p['cached']}; "
         f"no pin: {p['no_pin']}; no basemap source for the prefix: {p['other_prefix']}"]
    for kind, title in (('basemap', 'TRACER (kpc_trace_picture.py) basemap requests'),
                        ('geo', 'BEFORE THE TRACER (kpc_picture_geo.py) map-file downloads, only if that step is run')):
        L.append('')
        L.append(title + ':')
        rows = sorted(((h, e) for h, e in p['hosts'].items() if e['kind'] == kind), key=lambda t: (-len(t[1]['refs']), t[0]))
        if not rows:
            L.append('  (none)')
        for h, e in rows:
            guard = (f"tracer allow list: {'allowed' if e['tracer_allow_list'] else 'REFUSED'}; " if e['tracer_allow_list'] is not None else '')
            L.append(f"  {h}  [{len(e['refs'])} map(s)]  robots.txt read first: yes; {guard}kpc_host_rules: {e['host_rules']}; "
                     f"never-contact host: {'YES' if e['never_contact'] else 'no'}")
            L.append(f"      for: {e['what']}")
    nc = sorted(h for h, e in p['hosts'].items() if e['never_contact'])
    L.append('')
    L.append('services*.arcgis.com / apps.fs.usda.gov / ncnhde among them: ' + (', '.join(nc) + ' (refused before any request, robots.txt '
             'included)' if nc else 'none'))
    return '\n'.join(L) + '\n', p


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    off = '--offline' in a
    a = [x for x in a if x != '--offline']
    if len(a) != 1:
        print(__doc__)
        return 2
    txt, _ = report(a[0], off)
    sys.stdout.write(txt)
    return 0


if __name__ == '__main__':
    sys.exit(main())
