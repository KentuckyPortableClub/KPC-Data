#!/usr/bin/env python3
"""X1 (Quality Nov 13): kpc_release_approved requires a verified owner or Quality source,
refuses bot-written entries, and does not let a bot release itself (TRUST_RUN / auto_trusted).
Releases stay owner-run."""
import json, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / '.github/scripts'))
import kpc_release_approved as RA  # noqa: E402

ok = True
def check(msg, cond, extra=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg + (f' {extra}' if extra and not cond else ''))
    ok = ok and bool(cond)

check('TRUST_RUN is 0 (no bot self-release)', RA.TRUST_RUN == 0)
items = [
    {'what': 'access', 'chat11': 'YES', 'date': '2026-11-13', 'time': '8:00 AM', 'by': 'KPC owner'},
    {'what': 'access', 'chat11': 'YES', 'date': '2026-11-13', 'time': '8:10 AM', 'by': 'KPC owner'},
    {'what': 'access', 'chat11': 'YES', 'date': '2026-11-13', 'time': '8:20 AM', 'by': 'KPC owner'},
]
check('trusted_kinds is empty when TRUST_RUN is 0, even after three YES grades',
      RA.trusted_kinds(items) == set())

ok_yes, _ = RA.verdict_ok('YES')
check('a bare YES still parses as a verdict', ok_yes)

check('source_ok: KPC owner is accepted', RA.source_ok({'by': 'KPC owner'})[0])
check('source_ok: Brandon is accepted', RA.source_ok({'author': 'Brandon'})[0])
check('source_ok: Quality is accepted', RA.source_ok({'source': 'Quality'})[0])
check('source_ok: chat 11 is accepted', RA.source_ok({'by': 'chat 11'})[0])
check('source_ok: missing source is refused', not RA.source_ok({})[0] and 'verified' in RA.source_ok({})[1].lower())
check('source_ok: by=test is refused', not RA.source_ok({'by': 'test'})[0])
ok_bot, why_bot = RA.source_ok({'by': 'kpc-bot', 'chat11': 'YES'})
check('source_ok: a bot-written entry is refused', (not ok_bot) and 'bot-written' in why_bot)
ok_gh, why_gh = RA.source_ok({'author': 'github-actions[bot]', 'chat11': 'PASS'})
check('source_ok: github-actions is refused', (not ok_gh) and 'bot-written' in why_gh)

# auto_trusted is a no-op
log = []
RA.auto_trusted([{'what': 'access', 'chat11': 'YES', 'by': 'kpc-bot'}], log)
check('auto_trusted releases nothing (bot self-release refused)', log == [])

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
