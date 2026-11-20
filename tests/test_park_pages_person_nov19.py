#!/usr/bin/env python3
"""Person page, intake, and the PC kit (hand-off 05, part 3). Offline.
Prints PASS / FAIL lines and ends ALL PASS or SOME FAILED."""
import json, pathlib, re, socket, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
sys.path.insert(0, str(S))
ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


def _no_net(*a, **k):
    raise OSError('test: no network')


socket.socket.connect = _no_net
import kpc_park_pages_person as P  # noqa: E402

readme = (ROOT / 'tools/park-pages-pc/README-PC.txt').read_text(encoding='utf-8').splitlines()
check('the PC readme is ten plain lines', len([ln for ln in readme if ln.strip()]) == 10)
sh = (ROOT / 'tools/park-pages-pc/run-park-pages.sh').read_text(encoding='utf-8')
check('the launcher asks one question', 'Which state? (blank = continue the list)' in sh and 'park-pages-' in sh)

with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td)
    (t / 'facts').mkdir()
    (t / 'pictures').mkdir()
    (t / 'pictures' / 'US-9.jpg').write_bytes(b'\xff\xd8\xff' + b'x' * 20)
    fact = {
        'ref': 'US-9', 'area': 'US-UT', 'unchanged': False,
        'pota': {'name': 'Sample National Park', 'type': 'National Park', 'link': 'https://www.nps.gov/samp/index.htm'},
        'asked': {'url': 'https://www.nps.gov/samp/index.htm'},
        'page': {'kind': 'refused'},
        'name': {'best': 'Sample National Park', 'title': 'Sample', 'heading': 'Sample National Park'},
        'designation': {'combined': False, 'words': ['National Park'], 'parts': []},
        'inside_of': [], 'sizes': [{'acres': 100.0, 'as': '100 acres', 'label': 'Park', 'quote': '100 acres'}],
        'parts': [], 'questions': [{'code': 'REFUSED', 'plain': 'The site does not take automated visitors. For a person.', 'quote': ''}],
    }
    (t / 'facts' / 'US-UT.json').write_text(json.dumps({'area': 'US-UT', 'parks': {'US-9': fact}}), encoding='utf-8')
    html_path = t / 'for-a-person.html'
    subprocess.check_call([sys.executable, '-B', str(S / 'kpc_park_pages.py'), 'person-page', '--out', str(t), '--html', str(html_path), '--quiet'])
    html = html_path.read_text(encoding='utf-8')
    check('the person page is under 300 KB and asks for nothing on the network',
          html_path.stat().st_size < 300_000 and 'http://' not in html.split('<script>', 1)[-1] and 'fetch(' not in html)
    check('answer boxes are empty and no call sign is used as an example',
          'value="' not in html and 'KZ4CP' not in html and 'call sign' not in html.lower())
    check('the five fields are on the card',
          all(s in html for s in ("The name at the top of the page", "Says '& Preserve'",
                                  'inside another named area', 'Size on the page', 'Named tracts', 'Could not tell')))
    narrow = html.replace('</head>', '<style>html,body{width:390px;max-width:390px}</style></head>')
    narrow = narrow.replace('</body>', '<script>document.getElementById("dump").textContent="SW="+document.documentElement.scrollWidth+" CW="+document.documentElement.clientWidth;</script></body>')
    narrow_path = t / 'narrow.html'
    narrow_path.write_text(narrow, encoding='utf-8')
    dom = t / 'narrow-dom.html'
    with dom.open('w', encoding='utf-8') as out:
        subprocess.run(['timeout', '25', 'google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
                        '--window-size=390,800', '--virtual-time-budget=1500', '--dump-dom', str(narrow_path)],
                       stdout=out, stderr=subprocess.DEVNULL, timeout=35)
    m = re.search(r'SW=(\d+) CW=(\d+)', dom.read_text(encoding='utf-8', errors='replace'))
    check('at 390 px the page does not scroll sideways', bool(m) and int(m.group(1)) <= int(m.group(2)) + 1)
    filled = html.replace('</body>', '''<script>
document.getElementById('who').value = 'A person';
const card = document.querySelector('.card');
card.querySelector('[data-f=name]').value = 'Sample National Park and Preserve';
card.querySelector('[data-f=combined]').checked = true;
card.querySelector('[data-f=size]').value = '250';
card.querySelector('[data-f=size_words]').value = 'about 250 acres';
card.querySelector('[data-f=tracts]').value = 'North Tract, South Tract';
document.getElementById('dump').textContent = JSON.stringify(answers(), null, 1);
</script></body>''')
    filled_path = t / 'filled.html'
    filled_path.write_text(filled, encoding='utf-8')
    dom2 = t / 'filled-dom.html'
    with dom2.open('w', encoding='utf-8') as out:
        subprocess.run(['timeout', '25', 'google-chrome', '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
                        '--virtual-time-budget=1500', '--dump-dom', str(filled_path)],
                       stdout=out, stderr=subprocess.DEVNULL, timeout=35)
    dumped = re.search(r'<pre id="dump"[^>]*>(.*?)</pre>', dom2.read_text(encoding='utf-8', errors='replace'), re.S)
    check('the save button builds a file intake can read', bool(dumped) and 'Sample National Park and Preserve' in (dumped.group(1) if dumped else ''))
    if dumped:
        answers = json.loads(dumped.group(1).replace('&quot;', '"').replace('&amp;', '&'))
        (t / 'person-answers.json').write_text(json.dumps(answers), encoding='utf-8')
        subprocess.check_call([sys.executable, '-B', str(S / 'kpc_park_pages.py'), 'intake', str(t / 'person-answers.json'),
                               '--out', str(t), '--today', '2026-11-19', '--quiet'])
        got = json.loads((t / 'facts' / 'US-UT.json').read_text(encoding='utf-8'))['parks']['US-9']
        check('a person wins, the bot row is kept, and the picture is removed',
              got['name']['best'] == 'Sample National Park and Preserve' and got['bot_saw']['name'] == 'Sample National Park'
              and got['person']['by'] == 'person' and not (t / 'pictures' / 'US-9.jpg').exists())
        csv = (t / 'disagreements.csv').read_text(encoding='utf-8')
        check('a disagreement is written when the person and the bot differ', 'size' in csv and 'combined' in csv)
    # PC kit
    (t / 'data' / 'parkinfo').mkdir(parents=True)
    (t / 'data' / 'parkinfo' / 'US-UT.json').write_text(json.dumps({'parks': {'US-9': ['Sample', 'https://www.nps.gov/samp', 'National Park', '', '', 37, -113, 0, 0, 1]}}), encoding='utf-8')
    (t / 'data' / 'parkinfo' / 'US-AK.json').write_text('{"parks":{"US-1":["Other","","National Park","","",60,-150,0,0,1]}}', encoding='utf-8')
    kit = t / 'kit.zip'
    subprocess.check_call([sys.executable, '-B', str(S / 'kpc_park_pages.py'), 'pc-kit', '--data', str(t / 'data'),
                           '--areas', 'US-UT', '--out', str(kit), '--quiet'])
    import zipfile
    with zipfile.ZipFile(kit) as z:
        names = z.namelist()
    check('the PC kit has the reader and manners, and not the other state',
          'scripts/kpc_manners.py' in names and 'scripts/kpc_host_rules.py' in names and 'data/parkinfo/US-UT.json' in names
          and 'data/parkinfo/US-AK.json' not in names and 'run-park-pages.sh' in names)
    blob = kit.read_bytes()
    check('the kit holds no token', b'ghp_' not in blob and b'AKIA' not in blob)

print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
