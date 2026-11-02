#!/usr/bin/env python3
"""STORAGE KEEPER (chat 10, Oct 30 2026; HQ 8:50 AM, Brandon 8:45 AM 'a bot to keep storage size down?').
Runs in BOTH repos (each cleans only itself: a repo's own token can't touch the other):
  KPC-Data   kpc-storage.yml   Sunday 9:07 UTC + by hand: MEASURES all (KPC-Links, KPC-Data, kpc-app sizes; lookup + picture-maps
                               branches; own artifacts + caches), cleans KPC-Data, writes the status board line + data/status/storage.json
  KPC-Links  kpc-research-helpers.yml (Sundays): cleans KPC-Links, and writes the STORAGE WARNING line into HQ's inbox (chat-7.md)
Cleans by itself (safe things only): Actions artifacts older than 1 day, caches older than 7 days, bot branches older than 14 days
with no open PR and not named in any workflow file (never main, test-build, stage-*, lookup, picture-maps, a branch a bot uses);
squashes the orphan branches lookup past 150 MB and picture-maps past 300 MB (one fresh commit, same files: done by the workflow).
NEVER rewrites main's history or deletes a data file. Over the line (KPC-Links 650 MB, KPC-Data 400 MB) = a STORAGE WARNING; the
workflow then ends red ONCE that day (= the only email). Everything else ends `|| true`.
  python3 kpc_storage_keeper.py measure|clean|warn      env REPO (owner/name of this repo), GH_TOKEN"""
import datetime as dt, glob, json, os, pathlib, re, subprocess, sys, time

REPO = os.environ.get('REPO') or 'KentuckyPortableClub/KPC-Data'
OWNER = REPO.split('/')[0]
LINES = {'KPC-Links': 650, 'KPC-Data': 400}
KEEP = re.compile(r'^(main|master|test-build|stage-.*|lookup|picture-maps|gh-pages|.*(storage|state|data|archive|backup|keep).*)$')   # a branch that HOLDS data is never 'stale'
NOW = dt.datetime.now(dt.timezone.utc)


def api(path, method='GET'):
    p = subprocess.run(['gh', 'api', '-X', method, path] + (['--paginate'] if method == 'GET' else []), capture_output=True, text=True)
    if p.returncode: return None
    out = p.stdout.strip()
    if not out: return {}
    try: return json.loads(out)
    except ValueError:   # --paginate joins pages: '][' or '}{'
        try: return json.loads('[' + out.replace('][', ',').replace('}{', '},{').strip('[]') + ']')
        except ValueError: return None


def age_days(ts):
    try: return (NOW - dt.datetime.fromisoformat(str(ts).replace('Z', '+00:00'))).days
    except ValueError: return 0


def size_mb(repo):
    j = api(f'repos/{repo}')
    return round((j or {}).get('size', 0) / 1024) if j else None


def measure():
    row = {'date': NOW.strftime('%Y-%m-%d')}
    for r in ('KPC-Links', 'KPC-Data', 'kpc-app', 'KPC-App'):
        s = size_mb(f'{OWNER}/{r}')
        if s is not None: row[r] = s
    for b in ('lookup', 'picture-maps'):
        v = os.environ.get(f'BRANCH_MB_{b.replace("-", "_").upper()}')
        if v: row[f'branch {b}'] = int(v)
    arts = api(f'repos/{REPO}/actions/artifacts?per_page=100') or {}
    row['artifacts MB (this repo)'] = round(sum(a.get('size_in_bytes', 0) for a in (arts.get('artifacts') if isinstance(arts, dict) else []) or []) / 1048576)
    hist_f = pathlib.Path(os.environ.get('HIST') or 'data/status/storage.json')
    try: hist = json.load(open(hist_f))
    except Exception: hist = {'about': 'Storage keeper: weekly sizes (MB), last 12 weeks', 'weeks': []}  # noqa: BLE001
    hist['weeks'] = ([w for w in hist.get('weeks') or [] if w.get('date') != row['date']] + [row])[-12:]
    hist_f.parent.mkdir(parents=True, exist_ok=True); json.dump(hist, open(hist_f, 'w'), indent=1)
    over = [f"{k} {row[k]} MB (line {v})" for k, v in LINES.items() if isinstance(row.get(k), int) and row[k] > v]
    msg = ', '.join(f'{k} {v}' + ('' if k == 'date' else ' MB') for k, v in row.items() if k != 'date')
    print(f'::notice title=Storage keeper::{msg}' + (f' / STORAGE WARNING: {"; ".join(over)}' if over else ''))
    print('OVER=' + ('1' if over else '0'))
    print('LINE=' + (('STORAGE WARNING: ' + '; '.join(over) + ' / ') if over else '') + msg)


def clean():
    n = {'artifacts': 0, 'caches': 0, 'branches': 0}
    arts = api(f'repos/{REPO}/actions/artifacts?per_page=100') or {}
    for a in (arts.get('artifacts') if isinstance(arts, dict) else []) or []:
        if not a.get('expired') and age_days(a.get('created_at')) >= 1 and api(f"repos/{REPO}/actions/artifacts/{a['id']}", 'DELETE') is not None: n['artifacts'] += 1
    cs = api(f'repos/{REPO}/actions/caches?per_page=100') or {}
    for c in (cs.get('actions_caches') if isinstance(cs, dict) else []) or []:
        if age_days(c.get('last_accessed_at') or c.get('created_at')) >= 7 and api(f"repos/{REPO}/actions/caches/{c['id']}", 'DELETE') is not None: n['caches'] += 1
    used = ' '.join(open(f, encoding='utf-8', errors='replace').read() for f in glob.glob('.github/workflows/*.yml') + glob.glob('.github/workflows/*.yaml'))
    prs = {p.get('head', {}).get('ref') for p in (api(f'repos/{REPO}/pulls?state=open&per_page=100') or []) if isinstance(p, dict)}
    for b in api(f'repos/{REPO}/branches?per_page=100') or []:
        name = b.get('name', '') if isinstance(b, dict) else ''
        if not name or KEEP.match(name) or name in prs or re.search(r'(?<![\w-])' + re.escape(name) + r'(?![\w-])', used): continue
        c = api(f"repos/{REPO}/commits/{b.get('commit', {}).get('sha')}") or {}
        when = ((c.get('commit') or {}).get('committer') or {}).get('date')
        if when and age_days(when) >= 14 and api(f'repos/{REPO}/git/refs/heads/{name}', 'DELETE') is not None:
            n['branches'] += 1; print(f'::notice title=Storage keeper::deleted stale branch {name} (last commit {when[:10]})')
    print(f"::notice title=Storage keeper::{REPO}: {n['artifacts']} artifacts, {n['caches']} caches, {n['branches']} stale branches removed")


def warn():
    """KPC-Links side: an over-the-line week puts ONE line at the top of HQ's inbox."""
    line = os.environ.get('LINE') or ''
    f = pathlib.Path('.claude/inbox/chat-7.md')
    if 'STORAGE WARNING' not in line or not f.exists(): return
    t = f.read_text(encoding='utf-8'); tag = f"STORAGE KEEPER ({NOW:%Y-%m-%d})"
    if tag in t: return
    i = t.find('\n- '); new = f"- **FROM {tag}: {line}** HQ decides (squash / move files); the keeper never rewrites main."
    f.write_text(t[:i] + '\n' + new + t[i:] if i >= 0 else t + '\n' + new + '\n', encoding='utf-8')


if __name__ == '__main__':
    try: {'measure': measure, 'clean': clean, 'warn': warn}[sys.argv[1] if len(sys.argv) > 1 else 'measure']()
    except Exception as e: print(f'::notice title=Storage keeper::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
