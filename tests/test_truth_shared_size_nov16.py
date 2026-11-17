#!/usr/bin/env python3
"""Nov 16 2026 (KPC owner): the park truth bot's 'same number on many parks' check must group by the
size and the sentence it came from, not only by web address.

A site-wide banner reused on different park pages never tripped the old (acres, URL) grouping, so
one statewide sentence was read as each park's size. When one figure or sentence supplies the size
for 3 or more parks in a state (the threshold the bot already used), those sizes are left blank
('unsure', official cleared). Blank beats wrong.

Real review lists (modelled on MD, MN and OK) have real size gaps: each park's official size and
sentence is its own. Those 'off' rows must stay. Parks that only happen to share a figure, but from
different sentences, also stay.

Synthetic data only. Offline, no live or held truth files are read or written.
(KPC owner, 2026-11-16)"""
import os, pathlib, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.environ['OUT'] = tempfile.mkdtemp(prefix='kpc-truth-ss-')
sys.path.insert(0, str(ROOT / '.github' / 'scripts'))
import kpc_truth_bot as T  # noqa: E402
if not hasattr(T, 'demote_shared_agency_totals'):
    print('FAIL kpc_truth_bot.py has no demote_shared_agency_totals (the shared-size check)')
    print('SOME FAILED')
    sys.exit(1)

ok = True


def check(c, msg):
    global ok
    print(('PASS ' if c else 'FAIL ') + msg)
    ok = ok and bool(c)


def row(ref, n, ours, official_acres, sent, url, verdict='off'):
    return ref, {
        'n': n,
        'ours': {'acres': ours},
        'official': {'acres': official_acres, 'sent': sent, 'line': sent, 'url': url},
        'verdict': verdict,
        'pct': 80,
        'cause': '',
    }


# --- CT-style: one statewide sentence, same figure, different URLs (the bug).
# Without the fix, grouping only by (acres, url) would leave all nine 'off'.
banner = ('With 142 state parks and forests covering more than 255,000 acres of pristine '
          'coastline, rolling hills, and enchanting forests, Connecticut’s parks welcome you.')
ct = {}
for i in range(9):
    ref, r = row(f'US-CT{i}', f'Park {i}', 200 + i, 255000.0, banner,
                 f'https://portal.ct.gov/deep/state-parks/park-{i}')
    ct[ref] = r
old_style = {}
for ref, r in ct.items():
    of = r['official']
    old_style.setdefault((of['acres'], of.get('url', '')), []).append(ref)
check(all(len(v) < 3 for v in old_style.values()),
      'without the sentence grouping, the nine CT-style rows would not be caught (each has its own URL)')
demoted = T.demote_shared_agency_totals(ct)
check(sorted(demoted) == sorted(ct), f'all nine CT-style rows are demoted; got {sorted(demoted)}')
check(all(r['verdict'] == 'unsure' and r['official'] is None and r['pct'] is None for r in ct.values()),
      'those nine are left unsure and the official size is cleared (blank beats wrong)')
check(all('9 parks share from the same sentence (255,000 ac)' in (r.get('cause') or '') for r in ct.values()),
      f'the cause names the shared sentence and the figure; sample={next(iter(ct.values())).get("cause")}')


# --- MD / MN / OK style: real review-list size gaps, each park its own official figure and sentence.
md = dict((row(*a)[0], row(*a)[1]) for a in (
    ('US-MD1', 'Eastern Neck National Wildlife Refuge', 1839, 2285.0,
     'Eastern Neck National Wildlife Refuge is a 2,285 acre island providing habitat for wintering waterfowl.',
     'https://www.fws.gov/refuge/eastern-neck'),
    ('US-MD2', 'Monocacy National Battlefield', 1332, 1649.0,
     'Monocacy National Battlefield covers 1,649 acres.',
     'https://www.nps.gov/mono/index.htm'),
    ('US-MD3', 'Plum Creek Natural Area', 101, 500.0,
     'Plum Creek Natural Area encompasses nearly 500 acres and lies within Elk Neck State Forest.',
     'https://dnr.maryland.gov/wildlife/plum-creek'),
    ('US-MD4', 'Mattawoman Creek Natural Area', 1980, 1300.0,
     'Mattawoman Creek Natural Area includes over 1,300 acres in northwestern Charles County.',
     'https://dnr.maryland.gov/wildlife/mattawoman'),
    ('US-OK1', 'Washita National Wildlife Refuge', 8075, 8075.0,
     'Each fall 8,075 Canada geese stop at the refuge.',
     'https://www.fws.gov/refuge/washita'),  # a misread, but its own sentence and figure
))
# Washita in the fixture is 'off' with a unique sentence — it must stay off (not blanked as boilerplate).
T.demote_shared_agency_totals(md)
check(all(r['verdict'] == 'off' and r['official'] is not None for r in md.values()),
      'MD/MN/OK-style real size gaps stay off: each park has its own official size and sentence')


# --- Same figure, different sentences (TX 100-acre coincidence): not boilerplate, stay off.
tx100 = dict((row(*a)[0], row(*a)[1]) for a in (
    ('US-TX1', 'Waco Mammoth National Monument', 47, 100.0,
     'Waco Mammoth National Monument sits within 100 acres of wooded parkland along the Bosque River.',
     'https://www.nps.gov/waco/index.htm'),
    ('US-TX2', 'Dinosaur Valley State Park', 1425, 100.0,
     'Bring your own horse to explore the 100-acre South Primitive Area.',
     'https://tpwd.texas.gov/state-parks/dinosaur-valley'),
    ('US-TX3', 'M.O. Neasloney Wildlife Management Area', 69, 100.0,
     'Neasloney WMA has 100 acres located in Gonzales County, south of Luling.',
     'https://tpwd.texas.gov/huntwild/wma/neasloney'),
))
T.demote_shared_agency_totals(tx100)
check(all(r['verdict'] == 'off' and r['official'] is not None for r in tx100.values()),
      'three parks that only happen to share the figure 100, from different sentences, stay off')


# --- The older same-page rule still fires (same acres and URL, 3+ parks).
page = 'https://example.gov/statewide-camping'
one_page = {}
for i in range(3):
    ref, r = row(f'US-P{i}', f'Park {i}', 10 + i, 1400000.0,
                 f'Park {i} welcomes you. The system covers 1.4 million acres.', page)
    one_page[ref] = r
demoted = T.demote_shared_agency_totals(one_page)
check(sorted(demoted) == sorted(one_page),
      'three parks that share one number from one page are still demoted')
check(all(r['verdict'] == 'unsure' and r['official'] is None for r in one_page.values()),
      'the same-page group is left unsure and the official size is cleared')


# --- Two parks only: under the existing 3-park threshold, not demoted.
pair = dict((row(*a)[0], row(*a)[1]) for a in (
    ('US-A', 'Alpha', 10, 5000.0, 'The agency manages 5,000 acres.', 'https://a.example/1'),
    ('US-B', 'Beta', 20, 5000.0, 'The agency manages 5,000 acres.', 'https://a.example/2'),
))
T.demote_shared_agency_totals(pair)
check(all(r['verdict'] == 'off' and r['official'] is not None for r in pair.values()),
      'two parks sharing a sentence stay off: the threshold is still 3')


print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
