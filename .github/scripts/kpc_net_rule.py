#!/usr/bin/env python3
"""THE SITE RULE, as one table (owner, 26 Nov 2026, 9:46 and 9:49 PM: "We only avoid if robots.txt say we can't.";
"Avoid servers if they say no plain and simple."; "it thinks it's blocked but it's not").

A site is BLOCKED only when its robots.txt has a real Disallow line that covers the address. Nothing else is a block.
Everything else is "not now" at most, and "not now" is never saved as blocked, and never carried into the next run.

This file decides. It never fetches. kpc_manners.py (the fetcher), kpc_park_pages.py (the reader), the own-page finder,
the documents bot and the status page all ask it. Standard library only.
"""

# ------------------------------------------------------------------------- DECISIONS FOR THE OWNER TO CONFIRM (26 Nov)
# Each is ONE value: change the value here, nothing else. 'no-rules' = allowed; 'busy' = not this run, asked again next run.
DECISIONS = {
    # robots.txt answered with a bot-challenge or sign-in page ("verify you are human"): a page is not a Disallow line
    'robots_challenge_page': 'no-rules',
    # robots.txt sent us to a page on ANOTHER site that holds no robots lines
    'robots_other_site_page': 'no-rules',
    # a page is only a "wall" (are-you-human page: stop the site for this run) when its text is shorter than this
    'wall_max_chars': 3000,
    # owner 27 Nov 2026, 4:15 AM ("sure we are just polite"): a page that answers 401 / 403, or is a wall, is THAT PAGE only.
    # The site carries on at its slow pace. Only this many such answers IN A ROW from one site, with nothing read between,
    # stop that site for the rest of this run (manners, never a block; asked again next run).
    'refusals_in_a_row': 5,
}
WALL_MAX_CHARS = int(DECISIONS['wall_max_chars'])
REFUSALS_IN_A_ROW = max(1, int(DECISIONS['refusals_in_a_row']))

# ---------------------------------------------------------------------------------------------- the robots.txt answer
# key -> (verdict, plain words). verdict: 'rules' = read its lines (only a Disallow line can say no);
# 'no-rules' = allowed, carry on; 'busy' = not this run for that site, asked again next run by itself.
ROBOTS_TABLE = {
    'robots-file':  ('rules',    'robots.txt is a robots file: its lines decide, and only a Disallow line says no'),
    'too-long':     ('rules',    'robots.txt is longer than 500 KB: its first 500 KB decide (RFC 9309)'),
    'web-page':     ('no-rules', 'robots.txt answered with a web page, not a robots file: a page is not a Disallow line, allowed'),
    'empty':        ('no-rules', 'robots.txt is empty: no rules, allowed'),
    'unparsable':   ('no-rules', 'robots.txt could not be read as rules: no Disallow line was read, allowed'),
    'redirected':   (DECISIONS['robots_other_site_page'], 'robots.txt sent us to a page on another site with no robots lines (owner to confirm: see DECISIONS)'),
    'challenge':    (DECISIONS['robots_challenge_page'], 'robots.txt answered with a bot-challenge or sign-in page (owner to confirm: see DECISIONS)'),
    'no-file':      ('no-rules', 'there is no robots.txt (404 / 410): no rules, allowed'),
    '4xx':          ('no-rules', 'robots.txt answered 401 / 403 / another 4xx (not 429): no rules, allowed'),
    '429':          ('busy',     'robots.txt answered 429 (too many requests): the site is busy, not this run, tried next run'),
    '5xx':          ('busy',     'robots.txt answered a server error (5xx): the site is busy, not this run, tried next run'),
    'no-answer':    ('busy',     'robots.txt did not answer (time-out, no connection, certificate): not this run, tried next run'),
}

# ------------------------------------------------------------------------------------------- the page's own answer
# key -> (verdict, plain words). verdict: 'read' / 'dead' / 'skip-page' (THIS page is not read this run; the site carries
# on; REFUSALS_IN_A_ROW of them in a row stop the site for this run) / 'stop-site' (stop asking THAT site for the rest of THIS run,
# no retry, asked again next run, never saved as blocked) / 'busy' (not now, asked again next run).
PAGE_TABLE = {
    '2xx':   ('read',      'the page answered'),
    '404':   ('dead',      'the page is not there (404 / 410)'),
    '401':   ('skip-page', 'the page answered 401: one try with the page browser where the owner\'s 24 Nov rule P-2 allows it; then this page waits for the next run and the site carries on'),
    '403':   ('skip-page', 'the page answered 403: one try with the page browser where the owner\'s 24 Nov rule P-2 allows it; then this page waits for the next run and the site carries on'),
    '429':   ('stop-site', 'the page answered 429 (the site says slow down): stop asking that site at once for this run, no browser try; ask again next run'),
    'wall':  ('skip-page', 'the page is a "are you human" wall: this page waits for the next run and the site carries on'),
    '5xx':   ('busy',      'the page answered a server error: busy, asked again next run'),
    'no-answer': ('busy',  'the page did not answer (time-out, no connection): busy, asked again next run'),
    'other': ('dead',      'the page answered another 4xx: it does not open'),
}

# ------------------------------------------------- why a park's page is not read: the FIXED list for the status page
# code -> plain words (the order is the order on the status page). Only 'disallow' is a block.
REASONS = [
    ('disallow',   'refused by robots.txt: a real Disallow line (needs a hand look)'),
    ('busy',       'site busy last run (429 / server error / no answer): tried again next run by itself'),
    ('stopped',    'the page answered 401 / 403 or a wall last run, or the site said 429: tried again next run by itself'),
    ('slow',       'slow site (Crawl-delay): waiting for the slow pass'),
    ('built',      'the page builds itself: needs the page browser (0-INSTALL-PAGE-BROWSER.bat)'),
    ('no-link',    'no link to read (no link, or only the agency front page or a list)'),
    ('dead',       'the link is dead (404)'),
    ('club-rule',  "the club's own saved-copies-only list (never asked live)"),
]
REASON_WORDS = dict(REASONS)

# Statuses the fetcher returns as text (kpc_manners.get) -> reason code.
_TEXT_STATUS = {
    'robots': 'disallow',
    'robots-unreadable': 'busy', 'rest': 'busy', 'err': 'busy', 'not-in-copy': 'busy',
    'stopped': 'stopped', 'refused': 'stopped',
    'crawl-delay': 'slow', 'deferred': 'slow',
    'host-rule': 'club-rule',
    'not-asked': 'no-link',
}


P2_BROWSER_CODES = (401, 403)   # owner 24 Nov 7:32 AM, P-2 "yes": these get ONE page-browser try before the page is counted as refused


def robots_key(status, body=b'', redirected_off_site=False, looks_like_page=False, error=None, challenge=False):
    """Which row of ROBOTS_TABLE an answer to /robots.txt is. status: an int HTTP status, or None when no answer came
    (error holds why). body: the bytes. looks_like_page: True when the 200 body is a web page with no robots lines."""
    if status is None or error is not None and not isinstance(status, int):
        return 'no-answer'
    if not isinstance(status, int):
        return 'no-answer'
    if status in (404, 410):
        return 'no-file'
    if status == 429:
        return '429'
    if 400 <= status < 500:
        return '4xx'
    if status >= 500:
        return '5xx'
    if status != 200 and not 200 <= status < 300:
        return '4xx' if 300 <= status < 400 else 'no-answer'   # a redirect that never landed = no rules
    b = body or b''
    if not b.strip():
        return 'empty'
    if looks_like_page:
        return 'redirected' if redirected_off_site else 'challenge' if challenge else 'web-page'
    if len(b) > ROBOTS_MAX:
        return 'too-long'
    return 'robots-file'


ROBOTS_MAX = 512_000


def robots_verdict(status, body=b'', redirected_off_site=False, looks_like_page=False, error=None, challenge=False):
    """-> (verdict, key, plain words). verdict is 'rules', 'no-rules' or 'busy'."""
    k = robots_key(status, body, redirected_off_site, looks_like_page, error, challenge)
    v, why = ROBOTS_TABLE[k]
    if k == 'no-answer' and error:
        why = f'{why} ({str(error)[:100]})'
    return v, k, why


def page_key(status, wall=False):
    if wall:
        return 'wall'
    if not isinstance(status, int):
        return 'no-answer'
    if 200 <= status < 300:
        return '2xx'
    if status in (404, 410):
        return '404'
    if status in (401, 403, 429):
        return str(status)
    if status >= 500:
        return '5xx'
    return 'other'


def page_verdict(status, wall=False):
    """-> (verdict, key, plain words). verdict is 'read', 'dead', 'skip-page', 'stop-site' or 'busy'."""
    k = page_key(status, wall)
    v, why = PAGE_TABLE[k]
    return v, k, why


def reason_of(status, kind, own_is=''):
    """The fixed reason a park's page is NOT read, or '' when it was read (html / pdf with words).
    status / kind are what the reader saved in page.status / page.kind."""
    if kind in ('html', 'pdf'):
        return ''
    if own_is in ('agency-home', 'list') or kind == 'none':
        if isinstance(status, str) and status in _TEXT_STATUS and _TEXT_STATUS[status] != 'no-link':
            return _TEXT_STATUS[status]
        return 'no-link'
    if kind == 'script-built':
        return 'built'
    if kind == 'dead':
        return 'dead'
    if isinstance(status, int):
        v, k, _ = page_verdict(status)
        if v in ('stop-site', 'skip-page'):
            return 'stopped'
        if v == 'dead':
            return 'dead'
        if v == 'busy':
            return 'busy'
        if kind == 'refused':
            return 'stopped'     # a 200 that was a wall
        return 'busy'
    s = str(status or '')
    if s.startswith('err'):
        return 'busy'
    if s in _TEXT_STATUS:
        return _TEXT_STATUS[s]
    if kind == 'refused':
        return 'stopped'
    return 'busy' if s else 'no-link'


def is_block(reason):
    """Only a real Disallow line is a block. Everything else is 'not now' at most."""
    return reason == 'disallow'
