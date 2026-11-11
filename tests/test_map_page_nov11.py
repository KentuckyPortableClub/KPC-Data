#!/usr/bin/env python3
"""Picture saver keeps the MAP page (KPC owner, 2026-11-11). Offline: synthetic pages and PDFs, a fake fetch; no network.

Before: save-map kept page 1 (AUTO-3 always asks for page 1), so a management plan's cover, a brochure's photo or a text page was
saved and traced (NO FIT / NO LINE). Now kpc_map_page.py looks at every page and keeps the map; with none it keeps page 1 and says
'no map page found', and kpc_picture_prep.py leaves such a park out of the tracer's input with that reason (not-maps.json).
  1. choose() on page pictures + text signals: map in position 2, 3, last; a single-page map unchanged; GeoPDF wins; no map page =
     today's page + the flag; a scanned PDF with no text is never flagged ('cannot tell').
  2. the same through real PDFs (Pillow pages + a pypdf text layer + GeoPDF keys) with poppler, when poppler and pypdf are here.
  3. kpc_lookup.save_map with a fake fetch: the map page is rendered and saved, the row says which page and why; a page a person
     named is kept as asked; a single picture is unchanged.
  4. kpc_picture_prep.py leaves out a 'no map page found' row and lists it in not-maps.json.
Prints PASS / FAIL lines, ends ALL PASS / SOME FAILED."""
import io, json, math, os, pathlib, random, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
sys.path.insert(0, str(S))
ok = True


def check(msg, c):
    global ok
    ok &= bool(c)
    print(('PASS ' if c else 'FAIL ') + msg)


try:
    from PIL import Image, ImageDraw
except ImportError as e:
    print(f'NOTE: Pillow missing here ({e}); the look-up workflow installs it. Static checks only.')
    src = (S / 'kpc_lookup.py').read_text(encoding='utf-8')
    check('save-map asks the page chooser', 'pick_page(kind, body, pages, q)' in src)
    print('ALL PASS' if ok else 'SOME FAILED')
    sys.exit(0 if ok else 1)
import kpc_map_page as MP

W, H = 850, 1100


def cover(seed=0):
    """A management-plan cover: a photo collage, a strong title band with a few words."""
    rnd = random.Random(seed)
    im = Image.new('RGB', (W, H), (250, 250, 250))
    px = im.load()
    for (x0, y0, x1, y1) in ((0, 0, W, 330), (0, 560, W, H)):
        for y in range(y0, y1):
            for x in range(x0, x1):
                v = (x * 7 + y * 13) % 40
                px[x, y] = (60 + rnd.randrange(120) + v, 80 + rnd.randrange(110), 40 + rnd.randrange(100))
    ImageDraw.Draw(im).rectangle((0, 330, W, 560), fill=(205, 70, 30))
    return im


def photo(seed=1):
    rnd = random.Random(seed)
    im = Image.new('RGB', (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            px[x, y] = (rnd.randrange(30, 200), rnd.randrange(60, 220), rnd.randrange(20, 160))
    return im


def text_page(seed=2):
    rnd = random.Random(seed)
    im = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for row in range(60, H - 60, 22):
        x = 70
        while x < W - 90:
            wl = rnd.randrange(12, 60)
            d.rectangle((x, row, x + wl, row + 9), fill=(30, 30, 30))
            x += wl + 9
    return im


def map_page(seed=3):
    rnd = random.Random(seed)
    im = Image.new('RGB', (W, H), (238, 236, 225))
    d = ImageDraw.Draw(im)
    d.polygon([(150, 200), (650, 160), (720, 600), (420, 820), (130, 640)], fill=(190, 220, 170), outline=(40, 120, 40))
    d.ellipse((480, 650, 760, 900), fill=(150, 200, 235))
    for _ in range(18):
        d.line([(rnd.randrange(W), rnd.randrange(H)), (rnd.randrange(W), rnd.randrange(H))], fill=(90, 90, 90), width=3)
    for _ in range(25):
        x, y = rnd.randrange(60, W - 120), rnd.randrange(60, H - 30)
        d.rectangle((x, y, x + rnd.randrange(30, 90), y + 8), fill=(20, 20, 20))
    d.rectangle((40, 40, W - 40, H - 40), outline=(0, 0, 0), width=3)
    return im


PAGE = {'cover': cover, 'photo': photo, 'text': text_page, 'map': map_page}
WORDS = {'cover': 'Fort Example National Historic Site Management Plan 2018',
         'photo': '',
         'text': ' '.join(['the park plan describes the vision and the objectives for the site over the next ten years'] * 30),
         'map': 'Legend Trail Parking Lake Scale 0 1 km North Picnic area Boat launch Fort Example'}
cells_of = {k: MP.cells(f()) for k, f in PAGE.items()}


def sig(kind, geo=False, text=True):
    w, m = MP.text_signals(WORDS[kind]) if text else (0, 0)
    return (cells_of[kind], geo, w if text else 0, m)


# ---- 1. the choice, on page pictures + text signals
for order, want in ((['cover', 'map', 'text', 'photo'], 2), (['cover', 'text', 'map', 'photo'], 3),
                    (['cover', 'photo', 'text', 'text', 'map'], 5), (['map'], 1), (['map', 'cover', 'text'], 1)):
    r = MP.choose({i + 1: sig(k) for i, k in enumerate(order)}, today=1)
    check(f'pages {order}: page 1 before, page {r["kept"]} now ({r["how"]}; map page found {r["map_page_found"]})',
          r['kept'] == want and r['map_page_found'] is True)
r = MP.choose({1: sig('cover'), 2: sig('text'), 3: sig('photo')}, today=1)
check(f'no map page (cover, text, photo): today\'s page 1 is kept and flagged: "{r["how"]}"', r['kept'] == 1 and r['map_page_found'] is False)
r = MP.choose({1: sig('cover'), 2: sig('photo', geo=True, text=False), 3: sig('map', text=False)}, today=1)
check(f'a GeoPDF page wins even when it looks like a photo (an aerial map): kept page {r["kept"]}', r['kept'] == 2 and r['map_page_found'] is True)
r = MP.choose({1: sig('cover', text=False), 2: sig('photo', text=False)}, today=1)
check(f'a scanned PDF with no text and no GeoPDF is never flagged: page {r["kept"]}, map page found {r["map_page_found"]}',
      r['kept'] == 1 and r['map_page_found'] is None)
r = MP.choose({1: sig('photo', text=False), 2: sig('map', text=False)}, today=1)
check(f'a scanned PDF: a page that looks clearly more like a map than page 1 is kept ({r["kept"]}), still "cannot tell"',
      r['kept'] == 2 and r['map_page_found'] is None)
w, m = MP.text_signals(WORDS['text'])
check(f'a text page with map words is not a map ({w} words)', w > MP.TEXT_WORDS)
check('map words count different words (Legend, Trail, Parking, Lake, Scale, km, North, Picnic, Boat): '
      + str(MP.text_signals(WORDS['map'])[1]), MP.text_signals(WORDS['map'])[1] >= 6)
check('French map words count (Légende, Échelle, Sentier, Stationnement)', MP.text_signals('Légende Échelle Sentier Stationnement')[1] >= 3)
check('the picture part on its own: a map page scores above a cover, a photo and a text page',
      MP.img_term(cells_of['map']) > max(MP.img_term(cells_of[k]) for k in ('cover', 'photo')))

# ---- 2. real PDFs (Pillow pages + text layer + GeoPDF keys), through poppler
have_poppler = all(shutil.which(t) for t in ('pdftoppm', 'pdftotext', 'pdfinfo'))
try:
    import pypdf  # noqa: F401
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import ArrayObject, DictionaryObject, FloatObject, NameObject, NumberObject, StreamObject
    have_pypdf = True
except ImportError:
    have_pypdf = False


def make_pdf(path, kinds, geo_page=None, text=True):
    """Pages drawn with Pillow, each with its words as a real (invisible-colour-free, tiny) text layer from pypdf, and GeoPDF keys on one."""
    buf = io.BytesIO()
    ims = [PAGE[k](i) for i, k in enumerate(kinds)]
    ims[0].save(buf, 'PDF', save_all=True, append_images=ims[1:], resolution=100)
    r = PdfReader(io.BytesIO(buf.getvalue()))
    wtr = PdfWriter()
    for i, (pg, k) in enumerate(zip(r.pages, kinds)):
        if text and WORDS[k]:
            words = WORDS[k].replace('\\', '').replace('(', '').replace(')', '')
            lines = [words[j:j + 90] for j in range(0, len(words), 90)]
            ops = 'BT /KF 6 Tf 20 20 Td ' + ' '.join(f'({ln}) Tj 0 7 Td' for ln in lines) + ' ET'
            st = StreamObject()
            st._data = ops.encode('latin-1', 'replace')
            font = DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'),
                                     NameObject('/BaseFont'): NameObject('/Helvetica')})
            res = pg.get('/Resources').get_object()
            fonts = DictionaryObject({NameObject('/KF'): font})
            res[NameObject('/Font')] = fonts
            cont = pg.get_contents()
            data = (cont.get_data() if cont is not None else b'') + b'\n' + st._data
            new = StreamObject()
            new._data = data
            pg[NameObject('/Contents')] = wtr._add_object(new)
        if geo_page == i + 1:
            meas = DictionaryObject({NameObject('/Type'): NameObject('/Measure'), NameObject('/Subtype'): NameObject('/GEO'),
                                     NameObject('/GPTS'): ArrayObject([FloatObject(v) for v in (38.0, -85.0, 38.1, -85.0, 38.1, -84.9, 38.0, -84.9)])})
            vp = DictionaryObject({NameObject('/Type'): NameObject('/Viewport'), NameObject('/BBox'): ArrayObject([NumberObject(0)] * 4),
                                   NameObject('/Measure'): meas})
            pg[NameObject('/VP')] = ArrayObject([vp])
        wtr.add_page(pg)
    with open(path, 'wb') as f:
        wtr.write(f)


if not (have_poppler and have_pypdf):
    print(f'NOTE: poppler ({have_poppler}) or pypdf ({have_pypdf}) missing here: the PDF drawing and reading part is checked by the '
          'look-up workflow (it installs poppler-utils and pypdf); the choice itself is checked above on page pictures')
else:
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, 'plan.pdf')
        make_pdf(p, ['cover', 'text', 'photo', 'map', 'text'])
        r = MP.choose_pdf_page(p, today=1)
        check(f'PDF cover/text/photo/map/text: page 1 before, page {r["kept"]} now ({r["how"]}); {r["pages"]} pages looked at',
              r['kept'] == 4 and r['map_page_found'] is True and r['pages'] == 5)
        make_pdf(p, ['map'])
        r = MP.choose_pdf_page(p, today=1)
        check(f'single-page map PDF: unchanged (page {r["kept"]})', r['kept'] == 1 and r['map_page_found'] is True)
        make_pdf(p, ['cover', 'text', 'photo'])
        r = MP.choose_pdf_page(p, today=1)
        check(f'PDF with no map page: page 1 kept, "{r["how"]}"', r['kept'] == 1 and r['map_page_found'] is False)
        make_pdf(p, ['cover', 'photo', 'text'], geo_page=2, text=True)
        r = MP.choose_pdf_page(p, today=1)
        check(f'PDF whose page 2 carries GeoPDF coordinates: page {r["kept"]} ({r.get("why", "")[:60]})', r['kept'] == 2 and r['map_page_found'] is True)

        # ---- 3. save_map with a fake fetch (no network): the map page is rendered and the row says which and why
        import kpc_lookup as LK
        make_pdf(p, ['cover', 'text', 'map'])
        body = open(p, 'rb').read()
        pic = pathlib.Path(td) / 'pm'
        LK.PIC = pic
        LK.fetch = lambda u: ('pdf', body, u, '')
        res = LK.save_map({'ref': 'US-0001', 'name': 'Example Park', 'agency': 'Example Agency', 'url': 'https://example.gov/plan.pdf', 'pages': 1}, 'test-1')
        row = json.load(open(pic / 'rows' / 'US-0001_example-park.json'))
        check(f"save-map: page {row['page']} saved (was page 1), the row says how: {row['page_pick']['how']}",
              row['page'] == [3] and row['page_pick']['map_page_found'] is True and (pic / 'maps' / 'US-0001_example-park.jpg').exists())
        def _diff(a, b):
            a, b = a.convert('L').resize((64, 80)), b.convert('L').resize((64, 80))
            return sum(abs(x - y) for x, y in zip(a.tobytes(), b.tobytes())) / (64 * 80.0)
        with Image.open(pic / 'maps' / 'US-0001_example-park.jpg') as im:
            dd = {k: round(_diff(im, PAGE[k](i)), 1) for i, k in enumerate(['cover', 'text', 'map'])}
            check(f'the saved picture is the map page (mean difference to each page: {dd})', min(dd, key=dd.get) == 'map')
        res = LK.save_map({'ref': 'US-0002', 'name': 'Named Page', 'url': 'https://example.gov/plan.pdf', 'pages': 2}, 'test-2')
        row = json.load(open(pic / 'rows' / 'US-0002_named-page.json'))
        check('save-map: a page a person named (2) is kept as asked', row['page'] == [2] and 'kept as asked' in row['page_pick']['how'])
        res = LK.save_map({'ref': 'US-0003', 'name': 'No Pick', 'url': 'https://example.gov/plan.pdf', 'pages': 1, 'pick_page': False}, 'test-3')
        row = json.load(open(pic / 'rows' / 'US-0003_no-pick.json'))
        check('save-map: "pick_page": false keeps page 1 (today\'s rule)', row['page'] == [1])
        make_pdf(p, ['cover', 'text', 'photo'])
        body = open(p, 'rb').read()
        LK.fetch = lambda u: ('pdf', body, u, '')
        LK.save_map({'ref': 'US-0004', 'name': 'Plan Only', 'url': 'https://example.gov/plan.pdf', 'pages': 1}, 'test-4')
        row4 = json.load(open(pic / 'rows' / 'US-0004_plan-only.json'))
        check(f"save-map: no map page: page 1 saved as before and flagged ({row4['page_pick']['how']})",
              row4['page'] == [1] and row4['page_pick']['map_page_found'] is False)
        jb = io.BytesIO()
        map_page().save(jb, 'JPEG')
        LK.fetch = lambda u: ('img', jb.getvalue(), u, '')
        LK.save_map({'ref': 'US-0005', 'name': 'One Picture', 'url': 'https://example.gov/map.jpg'}, 'test-5')
        row5 = json.load(open(pic / 'rows' / 'US-0005_one-picture.json'))
        check('save-map: a single picture is saved as before, never flagged', row5['page'] is None and row5['page_pick']['map_page_found'] is None)

        # ---- 4. the tracer's prep leaves out a 'no map page found' row, with the reason
        base = pathlib.Path(td) / 'base'
        (base / 'maps').mkdir(parents=True)
        pins = {}
        for f in sorted((ROOT / 'data/parkinfo').glob('US-*.json'))[:3]:
            for ref_, a in (json.load(open(f)).get('parks') or {}).items():
                if len(pins) < 2: pins[ref_] = a
        r1, r2 = list(pins)[:2]
        for r_ in (r1, r2):
            shutil.copy(pic / 'maps' / 'US-0001_example-park.jpg', base / 'maps' / f'{r_}_x.jpg')
        rows = [dict(json.load(open(pic / 'rows' / 'US-0001_example-park.json')), ref=r1, files=[f'maps/{r1}_x.jpg']),
                dict(row4, ref=r2, files=[f'maps/{r2}_x.jpg'])]
        json.dump({'maps': rows}, open(base / 'index.json', 'w'))
        out = subprocess.run([sys.executable, '-B', str(S / 'kpc_picture_prep.py'), str(base), str(pathlib.Path(td) / 'nolinks')],
                             cwd=str(ROOT), capture_output=True, text=True, timeout=300)
        idx = json.load(open(base / 'index.json'))
        nm = json.load(open(base / 'not-maps.json'))
        check(f'prep: the park with a map page is traced, the one with none is not, and says why ({out.stdout.strip()[-120:]})',
              r1 in idx and r2 not in idx and r2 in nm and 'no map page found' in nm[r2])
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
