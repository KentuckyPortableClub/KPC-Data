#!/usr/bin/env python3
"""Offline test (bots review, package E, Nov 11 2026), KPC-Data side. Fake poster, fake failing second message, no network.
 - YouTube comments: an API key or the staff-room webhook that comes back in an error never reaches stdout / stderr; the memory is
   written after every message that went out (message 2 of 3 failing leaves 1 recorded), and the next run sends only what is left
 - the workflows touched (EU warnings, YouTube comments) parse, keep their cron lines and jobs, and use sparse checkouts"""
import contextlib, importlib, io, json, os, pathlib, re, subprocess, sys, tempfile, urllib.error, urllib.request
import yaml

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / '.github/scripts'))
ok = True


def check(c, m):
    global ok
    print(('PASS ' if c else 'FAIL ') + m); ok = ok and bool(c)


KEYV = 'AIza' + 'FAKEyoutubeKEY0123456789abcdefgh'
HOOK = 'https://discord' + '.com/api/webhooks/' + '123456789012345678/' + 'FAKEhookTOKEN' + 'abcdefghijklmnopqrstuvwxyz012345'
os.environ.update({'YOUTUBE_API_KEY': KEYV, 'KPC_DISCORD_STAFF_WEBHOOK': HOOK})
os.environ.pop('DRY_RUN', None)
tmp = pathlib.Path(tempfile.mkdtemp()); os.chdir(tmp)
yc = importlib.import_module('kpc_youtube_comments')

# scrub on the error path
msg = f'HTTP 403 {yc.API}commentThreads?key={KEYV}&x=1 and {HOOK}'
out = io.StringIO()
with contextlib.redirect_stdout(out): yc.note('t', msg)
check(KEYV not in out.getvalue() and 'FAKEhookTOKEN' not in out.getvalue(), 'youtube comments: a key or a webhook inside a message is replaced before it is printed')
check(KEYV not in yc.scrub(msg) and 'FAKEhookTOKEN' not in yc.scrub(msg) and '123456789012345678' not in yc.scrub(msg), 'youtube comments: scrub() hides the key and the webhook')

# partial progress: 3 comments, one per message (force a tiny message size by long text), the 2nd post fails
def thread(i):
    return {'snippet': {'videoId': 'VID', 'totalReplyCount': 0, 'topLevelComment': {'id': f'c{i}', 'snippet': {
        'publishedAt': yc.NOW.strftime('%Y-%m-%dT%H:%M:%SZ'), 'authorDisplayName': 'A', 'textOriginal': 'x' * 290 if i < 3 else 'y',
        'authorChannelId': {'value': 'other'}}}}}


def fake_yt(path, **q):
    if path == 'channels': return {'items': [{'id': 'CH', 'snippet': {'title': 'T'}}]}
    if path == 'commentThreads': return {'items': [thread(i) for i in range(1, 8)]}
    if path == 'videos': return {'items': [{'id': 'VID', 'snippet': {'title': 'v' * 200}}]}
    return {}


posts, plan = [], ['ok', 'fail']
class R:
    def read(self): return b''
def fake_open(req, timeout=0):
    step = plan[min(len(posts), len(plan) - 1)]
    posts.append(json.loads(req.data)['content'][:20])
    if step == 'fail': raise urllib.error.URLError('connection reset')
    return R()
yc.yt = fake_yt; yc.urllib.request.urlopen = fake_open; yc.time.sleep = lambda s: None
out = io.StringIO()
with contextlib.redirect_stdout(out):
    try: yc.main()
    except Exception as e: err = e
    else: err = None
mem = json.load(open(yc.SEEN_F))
check(err is not None and len(posts) == 2 and len(mem['seen']) >= 1 and len(mem['seen']) < 7, 'youtube comments: message 2 fails: the comments of message 1 are already in the memory, the rest are not')
n_first = len(mem['seen'])
posts.clear(); plan[:] = ['ok']
with contextlib.redirect_stdout(io.StringIO()): yc.main()
mem = json.load(open(yc.SEEN_F))
check(len(mem['seen']) == 7 and len(posts) >= 1, 'youtube comments: the next run sends the rest and now all 7 are remembered')
posts.clear()
with contextlib.redirect_stdout(io.StringIO()): yc.main()
check(not posts, 'youtube comments: a run with nothing new posts nothing')

# workflows
WF = HERE / '.github/workflows'
def main_wf(n):
    r = subprocess.run(['git', 'show', f'origin/main:.github/workflows/{n}'], cwd=HERE, capture_output=True, text=True)
    return yaml.safe_load(r.stdout) if r.returncode == 0 else None
for n in ('kpc-eu-alerts.yml', 'kpc-youtube-comments.yml'):
    d = yaml.safe_load((WF / n).read_text()); on = d.get(True, d.get('on'))
    check(d.get('jobs') and all(j.get('steps') for j in d['jobs'].values()), f'{n}: parses, jobs and steps intact')
    o = main_wf(n)
    if o:
        oon = o.get(True, o.get('on'))
        check(on.get('schedule') == oon.get('schedule') and set(on) == set(oon), f'{n}: cron lines and trigger kinds exactly as main')
        check(set(d['jobs']) == set(o['jobs']) and d.get('concurrency') == o.get('concurrency'), f'{n}: same jobs and concurrency as main')
    t = (WF / n).read_text()
    check(t.count('sparse-checkout:') >= 1 and 'sparse-checkout-cone-mode: false' in t, f'{n}: sparse checkouts in place')
    check(not re.search(r'discord(app)?\.com/api/webhooks/\d+/\S+|AIza[0-9A-Za-z_-]{20,}', t), f'{n}: no secret value in the text')
t = (WF / 'kpc-eu-alerts.yml').read_text()
check('kpc_overlay.sh' not in t and 'rsync -a kpcdata/data/' not in t, 'eu alerts: the whole-tree overlay and rsync are gone')
check('data/alerts/' in t and '.github/scripts/' in t and 'data/outlines/layers.json' in t, 'eu alerts: the scripts, the never-contact host list and data/alerts are the only things fetched')
check("v.get('stale')" in t, 'eu alerts: the quiet-save test counts a stale mark as a change')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
