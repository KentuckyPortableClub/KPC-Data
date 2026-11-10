#!/usr/bin/env python3
"""kpc_host_rules.py (Nov 10): the ONE pre-request host check for every KPC-Data fetch, the same rule as KPC-Links
kpc_master.live_ok. It is asked BEFORE robots.txt and before every request, so a blocked host gets no request of any kind.

  * never contact: the Grant County NM parcel server (services.arcgis.com/33TOOklri9xpic7U) and ncnhde.natureserve.org;
  * every services*.arcgis.com host: services, services1 to services9 and up, and the regional ones (services-eu1 and the like).
    No live read, robots.txt included; their layers come from saved copies only (a person downloads them);
  * the saved-copy-only list: services.arcgis.com, services1.arcgis.com, apps.fs.usda.gov (KPC_SAVED_ONLY_HOSTS adds hosts;
    the services*.arcgis.com rule holds even if that list is emptied).
www.arcgis.com, hub.arcgis.com and agency servers are not caught (they follow robots.txt; hub portals wait 60 s).
Standard library only, no state.
"""
import os, re, urllib.parse

NEVER_CONTACT = [('services.arcgis.com', '/33TOOklri9xpic7U'), ('ncnhde.natureserve.org', '')]
ARCGIS_SERVICES_HOST_RE = re.compile(r'^services(?:\d+|-[a-z0-9]+)?\.arcgis\.com$')
DEFAULT_SAVED_ONLY = 'services.arcgis.com,services1.arcgis.com,apps.fs.usda.gov'


def saved_only_hosts():
    return {h.strip().lower() for h in (os.environ.get('KPC_SAVED_ONLY_HOSTS') or DEFAULT_SAVED_ONLY).split(',') if h.strip()}


def parts(url):
    u = str(url or '').strip()
    if u.startswith('svc:'): u = u[4:]
    u = u.split('|')[0]
    p = urllib.parse.urlsplit(u if '://' in u else 'https://' + u)
    return (p.hostname or '').lower(), p.path or '/'


def is_arcgis_services_host(host): return bool(ARCGIS_SERVICES_HOST_RE.match(str(host or '').lower()))


def host_ok(url):
    """(ok, why). ok=False means NO request of any kind to this url, robots.txt included."""
    host, path = parts(url)
    for h, p in NEVER_CONTACT:
        if host == h and path.lower().startswith(p.lower()): return False, f'never contact {h}{p}'
    if is_arcgis_services_host(host): return False, f'{host}: services*.arcgis.com, saved copies only (no live read, robots.txt included)'
    if host in saved_only_hosts(): return False, f'{host}: saved copies only, no live read'
    return True, ''


def who_for(url, robots_ok=None, file_url=None):
    """('bot' | 'person' | 'never', why), the same words as the needs-download list. Nov 10 (the same rule as KPC-Links
    kpc_master.who_for): a layer a bot may not read whose OFFICIAL DIRECT FILE sits on a host a bot may fetch is a bot's row."""
    host, path = parts(url)
    for h, p in NEVER_CONTACT:
        if host == h and path.lower().startswith(p.lower()): return 'never', f'never contact {h}{p}: no request of any kind, by a bot or a person'
    ok, why = host_ok(url)
    if ok and (robots_ok is None or robots_ok(url)): return 'bot', ''
    why = why + ': a person downloads it in a browser' if not ok else f'{host}: robots.txt does not allow a bot to read it (a 403 counts as no): a person downloads it'
    if file_url and host_ok(file_url)[0] and (robots_ok is None or robots_ok(file_url)):
        return 'bot', f'the official direct file is on {parts(file_url)[0]}, which a bot may fetch: the master step downloads it'
    return 'person', why
