#!/usr/bin/env python3
"""PICTURE SAVER: WHICH PAGE OF A DOCUMENT IS THE MAP (KPC owner, 2026-11-11). Standard library + Pillow; for PDFs also pypdf and
poppler (pdfinfo, pdftoppm, pdftotext), all already installed by the look-up workflow. No network.

Before: kpc_lookup.py save-map kept the page it was asked for, and AUTO-3 (kpc_auto_flow.py) always asks for page 1. For management
plans, brochures and fact sheets page 1 is a cover, a photo or text (Nov 11 run: 32 of 88 NO FIT and 11 of 32 NO LINE pictures).
Now every page (the first MAX_PAGES) of a PDF is looked at and the map page is kept; when no page qualifies the saver keeps exactly
the page it kept before, and the row says why (map_page_found false = 'no map page found', null = 'cannot tell').

PER PAGE
  geo     the page carries its own GeoPDF coordinates (/VP /Measure /GPTS, or /LGIDict). Only an agency map does that.
  words   words on the page (pdftotext); map_words = how many DIFFERENT map words it has (map, legend, scale, km, trail, parking,
          road, lake, carte, légende, échelle, sentier ...). A cover has a title and few or none; a map has labels and a legend.
  picture the page drawn small (THUMB px) and cut in CELL px cells, each one 'flat' (one colour), 'graphic' (a few colours: lines,
          labels, tints) or 'photo' (many colours, none dominant). img = 2 x graphic + flat - 2 x (photo share over one half).
          Covers and photo pages are mostly photo cells; line and tint maps mostly flat and graphic cells. An aerial-photo map is
          photo cells too, which is why the picture part never decides on its own that a page is NOT a map (see below).
A PAGE IS A MAP when it has GeoPDF coordinates, or it has at most TEXT_WORDS words and at least 2 different map words.
score = 6 x geo + (2 + 0.5 x map words, up to 6) when it is a map by words - 3 when it is a text page (more than TEXT_WORDS words) + img.
CHOICE
  1. pages that are maps: the best score is kept (the lowest page number on a tie);
  2. none, but the PDF has text: the page asked for is kept, map_page_found = false ('no map page found');
  3. none, and no text and no GeoPDF anywhere (a scanned PDF): the page asked for is kept unless another page's picture score beats
     it by IMG_MARGIN; map_page_found = null ('cannot tell'). The picture score alone never says 'not a map' (it cannot tell an
     aerial-photo map from a cover photo: on the 151 saved Nov 11 pictures, the cut that flags no traced map also flags 3 real maps).
A single picture (JPEG / PNG source) has nothing to choose from: it is kept as before, map_page_found = null.
  python3 kpc_map_page.py score <file.pdf | picture> [...]     prints what would be kept and why
"""
import json, os, re, subprocess, sys, tempfile

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
THUMB, CELL = 320, 16
MAX_PAGES = 60
TEXT_WORDS = 250
IMG_MARGIN = 1.0
MAP_WORDS = re.compile(r"(?<![\w])(maps?|cartes?|legend|l[ée]gende|scale|[ée]chelle|north|nord|kilomet\w*|km|met(?:er|re)s?|miles?|mi"
                       r"|boundary|boundaries|limite|parking|stationnement|trails?|sentiers?|roads?|chemin|route|lakes?|lac|rivers?"
                       r"|rivi[eè]re|campground|camping|campsites?|boat|launch|ramp|picnic|pique-nique|toilets?|restrooms?|you are here"
                       r"|vous [eê]tes ici)(?![\w])", re.I)


def cells(img):
    """(photo, flat, graphic) shares of the page's cells."""
    im = img.convert('RGB')
    im.thumbnail((THUMB, THUMB))
    q = im.quantize(colors=32, method=Image.Quantize.MEDIANCUT)
    w, h = q.size
    n = ph = fl = gr = 0
    for y in range(0, h - CELL + 1, CELL):
        for x in range(0, w - CELL + 1, CELL):
            cnt = sorted((c for c, _i in q.crop((x, y, x + CELL, y + CELL)).getcolors(CELL * CELL)), reverse=True)
            tot = float(CELL * CELL)
            dom, k = cnt[0] / tot, sum(1 for c in cnt if c / tot >= 0.03)
            n += 1
            if dom >= 0.9:
                fl += 1
            elif dom >= 0.5 and k <= 5:
                gr += 1
            elif dom < 0.45 and k >= 6:
                ph += 1
    n = max(n, 1)
    return round(ph / n, 3), round(fl / n, 3), round(gr / n, 3)


def img_term(c):
    photo, flat, graphic = c
    return round(2.0 * graphic + flat - 2.0 * max(0.0, photo - 0.5), 3)


def text_signals(text):
    """(words, number of different map words) of one page's text."""
    t = text or ''
    return len(t.split()), len({m.lower().replace('é', 'e').replace('è', 'e').rstrip('s') for m in MAP_WORDS.findall(t)})


def page_verdict(c, geo=False, words=None, map_words=0):
    """(is_map, score, why) for one page."""
    it = img_term(c)
    s, why = it, []
    by_words = words is not None and words <= TEXT_WORDS and map_words >= 2
    is_map = bool(geo) or by_words
    if geo:
        s += 6.0
        why.append('GeoPDF coordinates')
    if by_words:
        s += 2.0 + min(6, map_words) * 0.5
        why.append(f'{map_words} map words in {words} words')
    if words is not None and words > TEXT_WORDS:
        s -= 3.0
        why.append(f'a text page ({words} words)')
    why.append(f'picture: photo {c[0]:.2f}, flat {c[1]:.2f}, graphic {c[2]:.2f}')
    return is_map, round(s, 2), '; '.join(why)


# ------------------------------------------------------------------ PDFs
def pdf_pages(pdf_path):
    try:
        out = subprocess.run(['pdfinfo', str(pdf_path)], capture_output=True, text=True, timeout=60).stdout
        m = re.search(r'^Pages:\s+(\d+)', out, re.M)
        if m:
            return int(m.group(1))
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(pdf_path)).pages)
    except Exception:  # noqa: BLE001
        return 0


def geo_pages(pdf_path, last):
    """Pages (1-based, up to last) with their own GeoPDF coordinates; none when pypdf is missing or the file does not read."""
    out = set()
    try:
        from pypdf import PdfReader
        for i, pg in enumerate(PdfReader(str(pdf_path)).pages[:last]):
            vp = pg.get('/VP')
            for v in (vp.get_object() if vp is not None else []) or []:
                m = v.get_object().get('/Measure')
                if m is not None and '/GPTS' in m.get_object():
                    out.add(i + 1)
            if pg.get('/LGIDict') is not None:
                out.add(i + 1)
    except Exception:  # noqa: BLE001
        pass
    return out


def page_texts(pdf_path, last):
    """{page: text} from pdftotext (a form feed ends each page); {} when poppler is missing."""
    try:
        t = subprocess.run(['pdftotext', '-f', '1', '-l', str(last), '-layout', str(pdf_path), '-'], capture_output=True,
                           text=True, timeout=300).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    return {i + 1: p for i, p in enumerate(t.split('\f')[:last])}


def page_thumbs(pdf_path, last):
    """{page: PIL image} for pages 1..last, drawn small by pdftoppm; {} when poppler is missing."""
    out = {}
    with tempfile.TemporaryDirectory() as td:
        try:
            subprocess.run(['pdftoppm', '-f', '1', '-l', str(last), '-scale-to', str(THUMB), '-png', str(pdf_path),
                            os.path.join(td, 'p')], capture_output=True, timeout=900)
        except (OSError, subprocess.SubprocessError):
            return {}
        for fn in os.listdir(td):
            m = re.match(r'p-0*(\d+)\.png$', fn)
            if m:
                with Image.open(os.path.join(td, fn)) as im:
                    out[int(m.group(1))] = im.copy()
    return out


def choose(pages, today=1, total=None):
    """pages: {page: (cells, geo, words or None, map_words)}. Returns the row's page_pick dict."""
    v = {p: page_verdict(*a) for p, a in pages.items()}
    res = {'today': today, 'pages': total or len(pages), 'looked': len(pages), 'scores': {str(p): s for p, (_m, s, _w) in sorted(v.items())}}
    maps = [p for p, (m, _s, _w) in v.items() if m]
    has_text = any(a[2] for a in pages.values()) or any(a[1] for a in pages.values())
    if maps:
        kept = max(maps, key=lambda p: (v[p][1], -p))
        res.update(kept=kept, map_page_found=True, score=v[kept][1], why=v[kept][2],
                   how='the map page' + ('' if kept == today else f' (page {today} is not: {v[today][2]})' if today in v else ''))
    elif has_text:
        res.update(kept=today, map_page_found=False, score=v.get(today, (0, None, ''))[1], how='no map page found',
                   why=f"no page has GeoPDF coordinates or a map's words (at most {TEXT_WORDS} words, 2+ map words)"
                       + (f"; looked at {len(pages)} of {total} pages" if total and total > len(pages) else ''))
    else:
        best = max(v, key=lambda p: (v[p][1], -p))
        kept = best if today not in v or v[best][1] >= v[today][1] + IMG_MARGIN else today
        res.update(kept=kept, map_page_found=None, score=v[kept][1], why=v[kept][2],
                   how="cannot tell (no text and no GeoPDF in the PDF): " + ('the page that looks most like a map' if kept != today else 'the page asked for'))
    return res


def choose_pdf_page(pdf_path, today=1):
    n = pdf_pages(pdf_path)
    last = max(1, min(n or 1, MAX_PAGES))
    th = page_thumbs(pdf_path, last)
    if not th:
        return {'kept': today, 'today': today, 'map_page_found': None, 'how': 'the page asked for: the pages could not be drawn here',
                'pages': n, 'looked': 0}
    geo, texts = geo_pages(pdf_path, last), page_texts(pdf_path, last)
    pages = {}
    for p, im in th.items():
        words, mw = text_signals(texts.get(p, '')) if texts else (None, 0)
        pages[p] = (cells(im), p in geo, words, mw)
    return choose(pages, today=today, total=n)


def judge_picture(img):
    """A single picture: nothing to choose, nothing flagged (the picture part never says 'not a map' on its own)."""
    c = cells(img)
    return {'kept': None, 'today': None, 'map_page_found': None, 'how': 'a single picture: nothing to choose', 'pages': 1, 'looked': 1,
            'score': img_term(c), 'why': f'picture: photo {c[0]:.2f}, flat {c[1]:.2f}, graphic {c[2]:.2f}'}


def main(argv):
    if len(argv) < 2 or argv[0] != 'score':
        print(__doc__)
        return 2
    for f in argv[1:]:
        if f.lower().endswith('.pdf'):
            print(f, json.dumps(choose_pdf_page(f)))
        else:
            with Image.open(f) as im:
                print(f, json.dumps(judge_picture(im)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
