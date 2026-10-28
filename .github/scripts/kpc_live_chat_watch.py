#!/usr/bin/env python3
"""KPC LIVE CHAT WATCHER (chat 5, Oct 28 2026; HQ/Brandon 4:32 PM). READ ONLY: never posts in YouTube.
Watches the live chat of the YouTube streams in VIDEOS (ids, comma separated). Until a stream goes live it re-checks
every 5 min (videos.list, 1 unit); then it reads liveChatMessages.list (5 units) at YouTube's own pollingIntervalMillis,
never faster than 20 s. A message that matches WORDS -> ONE post to the Discord STAFF room (stream, author, message,
time, stream link + the ready reply staff paste as themselves). Never repeats a message. Stops per stream when it ends
(or its chat closes); stops everything after MAX_HOURS. Secrets: YOUTUBE_API_KEY, KPC_DISCORD_STAFF_WEBHOOK.
Missing secret / quota used up / any error = a notice, never a red run. DRY_RUN=1 prints instead of posting."""
import datetime as dt, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

KEY = os.environ.get('YOUTUBE_API_KEY', '').strip()
HOOK = os.environ.get('KPC_DISCORD_STAFF_WEBHOOK', '').strip()
DRY = os.environ.get('DRY_RUN', '') in ('1', 'true')
VIDEOS = [v.strip() for v in re.split(r'[,\s]+', os.environ.get('VIDEOS', '')) if v.strip()]
MAX_HOURS = float(os.environ.get('MAX_HOURS') or 5)
WORDS = re.compile(os.environ.get('WORDS') or r'camp\s*out|\bkpc\b|kentucky\s+portable|taylorsville', re.I)
REPLY = ('Thanks for asking! The KPC 2027 Campout is Sept 24-26, 2027 at Taylorsville Lake State Park, Kentucky. '
         'Details: https://kentuckyportableclub.github.io/KPC-Links/campout.html')
CT = ZoneInfo('America/Chicago')
START = time.time()
API = 'https://www.googleapis.com/youtube/v3/'


def note(msg): print(f'::notice title=Live chat watcher::{msg}', flush=True)


class Quota(Exception): pass


def yt(path, **q):
    q['key'] = KEY
    try:
        with urllib.request.urlopen(API + path + '?' + urllib.parse.urlencode(q), timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf8', 'replace')
        if 'quotaExceeded' in body or 'dailyLimitExceeded' in body: raise Quota()
        reason = (re.search(r'"reason":\s*"(\w+)"', body) or [None, f'HTTP {e.code}'])[1]
        return {'_error': reason}
    except Exception as e:  # noqa: BLE001
        return {'_error': type(e).__name__}


def post(text):
    if DRY: print(text + '\n-----', flush=True); return
    for i in range(3):
        try:
            req = urllib.request.Request(HOOK, data=json.dumps({'content': text[:1990], 'username': 'KPC Live Chat',
                                         'allowed_mentions': {'parse': []}}).encode(), headers={'Content-Type': 'application/json', 'User-Agent': 'KPC-bot'})
            urllib.request.urlopen(req, timeout=30).read(); return
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(float(json.loads(e.read() or b'{}').get('retry_after', 2)) + 0.5); continue
            note(f'staff room post failed: HTTP {e.code}'); return
        except Exception as e:  # noqa: BLE001
            note(f'staff room post failed: {type(e).__name__}'); time.sleep(3)


def safe(s):
    return s.replace('@everyone', '@​everyone').replace('@here', '@​here').replace('`', "'")


def main():
    if not KEY or (not HOOK and not DRY) or not VIDEOS:
        note('skipped: YOUTUBE_API_KEY / KPC_DISCORD_STAFF_WEBHOOK not set, or no streams given'); return
    S = {v: {'state': 'waiting', 'next': 0, 'chat': None, 'tok': None, 'title': v, 'seen': set(), 'hits': 0, 'read': 0} for v in VIDEOS}
    note(f'watching {len(VIDEOS)} stream(s) for up to {MAX_HOURS:g} h: ' + ', '.join(VIDEOS))
    while time.time() - START < MAX_HOURS * 3600:
        live = [v for v, s in S.items() if s['state'] != 'done']
        if not live: break
        now = time.time()
        for v in live:
            s = S[v]
            if now < s['next']: continue
            if s['state'] == 'waiting':
                d = yt('videos', part='snippet,liveStreamingDetails', id=v)
                it = (d.get('items') or [None])[0]
                if not it:
                    note(f'{v}: not found ({d.get("_error", "no such video")}); re-checking in 5 min'); s['next'] = now + 300; continue
                s['title'] = it['snippet']['title']
                ls = it.get('liveStreamingDetails') or {}
                if ls.get('actualEndTime'):
                    note(f'{v}: stream already ended'); s['state'] = 'done'; continue
                if ls.get('activeLiveChatId'):
                    s['chat'], s['state'] = ls['activeLiveChatId'], 'live'
                    note(f'{v}: live, reading chat ("{s["title"][:60]}")')
                else:
                    s['next'] = now + 300; continue
            q = dict(liveChatId=s['chat'], part='snippet,authorDetails', maxResults=2000)
            if s['tok']: q['pageToken'] = s['tok']
            d = yt('liveChat/messages', **q)
            if '_error' in d:
                if d['_error'] in ('liveChatEnded', 'liveChatNotFound', 'liveChatDisabled', 'forbidden'):
                    note(f'{v}: chat closed ({d["_error"]}); {s["read"]} messages read, {s["hits"]} posted'); s['state'] = 'done'
                else:
                    s['next'] = now + 30
                continue
            s['tok'] = d.get('nextPageToken')
            if d.get('offlineAt'):
                s['state'] = 'done'; note(f'{v}: stream ended; {s["read"]} messages read, {s["hits"]} posted')
            s['next'] = now + max(20, (d.get('pollingIntervalMillis') or 20000) / 1000)
            for m in d.get('items', []):
                if m['id'] in s['seen']: continue
                s['seen'].add(m['id']); s['read'] += 1
                txt = (m['snippet'].get('displayMessage') or '').strip()
                if not txt or not WORDS.search(txt): continue
                s['hits'] += 1
                who = (m.get('authorDetails') or {}).get('displayName', '?')
                at = dt.datetime.fromisoformat(m['snippet']['publishedAt'].replace('Z', '+00:00')).astimezone(CT)
                post(f"🔴 **Live chat** · {safe(s['title'][:90])}\n**{safe(who)}** ({at:%-I:%M %p} Central): {safe(txt[:400])}\n"
                     f"<https://www.youtube.com/live/{v}>\nReady reply (paste it as yourself):\n```{REPLY}```")
        time.sleep(5)
    for v, s in S.items():
        if s['state'] != 'done': note(f'{v}: stopped at the {MAX_HOURS:g} h limit ({s["state"]}); {s["read"]} messages read, {s["hits"]} posted')


if __name__ == '__main__':
    try: main()
    except Quota:
        note('stopped: the YouTube daily quota is used up'); post('⚠️ KPC Live Chat watcher stopped: the YouTube daily quota is used up. Please watch the stream chat by hand.') if HOOK and not DRY else None
    except Exception as e:  # noqa: BLE001
        note(f'stopped early: {type(e).__name__}: {str(e)[:200]}')
    sys.exit(0)
