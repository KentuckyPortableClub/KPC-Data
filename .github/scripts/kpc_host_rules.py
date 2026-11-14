#!/usr/bin/env python3
"""kpc_host_rules.py (Nov 10): the ONE pre-request host check for every KPC-Data fetch, the same rule as KPC-Links
kpc_master.live_ok. It is asked BEFORE robots.txt and before every request, so a blocked host gets no request of any kind.

  * never contact: the Grant County NM parcel server (services.arcgis.com/33TOOklri9xpic7U) and ncnhde.natureserve.org;
  * every services*.arcgis.com host: services, services1 to services9 and up, and the regional ones (services-eu1 and the like).
    No live read, robots.txt included; their layers come from saved copies only (a person downloads them);
  * the saved-copy-only list: services.arcgis.com, services1.arcgis.com (KPC_SAVED_ONLY_HOSTS ADDS hosts,
    it never drops these; the services*.arcgis.com rule holds whatever the list says). KPC owner, 2026-11-13: apps.fs.usda.gov is
    off the list (its robots.txt answered 403 = no rules file, not a Disallow line); kpc_manners asks it at most once every 10 s.
  * fail closed: an address with no host, or not plain http(s), is refused; the host compared is the one really dialled
    (no port, no user@, no trailing dot, percent-escapes decoded).
www.arcgis.com, hub.arcgis.com and agency servers are not caught (they follow robots.txt; hub portals wait 60 s).
Standard library only, no state.
"""
import os, re, urllib.error, urllib.parse, urllib.request

NEVER_CONTACT = [('services.arcgis.com', '/33TOOklri9xpic7U'), ('ncnhde.natureserve.org', '')]
ARCGIS_SERVICES_HOST_RE = re.compile(r'^services(?:\d+|-[a-z0-9]+)?\.arcgis\.com$')
DEFAULT_SAVED_ONLY = 'services.arcgis.com,services1.arcgis.com'


def saved_only_hosts():
    return {h.strip().lower().rstrip('.') for h in (DEFAULT_SAVED_ONLY + ',' + (os.environ.get('KPC_SAVED_ONLY_HOSTS') or '')).split(',') if h.strip()}


def parts(url):
    u = str(url or '').strip()
    if u.startswith('svc:'): u = u[4:]
    u = u.split('|')[0]
    p = urllib.parse.urlsplit(u if '://' in u else 'https:' + u if u.startswith('//') else 'https://' + u)
    try: host = urllib.parse.unquote(p.hostname or '').lower().rstrip('.')
    except ValueError: host = ''
    return host, p.path or '/'


def _scheme_ok(url):
    u = str(url or '').strip()
    u = u[4:] if u.startswith('svc:') else u
    return '://' not in u or urllib.parse.urlsplit(u).scheme.lower() in ('http', 'https')


def is_arcgis_services_host(host): return bool(ARCGIS_SERVICES_HOST_RE.match(str(host or '').lower()))


def host_ok(url):
    """(ok, why). ok=False means NO request of any kind to this url, robots.txt included."""
    host, path = parts(url)
    if not host or not _scheme_ok(url): return False, f'{str(url)[:80]}: no plain http(s) host (fail closed)'
    for h, p in NEVER_CONTACT:
        if host == h and path.lower().startswith(p.lower()): return False, f'never contact {h}{p}'
    if is_arcgis_services_host(host): return False, f'{host}: services*.arcgis.com, saved copies only (no live read, robots.txt included)'
    if host in saved_only_hosts(): return False, f'{host}: saved copies only, no live read'
    return True, ''


def downgrade(old_url, new_url):
    """True when a redirect goes from an https address to a plain http one (refused, like kpc_manners)."""
    new = urllib.parse.urljoin(str(old_url or ''), str(new_url or ''))
    return urllib.parse.urlsplit(str(old_url or '')).scheme.lower() == 'https' and urllib.parse.urlsplit(new).scheme.lower() == 'http'


class HostRefused(urllib.error.URLError):
    """A request the host rules forbid (an OSError, so a caller's ordinary 'read failed' handling applies)."""


_INSTALLED = []


def install():
    """Owner rule, 2026-11-10: refuse, before any request, a url host_ok() forbids. Wraps urllib's opener (urlopen, every redirect hop)
    and requests' adapter (every hop) once per process, and refuses an https -> http redirect hop. For the fetchers that do not go through kpc_manners. Fails closed."""
    if _INSTALLED: return
    _INSTALLED.append(1)
    o_open = urllib.request.OpenerDirector.open

    def open_(self, fullurl, *a, **k):
        ok, why = host_ok(getattr(fullurl, 'full_url', fullurl))
        if not ok: raise HostRefused(why)
        return o_open(self, fullurl, *a, **k)
    urllib.request.OpenerDirector.open = open_
    o_redir = urllib.request.HTTPRedirectHandler.redirect_request

    def redirect_request(self, req, fp, code, msg, headers, newurl):   # no https -> http downgrade on a redirect hop
        if downgrade(req.full_url, newurl): raise HostRefused(f'redirect from https to http refused: {str(newurl)[:80]}')
        return o_redir(self, req, fp, code, msg, headers, newurl)
    urllib.request.HTTPRedirectHandler.redirect_request = redirect_request
    try: import requests.adapters as _ra, requests.sessions as _rs
    except Exception: return   # noqa: BLE001  (requests is not installed: nothing to wrap)
    o_send = _ra.HTTPAdapter.send

    class _ReqRefused(HostRefused, _ra.ConnectionError):   # a requests caller's ordinary 'request failed' handling applies
        pass

    def send(self, request, *a, **k):
        ok, why = host_ok(request.url)
        if not ok: raise _ReqRefused(why)
        return o_send(self, request, *a, **k)
    _ra.HTTPAdapter.send = send
    o_target = _rs.SessionRedirectMixin.get_redirect_target

    def get_redirect_target(self, resp):
        t = o_target(self, resp)
        if t and downgrade(resp.url, t): raise _ReqRefused(f'redirect from https to http refused: {str(t)[:80]}')
        return t
    _rs.SessionRedirectMixin.get_redirect_target = get_redirect_target


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
