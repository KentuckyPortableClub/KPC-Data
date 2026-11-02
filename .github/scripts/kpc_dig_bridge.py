#!/usr/bin/env python3
"""DETECTIVE FOLDED INTO THE LOOK-UP BOT (chat 10, Oct 31 2026; Brandon 8:10 PM 'fold detective into look up').
A chat asks a dig question the same way as any look-up: a file on branch `lookup`, requests/<chat>-<id>.json =
  {"chat": 8, "kind": "dig", "ref": "US-12752", "park": "...", "what": "tract|acreage|owner|who runs it|handover|access|outline", "note": "the question"}
The look-up bot skips 'dig' requests; this bridge (in the detective's daily run):
  in   copies every unanswered dig request into data/detective/questions.json (id = the request name)
  out  writes the detective's answer back to the lookup branch as answers/<id>.json (same place as every look-up answer)
  python3 kpc_dig_bridge.py in <lookup dir> | out <lookup dir>     Never fails."""
import json, pathlib, sys, time

Q = pathlib.Path('data/detective/questions.json'); A = pathlib.Path('data/detective/answers.json')


def load(p, d):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception: return d  # noqa: BLE001


def dig_requests(lk):
    out = {}
    for p in sorted((lk / 'requests').glob('*.json')):
        r = load(p, {})
        if isinstance(r, dict) and r.get('kind') == 'dig' and not (lk / 'answers' / p.name).exists(): out[p.stem] = r
    return out


def cmd_in(lk):
    D = load(Q, {'questions': []}); qs = D.setdefault('questions', []); have = {q.get('id') for q in qs}; n = 0
    for rid, r in dig_requests(lk).items():
        if rid in have: continue
        qs.append({'id': rid, 'ref': r.get('ref', ''), 'park': r.get('park', ''), 'area': r.get('area', ''), 'what': r.get('what', 'outline'),
                   'note': r.get('note') or r.get('report') or '', 'added': time.strftime('%Y-%m-%d'), 'by': f"chat {r.get('chat')} (look-up dig)"})
        n += 1
    json.dump(D, open(Q, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'::notice title=Dig bridge::{n} new dig question(s) from the look-up branch')
    print(f'NEW={n}')


def cmd_out(lk):
    ans = (load(A, {}) or {}).get('answers') or {}; n = 0
    (lk / 'answers').mkdir(parents=True, exist_ok=True)
    for rid, r in dig_requests(lk).items():
        a = ans.get(rid)
        if not a: continue
        json.dump({'request': f'requests/{rid}.json', 'id': rid, 'chat': r.get('chat'), 'kind': 'dig', 'asked': r, 'answered': time.strftime('%Y-%m-%d %H:%MZ', time.gmtime()),
                   'short': f"{a.get('result')}: {str(a.get('answer') or a.get('why') or '')[:200]}", 'results': [a]}, open(lk / 'answers' / f'{rid}.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        n += 1
    print(f'::notice title=Dig bridge::{n} dig answer(s) written to the look-up branch')


if __name__ == '__main__':
    try:
        a = sys.argv[1:]
        {'in': cmd_in, 'out': cmd_out}[a[0]](pathlib.Path(a[1]))
    except Exception as e: print(f'::notice title=Dig bridge::stopped ({type(e).__name__}: {e})')  # noqa: BLE001
    sys.exit(0)
