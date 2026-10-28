#!/usr/bin/env python3
"""KPC YouTube comments -> Discord STAFF room, once a day (chat 5, Oct 28 2026; HQ/Brandon 9:30 AM).
Reads the public comments (and replies) on the club's two YouTube channels with the YouTube Data API v3
(secret YOUTUBE_API_KEY, read-only) and posts ONE message a day (split only if Discord's 2000-letter limit
needs it) to the staff room (secret KPC_DISCORD_STAFF_WEBHOOK; never the public webhook).
Nothing new = no post. data/status/youtube-seen.json remembers what was sent (60 days) so nothing posts twice.
DRY_RUN=1 prints instead of posting and saves nothing. A missing secret = a notice and a quiet exit, never red.
Quota: commentThreads/comments/videos/channels calls are 1 unit each; a day is ~5-10 units of the free 10,000."""
import datetime as dt, json, os, sys, time, urllib.parse, urllib.request

HANDLES = ['@ky.pota.campout', '@kpc-n4kpc']
SEEN_F = 'data/status/youtube-seen.json'
KEEP_DAYS = 60
FIRST_DAYS = int(os.environ.get('LOOK_BACK_DAYS') or 7)          # first run (empty memory): only the last week, so the staff room isn't flooded with old comments
API = 'https://www.googleapis.com/youtube/v3/'
KEY = os.environ.get('YOUTUBE_API_KEY', '').strip()
HOOK = os.environ.get('KPC_DISCORD_STAFF_WEBHOOK', '').strip()
DRY = os.environ.get('DRY_RUN', '') in ('1', 'true', 'yes')
NOW = dt.datetime.now(dt.timezone.utc)


def note(title, msg):
    print(f'::notice title={title}::{msg}')


def yt(path, **q):
    q['key'] = KEY
    url = API + path + '?' + urllib.parse.urlencode(q)
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'KPC-bot'}), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read()[:300].decode('utf8', 'replace')
            if e.code in (400, 403, 404): raise RuntimeError(f'{path}: HTTP {e.code} {body}')
        except Exception as e:
            body = str(e)
        time.sleep(5 * (i + 1))
    raise RuntimeError(f'{path}: {body}')


def when(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))


def main():
    if not KEY or (not HOOK and not DRY):
        note('YouTube comments', 'skipped: secret YOUTUBE_API_KEY or KPC_DISCORD_STAFF_WEBHOOK is not set'); return
    try: mem = json.load(open(SEEN_F))
    except Exception: mem = {}
    chans, seen = mem.get('channels', {}), mem.get('seen', {})
    first = not seen
    since = NOW - dt.timedelta(days=FIRST_DAYS if first else KEEP_DAYS)
    new, vids = [], set()
    for h in HANDLES:
        if h not in chans:
            d = yt('channels', part='snippet', forHandle=h)
            if not d.get('items'): note('YouTube comments', f'{h}: channel not found'); continue
            chans[h] = {'id': d['items'][0]['id'], 'title': d['items'][0]['snippet']['title']}
        cid, ctitle = chans[h]['id'], chans[h]['title']
        tok, pages = None, 0
        while pages < 5:
            q = dict(part='snippet,replies', allThreadsRelatedToChannelId=cid, maxResults=100, order='time', textFormat='plainText')
            if tok: q['pageToken'] = tok
            try: d = yt('commentThreads', **q)
            except RuntimeError as e:
                if 'commentsDisabled' in str(e): break
                raise
            pages += 1
            old_page = True
            for th in d.get('items', []):
                top = th['snippet']['topLevelComment']
                vid = th['snippet'].get('videoId', '')
                items = [top]
                n_rep = th['snippet'].get('totalReplyCount', 0)
                reps = (th.get('replies') or {}).get('comments', [])
                if n_rep > len(reps):
                    try: reps = yt('comments', part='snippet', parentId=top['id'], maxResults=100, textFormat='plainText').get('items', reps)
                    except RuntimeError: pass
                items += reps
                for c in items:
                    s = c['snippet']
                    if when(s['publishedAt']) >= since: old_page = False
                    if c['id'] in seen or when(s['publishedAt']) < since: continue
                    if (s.get('authorChannelId') or {}).get('value') == cid: seen[c['id']] = NOW.date().isoformat(); continue   # the club's own replies
                    new.append({'id': c['id'], 'ch': ctitle, 'vid': vid, 'who': s.get('authorDisplayName', '?'),
                                'text': s.get('textOriginal') or s.get('textDisplay', ''), 'at': s['publishedAt'], 'reply': c is not top})
                    vids.add(vid)
            tok = d.get('nextPageToken')
            if not tok or old_page: break
    titles = {}
    vl = [v for v in vids if v]
    for i in range(0, len(vl), 50):
        for v in yt('videos', part='snippet', id=','.join(vl[i:i + 50])).get('items', []):
            titles[v['id']] = v['snippet']['title']
    new.sort(key=lambda c: c['at'])
    mem['channels'] = chans
    if not new:
        note('YouTube comments', 'nothing new')
    else:
        blocks = []
        for c in new:
            t = ' '.join(c['text'].split())
            t = (t[:300] + '…') if len(t) > 300 else t
            t = t.replace('@everyone', '@​everyone').replace('@here', '@​here')
            link = f"https://www.youtube.com/watch?v={c['vid']}&lc={c['id']}" if c['vid'] else 'https://www.youtube.com/'
            blocks.append(f"**{c['ch']}** · {titles.get(c['vid'], 'video')}\n"
                          f"{'↪️ reply' if c['reply'] else '💬'} **{c['who']}**: {t}\n<{link}>")
        head = f"📺 **YouTube comments** ({len(new)} new{f', last {FIRST_DAYS} days' if first else ''})"
        msgs, cur = [], head
        for b in blocks:
            if len(cur) + len(b) + 2 > 1900: msgs.append(cur); cur = ''
            cur = (cur + '\n\n' + b) if cur else b
        msgs.append(cur)
        for m in msgs:
            if DRY: print(m); print('-----'); continue
            body = json.dumps({'content': m, 'username': 'KPC YouTube', 'allowed_mentions': {'parse': []}}).encode()
            req = urllib.request.Request(HOOK, data=body, headers={'Content-Type': 'application/json', 'User-Agent': 'KPC-bot'})
            urllib.request.urlopen(req, timeout=30).read()
            time.sleep(1.5)
        for c in new: seen[c['id']] = NOW.date().isoformat()
        note('YouTube comments', f"{'DRY RUN, would post' if DRY else 'posted'} {len(new)} comment(s) in {len(msgs)} message(s)")
    cut = (NOW - dt.timedelta(days=KEEP_DAYS)).date().isoformat()
    mem['seen'] = {k: v for k, v in seen.items() if v >= cut}
    if DRY: note('YouTube comments', 'dry run: memory not saved'); return
    os.makedirs(os.path.dirname(SEEN_F), exist_ok=True)
    json.dump(mem, open(SEEN_F, 'w'), indent=0, sort_keys=True)


if __name__ == '__main__':
    try: main()
    except Exception as e:
        note('YouTube comments PROBLEM', str(e)[:400]); sys.exit(0)
