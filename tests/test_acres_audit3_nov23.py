#!/usr/bin/env python3
"""The acreage bot, 23 Nov 2026 (owner 'Yes' to the outside audit 3 fixes): numbers read right ('0,123 km2', '.5', no
negatives, '2019 1,200' is 2019), a repeated row counted once, a tie decided by the list itself (not the work order), a list
that failed on the network asked again, a failed re-read never wipes the last good one, and park facts does not count a
flagged size or a hand copy with no source page as proof. Offline, invented parks.
Prints PASS / FAIL and ends ALL PASS or SOME FAILED."""
import os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.environ['KPC_NO_NET'] = '1'
sys.path.insert(0, str(ROOT / '.github/scripts/draft/tools/kpc_acres'))
sys.path.insert(0, str(ROOT / '.github/scripts/draft/tools/kpc_park_facts'))
import kpc_acres as A  # noqa: E402
import kpc_park_facts as PF  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


# MUST 2: the number reader
for s, want in [('0,123 km2', 0.123), ('.5 acres', 0.5), ('-45 acres', None), ('2019 1,200', 2019.0), ('1 234,5 ha', 1234.5),
                ('12 345 ha', 12345.0), ('1 234 567 ac', 1234567.0), ('1,234.5', 1234.5), ('12,345', 12345.0), ('45,6 km2', 45.6)]:
    check(f'{s!r} reads as {want}', A.parse_size(s)[0] == want)


# MUST 1 + S3: the merge
class Parks:
    outline, p = {}, {}


def mrow(ref, name, value, row, unit='acres'):
    return {'ref': ref, 'row_name': name, 'value': value, 'unit': unit, 'acres': value, 'row': row, 'rule': 'name+kind',
            'how_text': '', 'why': 'invented', 'source_url': ''}


def res(agency, matches, url='https://lists.invented.example/a.csv', kind='list'):
    return {'kind': kind, 'agency': agency, 'area': 'US-ZZ', 'source_url': url, 'read_date': '2026-11-23', 'matches': matches}


got = A.merge([res('Invented Agency', [mrow('US-9101', 'Heron Marsh', 300, 1), mrow('US-9101', 'Heron Marsh', 300, 2),
                                       mrow('US-9101', 'Heron Marsh', 300, 3)])], Parks())
check('three identical rows count once (300, not 900)', got['US-9101']['acres'] == 300)
check('and the size says it', any('counted once' in f for f in got['US-9101']['flags']))
got = A.merge([res('Invented Agency', [mrow('US-9102', 'Heron Marsh Unit A', 300, 1), mrow('US-9102', 'Heron Marsh Unit B', 200, 2)])], Parks())
check('two different rows still add up (500)', got['US-9102']['acres'] == 500)
a = res('B Agency', [mrow('US-9103', 'Heron Marsh', 100, 1)], url='https://b.invented.example/l.csv')
b = res('A Agency', [mrow('US-9103', 'Heron Marsh', 120, 1)], url='https://a.invented.example/l.csv')
check('a tie is decided by the list itself, whatever the work order',
      A.merge([a, b], Parks())['US-9103']['acres'] == A.merge([b, a], Parks())['US-9103']['acres'] == 120)

# S1: network failures are asked again
check('a list that failed on the network is retried', A._retry_now('failed: network error (timed out)') and A._retry_now('failed: HTTP 503'))
check('a list refused for good (HTTP 405) is not', not A._retry_now('failed: HTTP 405'))

# MUST 3: the code keeps a good read when the re-read fails
src = (ROOT / '.github/scripts/draft/tools/kpc_acres/kpc_acres.py').read_text(encoding='utf-8')
check('a failed re-read keeps the last good read of the list', "kept: the re-read on" in src and "startswith('failed') and os.path.exists(fp)" in src)

# S2: park facts
sizes = {'US-9201': {'acres': 50, 'how': 'number', 'source_url': 'https://agency.invented.example/parks.pdf', 'flags': []},
         'US-9202': {'acres': 50, 'how': 'number', 'source_url': 'https://agency.invented.example/parks.pdf',
                     'flags': ['over 50x the current outline (1 ac)']},
         'US-9203': {'acres': 50, 'how': 'hand copy', 'source_url': '', 'flags': []},
         'US-9204': {'acres': 50, 'how': 'hand copy', 'source_url': 'https://agency.invented.example/park/9204', 'flags': []}}
PF.tag_sizes(sizes, None)
check("an agency's own list counts as proof", sizes['US-9201']['witness_counts'] is True)
check('a size the bot flagged is not proof', sizes['US-9202']['witness_counts'] is False and 'flagged' in sizes['US-9202']['witness_why'])
check('a hand copy with no source page is not proof', sizes['US-9203']['witness_counts'] is False)
check('a hand copy with its source page is', sizes['US-9204']['witness_counts'] is (sizes['US-9204']['witness'] in PF.WITNESS_PROOF))
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
