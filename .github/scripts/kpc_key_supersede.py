"""Nov 8 (Brandon 1:50 PM CST, card t748s2719: "Make the freeze-rule PR so a newer Quality-passed build replaces the held one").

The Nov 2 freeze keeps a held key build in data/waiting/in/ until it is graded. This adds ONE way out: a NEWER build of the same key
replaces the held one when Quality (chat 11) has given that newer build a KEY YES in data/waiting/approved.json (the existing verdict
record: what=<key>, build=<the new build id>, chat11 'YES ...'). Nothing of the old build goes live: its files are overwritten in the
waiting room by the new build's, and the old build is LOGGED in data/status/key-copy/replaced-<key>.json (build, file list, sha1,
the KPC-Data commit that still holds it in history). A KEY NO is not needed, so the per-park release never runs on the old build.
"""
import hashlib, json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _verdict_ok(v):
    from kpc_release_approved import verdict_ok
    return verdict_ok(v)[0]


def newer_yes(approved, key, held_build, new_build):
    """The approved.json item that lets new_build replace held_build, or None."""
    if not new_build or not held_build or str(new_build) == str(held_build):
        return None
    for it in (approved or {}).get('items') or []:
        if isinstance(it, dict) and it.get('what') == key and str(it.get('build') or '') == str(new_build) and _verdict_ok(it.get('chat11')):
            return it
    return None


def reason(approved, key, held_build, new_build):
    it = newer_yes(approved, key, held_build, new_build)
    if not it:
        return ''
    return f"newer build {new_build} has Quality's KEY YES ({str(it.get('chat11'))[:60]}; {it.get('date', '')} {it.get('time', '')}".rstrip() + ')'


def log_replaced(key, held_build, new_build, why, root='.'):
    """Write data/status/key-copy/replaced-<key>.json: what the old held build was (nothing of it goes live)."""
    d = os.path.join(root, 'data', 'waiting', 'in', 'data', key)
    files = []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, f)
        if os.path.isfile(p):
            files.append({'file': f'data/waiting/in/data/{key}/{f}', 'bytes': os.path.getsize(p), 'sha1': hashlib.sha1(open(p, 'rb').read()).hexdigest()})
    try:
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=root).stdout.strip()
    except Exception:
        head = ''
    rep = {'about': f'{key}: held build {held_build} was REPLACED by {new_build} (newer build with a KEY YES). None of the old build went live; '
                    f'its files are in KPC-Data history at commit {head or "(unknown)"} under data/waiting/in/data/{key}/. Written by kpc-copy-from-links.yml.',
           'key': key, 'old_build': held_build, 'new_build': new_build, 'why': why, 'commit_with_old_files': head,
           'written': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), 'went_live': 0, 'files': files}
    os.makedirs(os.path.join(root, 'data', 'status', 'key-copy'), exist_ok=True)
    out = os.path.join(root, 'data', 'status', 'key-copy', f'replaced-{key}.json')
    with open(out, 'w', encoding='utf-8', newline='') as fh:
        json.dump(rep, fh, indent=1, ensure_ascii=False)
    return rep


if __name__ == '__main__':   # selftest
    A = {'items': [{'what': 'us-key', 'build': 'US-2', 'chat11': 'KEY YES (regrade)', 'date': '2026-11-08'},
                   {'what': 'us-key', 'build': 'US-3', 'chat11': 'YES but NO to 3'},
                   {'what': 'ca-key', 'build': 'CA-9', 'chat11': 'YES'}]}
    assert reason(A, 'us-key', 'US-1', 'US-2')
    assert not reason(A, 'us-key', 'US-1', 'US-3')      # mixed verdict
    assert not reason(A, 'us-key', 'US-1', 'US-4')      # no verdict
    assert not reason(A, 'us-key', 'US-2', 'US-2')      # same build
    assert not reason(A, 'us-key', 'US-1', 'CA-9')      # another key's YES
    print('selftest ok')
