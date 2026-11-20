#!/usr/bin/env python3
"""The person page, the PC kit, and intake (hand-off 05, part 3).

No network. A person's answer is never pre-filled from the bot. No call sign is used.
"""
import csv, datetime, io, json, pathlib, re, zipfile

PAGE_MAX = 300_000


def cards_from_facts(facts_by_area):
    """Parks the bot could not read. Only POTA's own name, type, and link. No bot guess."""
    import kpc_park_pages_work as W
    cards = []
    for area, parks in facts_by_area.items():
        for ref, fact in parks.items():
            if not W.for_a_person(fact):
                continue
            pota = fact.get('pota') or {}
            cards.append({
                'ref': ref,
                'area': area,
                'name': pota.get('name') or '',
                'type': pota.get('type') or '',
                'link': (fact.get('asked') or {}).get('url') or pota.get('link') or '',
            })
    cards.sort(key=lambda c: c['ref'])
    return cards


def person_page(cards):
    """One self-contained file. Empty fields. Phone width. No network."""
    data = json.dumps([{k: c.get(k) or '' for k in ('ref', 'name', 'type', 'link')} for c in cards],
                      ensure_ascii=False).replace('<', '\\u003c')
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Parks for a person</title>
<style>
* { box-sizing: border-box; }
html, body { margin: 0; max-width: 100%; overflow-x: hidden; }
body { font: 16px/1.4 system-ui, sans-serif; padding: 12px; }
h1 { font-size: 1.25rem; margin: 0 0 8px; }
p, label, li { overflow-wrap: anywhere; }
label { display: block; margin: 8px 0 4px; }
input[type=text], textarea { width: 100%; max-width: 100%; font: inherit; padding: 8px; }
textarea { min-height: 4.5em; }
.card { border: 1px solid #bbb; border-radius: 8px; padding: 12px; margin: 12px 0; }
.row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
button { font: inherit; padding: 10px 14px; margin: 6px 8px 6px 0; max-width: 100%; }
a { overflow-wrap: anywhere; }
</style>
</head>
<body>
<h1>Parks for a person</h1>
<p>Open the link. Type only what you see on the page. Leave a box empty when the page does not say it.</p>
<label>Your name<input id="who" type="text" autocomplete="name"></label>
<div id="cards"></div>
<button id="save" type="button">Save answers</button>
<button id="copy" type="button">Copy answers</button>
<p id="msg"></p>
<pre id="dump" hidden></pre>
<script>
const PARKS = ''' + data + ''';
const root = document.getElementById('cards');
for (const p of PARKS) {
  const card = document.createElement('section');
  card.className = 'card';
  card.dataset.ref = p.ref;
  const title = document.createElement('h2');
  title.textContent = p.ref + ' ' + p.name;
  title.style.fontSize = '1.05rem';
  card.appendChild(title);
  const meta = document.createElement('p');
  meta.textContent = p.type;
  card.appendChild(meta);
  if (p.link) {
    const a = document.createElement('a');
    a.href = p.link;
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = p.link;
    card.appendChild(a);
  }
  function field(label, kind, key) {
    const lab = document.createElement('label');
    lab.appendChild(document.createTextNode(label));
    const el = document.createElement(kind === 'box' ? 'input' : (kind === 'area' ? 'textarea' : 'input'));
    if (kind === 'box') { el.type = 'checkbox'; }
    else { el.type = 'text'; }
    el.dataset.f = key;
    lab.appendChild(el);
    card.appendChild(lab);
    return el;
  }
  field('The name at the top of the page', 'text', 'name');
  field("Says '& Preserve' (or two kinds)", 'box', 'combined');
  field('Says it is inside another named area', 'box', 'inside');
  field("That area's name", 'text', 'inside_name');
  field('Size on the page (the number)', 'text', 'size');
  field('The words around the size', 'text', 'size_words');
  field('Named tracts, if a map shows them', 'area', 'tracts');
  field('Could not tell', 'box', 'could_not');
  root.appendChild(card);
}
function answers() {
  const parks = [];
  for (const card of document.querySelectorAll('.card')) {
    const val = (key) => card.querySelector('[data-f="' + key + '"]');
    parks.push({
      ref: card.dataset.ref,
      name: val('name').value.trim(),
      combined: val('combined').checked,
      inside: val('inside').checked,
      inside_name: val('inside_name').value.trim(),
      size: val('size').value.trim(),
      size_words: val('size_words').value.trim(),
      tracts: val('tracts').value.trim(),
      could_not_tell: val('could_not').checked
    });
  }
  const day = new Date().toISOString().slice(0, 10);
  return { who: document.getElementById('who').value.trim(), date: day, parks: parks };
}
function pack() {
  const text = JSON.stringify(answers(), null, 1);
  document.getElementById('dump').textContent = text;
  return text;
}
document.getElementById('save').addEventListener('click', () => {
  const text = pack();
  const blob = new Blob([text], {type: 'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'person-answers.json';
  a.click();
  document.getElementById('msg').textContent = 'Saved person-answers.json on this phone.';
});
document.getElementById('copy').addEventListener('click', async () => {
  const text = pack();
  try {
    await navigator.clipboard.writeText(text);
    document.getElementById('msg').textContent = 'Copied. Paste it into the chat.';
  } catch (e) {
    const box = document.createElement('textarea');
    box.value = text;
    document.body.appendChild(box);
    box.select();
    document.execCommand('copy');
    box.remove();
    document.getElementById('msg').textContent = 'Copied. Paste it into the chat.';
  }
});
</script>
</body>
</html>
'''
    if len(html.encode('utf-8')) > PAGE_MAX:
        raise RuntimeError('person page is over 300 KB')
    return html


def _num(text):
    m = re.search(r'(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?', str(text or '').replace(' ', ''))
    if not m:
        return None
    try:
        return float(m.group(1).replace(',', ''))
    except ValueError:
        return None


def _names(text):
    parts = re.split(r'[\n,;]+', str(text or ''))
    return sorted({p.strip() for p in parts if p.strip()})


def apply_person(facts_by_area, answers, today=''):
    """A person's row wins for the same fact. The bot's row is kept as bot_saw. Returns disagreement rows."""
    who = str((answers or {}).get('who') or '')[:80]
    day = str((answers or {}).get('date') or today or '')[:20]
    disagree = []
    by_ref = {}
    for area, parks in facts_by_area.items():
        for ref, fact in parks.items():
            by_ref[ref] = (area, fact)
    for item in (answers or {}).get('parks') or []:
        if not isinstance(item, dict):
            continue
        ref = item.get('ref')
        if ref not in by_ref:
            continue
        area, fact = by_ref[ref]
        bot = {
            'name': (fact.get('name') or {}).get('best') or '',
            'combined': bool((fact.get('designation') or {}).get('combined')),
            'inside': [i.get('unit') for i in (fact.get('inside_of') or []) if i.get('unit')],
            'sizes': list(fact.get('sizes') or []),
            'parts': list(fact.get('parts') or []),
        }
        fact['bot_saw'] = bot
        fact['person'] = {
            'by': 'person', 'who': who, 'date': day,
            'name': str(item.get('name') or '')[:200],
            'combined': bool(item.get('combined')),
            'inside': bool(item.get('inside')),
            'inside_name': str(item.get('inside_name') or '')[:200],
            'size': str(item.get('size') or '')[:40],
            'size_words': str(item.get('size_words') or '')[:200],
            'tracts': str(item.get('tracts') or '')[:400],
            'could_not_tell': bool(item.get('could_not_tell')),
        }
        if fact['person']['could_not_tell']:
            continue
        import kpc_park_pages_rules as R
        if fact['person']['name']:
            if bot['name'] and R.name_core(bot['name']) != R.name_core(fact['person']['name']):
                disagree.append({'ref': ref, 'field': 'name', 'bot': bot['name'], 'person': fact['person']['name'], 'who': who, 'date': day})
            fact.setdefault('name', {})['best'] = fact['person']['name']
        if fact['person']['combined'] != bot['combined'] and (fact['person']['combined'] or bot['combined']):
            if bot['combined'] != fact['person']['combined']:
                disagree.append({'ref': ref, 'field': 'combined', 'bot': str(bot['combined']), 'person': str(fact['person']['combined']), 'who': who, 'date': day})
            fact.setdefault('designation', {})['combined'] = fact['person']['combined']
        if fact['person']['inside'] and fact['person']['inside_name']:
            if bot['inside'] and fact['person']['inside_name'] not in bot['inside']:
                disagree.append({'ref': ref, 'field': 'inside', 'bot': '; '.join(bot['inside']), 'person': fact['person']['inside_name'], 'who': who, 'date': day})
            fact['inside_of'] = [{'unit': fact['person']['inside_name'], 'kind': '', 'pota_ref': None, 'quote': fact['person']['inside_name']}]
        pn = _num(fact['person']['size'] or fact['person']['size_words'])
        if pn is not None:
            bot_nums = [s.get('acres') for s in bot['sizes'] if isinstance(s.get('acres'), (int, float))]
            if bot_nums and not any(abs(pn - b) <= max(1, 0.02 * b) for b in bot_nums):
                disagree.append({'ref': ref, 'field': 'size', 'bot': '; '.join(str(b) for b in bot_nums), 'person': fact['person']['size'] or fact['person']['size_words'], 'who': who, 'date': day})
            fact['sizes'] = [{'acres': pn, 'as': fact['person']['size_words'] or fact['person']['size'], 'label': '', 'quote': fact['person']['size_words'] or fact['person']['size'],
                              'total': False, 'clean': False, 'why': 'a person typed this', 'by': 'person'}]
        tracts = _names(fact['person']['tracts'])
        if tracts:
            if bot['parts'] and set(tracts) != set(bot['parts']):
                disagree.append({'ref': ref, 'field': 'tracts', 'bot': '; '.join(bot['parts']), 'person': '; '.join(tracts), 'who': who, 'date': day})
            fact['parts'] = tracts
    return disagree


def write_disagreements(path, rows):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    new = not p.is_file()
    with p.open('a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        if new:
            w.writerow(['ref', 'field', 'bot', 'person', 'who', 'date'])
        for r in rows:
            w.writerow([r['ref'], r['field'], r['bot'], r['person'], r['who'], r['date']])


def _safe_names(names):
    out = []
    for name in names:
        parts = pathlib.PurePosixPath(name).parts
        if not parts or any(part in ('..', '') for part in parts) or name.startswith('/'):
            continue
        out.append('/'.join(parts))
    return out


def load_answers_or_zip(path):
    """A person-answers.json, or a PC zip that holds facts and maybe that json. Returns (facts_by_area or None, answers or None)."""
    path = pathlib.Path(path)
    if path.suffix.lower() == '.zip':
        facts, answers = {}, None
        with zipfile.ZipFile(path) as z:
            names = set(_safe_names(z.namelist()))
            for name in sorted(names):
                if name.endswith('person-answers.json'):
                    answers = json.loads(z.read(name).decode('utf-8'))
                m = re.search(r'(?:^|/)facts/([^/]+)\.json$', name)
                if m:
                    doc = json.loads(z.read(name).decode('utf-8'))
                    area = doc.get('area') or m.group(1)
                    facts[area] = doc.get('parks') or {}
        return facts or None, answers
    doc = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(doc, dict) and 'parks' in doc and 'who' not in doc and 'area' in doc:
        return {doc.get('area') or 'area': doc.get('parks') or {}}, None
    return None, doc


def drop_pictures(out_dir, refs, facts_by_area=None):
    """Delete a reviewer's picture once a person has answered, including a path noted on the fact."""
    pic = pathlib.Path(out_dir) / 'pictures'
    refs = {r for r in refs if r}
    if pic.is_dir():
        for ref in refs:
            for ext in ('.jpg', '.jpeg'):
                f = pic / f'{ref}{ext}'
                if f.is_file():
                    f.unlink()
    for parks in (facts_by_area or {}).values():
        for ref, fact in parks.items():
            if ref not in refs:
                continue
            rec = fact.get('picture') or {}
            rel = rec.get('file') if isinstance(rec, dict) else rec
            if rel:
                f = pathlib.Path(out_dir) / str(rel)
                if f.is_file():
                    f.unlink()
            fact.pop('picture', None)


def say_extras():
    """One line each when an optional reader is missing. Never a stack trace."""
    try:
        import pypdf  # noqa: F401
    except Exception:
        print('pypdf is not installed. A PDF is read from the words stored in the file.')
    try:
        import playwright  # noqa: F401
    except Exception:
        print('Playwright is not installed. A page that builds itself stays on the person list.')


KIT_SCRIPTS = (
    'kpc_park_pages.py', 'kpc_park_pages_rules.py', 'kpc_park_pages_work.py', 'kpc_park_pages_person.py',
    'kpc_not_sure.py', 'kpc_manners.py', 'kpc_host_rules.py', 'kpc_truth_bot.py', 'kpc_docs_bot.py',
)


def build_pc_kit(data_dir, areas, out_zip, state_path='', scripts_dir=None, launcher_dir=None):
    """A small zip: the scripts the reader imports, the rows for the named areas, the state. No secrets, no whole repo."""
    data = pathlib.Path(data_dir)
    scripts = pathlib.Path(scripts_dir or pathlib.Path(__file__).resolve().parent)
    launcher = pathlib.Path(launcher_dir) if launcher_dir else scripts.parents[1] / 'tools' / 'park-pages-pc'
    want = set(areas)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name in KIT_SCRIPTS:
            src = scripts / name
            if src.is_file():
                z.writestr(f'scripts/{name}', src.read_bytes())
        for name in ('run-park-pages.sh', 'run-park-pages.bat', 'README-PC.txt'):
            src = launcher / name
            if src.is_file():
                z.writestr(name, src.read_bytes())
        park = data / 'parkinfo'
        if park.is_dir():
            for f in sorted(park.glob('*.json')):
                if f.name == 'index.json':
                    continue
                if want and f.stem not in want:
                    continue
                z.writestr(f'data/parkinfo/{f.name}', f.read_bytes())
        web = data / 'parkinfo-web.json'
        if web.is_file() and want:
            doc = json.loads(web.read_text(encoding='utf-8'))
            parks = doc.get('parks') if isinstance(doc, dict) and 'parks' in doc else doc
            # keep rows whose ref is in the chosen area files
            keep_refs = set()
            for area in want:
                p = park / f'{area}.json'
                if p.is_file():
                    body = json.loads(p.read_text(encoding='utf-8'))
                    keep_refs.update((body.get('parks') or {}))
            if isinstance(parks, dict):
                slim = {k: v for k, v in parks.items() if k in keep_refs}
                z.writestr('data/parkinfo-web.json', json.dumps(slim, ensure_ascii=False).encode('utf-8'))
        for folder in ('docs', 'truth'):
            d = data / folder
            if not d.is_dir():
                continue
            for f in sorted(d.glob('*.json')):
                if want and f.stem not in want:
                    continue
                z.writestr(f'data/{folder}/{f.name}', f.read_bytes())
        if state_path and pathlib.Path(state_path).is_file():
            z.writestr('out/state.json', pathlib.Path(state_path).read_bytes())
    raw = buf.getvalue()
    pathlib.Path(out_zip).write_bytes(raw)
    return raw
