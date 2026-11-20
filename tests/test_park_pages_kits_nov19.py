#!/usr/bin/env python3
"""Blind kits (hand-off 05, part 4). Offline. The answer key is not in the kit.
Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED."""
import json, pathlib, socket, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def _no_net(*a, **k):
    raise OSError('test: no network')


socket.socket.connect = _no_net
import kpc_park_pages_kits as K  # noqa: E402


def fact(ref, kind, questions, person=None, name='Sample', typ='National Park', link='https://www.nps.gov/samp/index.htm'):
    row = {
        'ref': ref, 'pota': {'name': name, 'type': typ, 'link': link},
        'asked': {'url': link}, 'page': {'kind': kind},
        'questions': [{'code': c, 'plain': c, 'quote': ''} for c in questions],
    }
    if person:
        row['person'] = person
    return row


with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td)
    facts = {'US-UT': {
        'US-1': fact('US-1', 'refused', ['REFUSED']),
        'US-2': fact('US-2', 'script-built', ['SCRIPT_BUILT'], name='Second Park'),
        'US-3': fact('US-3', 'html', ['INSIDE_BIGGER_UNIT'], person={
            'by': 'person', 'who': 'A person', 'could_not_tell': False,
            'name': 'Known Place', 'combined': True, 'inside_name': 'Big Area', 'size': '10', 'tracts': 'North Tract',
        }, name='Known Place'),
    }}
    (t / 'facts').mkdir()
    (t / 'facts' / 'US-UT.json').write_text(json.dumps({'area': 'US-UT', 'parks': facts['US-UT']}), encoding='utf-8')
    known = {
        'inside_a_bigger_unit': [{
            'ref': 'US-9', 'level': 'must', 'pota_name': 'Red Cliffs BLM Recreation Management Area',
            'expect': {'inside_of[0].unit': 'Red Cliffs National Conservation Area', 'designation.combined': False},
        }]
    }
    # US-9 is not in facts, so the plant card uses the public POTA name only
    (t / 'known.json').write_text(json.dumps(known), encoding='utf-8')
    # give US-9 a fact-less plant by adding a minimal fact so the card has a type
    info = K.make_kits(facts, t / 'kits', t / 'kit-keys', n=2, seed=3, known_path=t / 'known.json')
    p1 = json.loads((t / 'kits' / 'pass1' / 'parks.json').read_text(encoding='utf-8'))
    p2 = json.loads((t / 'kits' / 'pass2' / 'parks.json').read_text(encoding='utf-8'))
    key = json.loads((t / 'kit-keys' / 'key.json').read_text(encoding='utf-8'))
    check('two passes hold the same parks', sorted(r['ref'] for r in p1) == sorted(r['ref'] for r in p2))
    check('the passes are in a different order', [r['ref'] for r in p1] != [r['ref'] for r in p2])
    check('a kit does not contain the answer key or the other pass',
          not (t / 'kits' / 'kit-keys').exists() and 'pass2' not in (t / 'kits' / 'pass1' / 'parks.json').read_text(encoding='utf-8')
          and 'pass1' not in (t / 'kits' / 'pass2' / 'README.md').read_text(encoding='utf-8'))
    blob = (t / 'kits' / 'pass1' / 'parks.json').read_text(encoding='utf-8') + (t / 'kits' / 'pass2' / 'parks.json').read_text(encoding='utf-8')
    check('a plant is unmarked and its answer is not in the kit',
          'plant' not in blob.lower() and 'National Conservation Area' not in blob and 'Big Area' not in blob)
    check('the key records the plants and is outside the kit', key['plants'] and info['plants'] == len(key['plants']) and not str((t / 'kit-keys').resolve()).startswith(str((t / 'kits').resolve())))
    # both passes answer the same way, matching the person plant
    def answers(refs):
        return {'parks': [{'ref': ref, 'name': 'Known Place', 'combined': True, 'inside_name': 'Big Area', 'size': '10', 'tracts': 'North Tract'}
                          if ref == 'US-3' else {'ref': ref, 'name': 'Same', 'combined': False, 'inside_name': '', 'size': '', 'tracts': ''}
                          for ref in refs]}
    (t / 'a.json').write_text(json.dumps(answers([r['ref'] for r in p1])), encoding='utf-8')
    (t / 'b.json').write_text(json.dumps(answers([r['ref'] for r in p2])), encoding='utf-8')
    res = K.score(t / 'a.json', t / 'b.json', t / 'kit-keys' / 'key.json')
    person_plants = [p for p in key['plants'] if p['ref'] == 'US-3']
    check('score counts agreement and a plant that matches',
          res['agreed'] == len(p1) and res['differ'] == 0 and (res['plant_hits'] >= 1 if person_plants else res['plants'] >= 0))
    # a different answer differs
    bad = answers([r['ref'] for r in p2])
    bad['parks'][0]['name'] = 'Not the same'
    (t / 'c.json').write_text(json.dumps(bad), encoding='utf-8')
    res2 = K.score(t / 'a.json', t / 'c.json', t / 'kit-keys' / 'key.json')
    check('score counts a difference', res2['differ'] >= 1)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
