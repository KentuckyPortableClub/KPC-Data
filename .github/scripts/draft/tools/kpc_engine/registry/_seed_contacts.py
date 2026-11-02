"""Builds registry/AGENCY_CONTACT_PAGES.md: for each area, the agency's own open-data / GIS portal as written in the club's
agency atlas (tips/agency-atlas/<area>.md, '## Open-data portal'). The portal is where the agency publishes its own
contact link. No people are listed, nothing is guessed, and bots never send email.
Usage: python registry/_seed_contacts.py --pack /path/to/sources/sources"""
import argparse, pathlib, re

ap = argparse.ArgumentParser(); ap.add_argument('--pack', required=True); a = ap.parse_args()
rows = []
for f in sorted(pathlib.Path(a.pack, 'tips', 'agency-atlas').glob('*.md')):
    t = f.read_text(errors='ignore')
    m = re.search(r'^## Open-data portal[^\n]*\n(.*?)(?=^## |\Z)', t, re.M | re.S)
    if not m: continue
    urls = []
    for u in re.findall(r'https?://[^\s)>\]`"\']+', m.group(1)):
        u = u.rstrip('.,;')
        if u not in urls: urls.append(u)
    if urls: rows.append((f.stem, urls[:2]))
out = ['# Where each agency publishes its own GIS / open-data contact', '',
       'Copied from the club agency atlas (`tips/agency-atlas/<area>.md`, section "Open-data portal"). The engine has **no agency',
       'contacts** and lists **no people**. If a layer is wrong or gone, a person opens the portal below and uses the contact link the',
       'agency itself publishes there (if it publishes one). **Bots never send email.** Links were written by the club; the engine did not',
       'guess any. Areas with no portal in the atlas are left out.', '', '| Area | Portal(s) from the atlas |', '|---|---|']
out += [f'| {s} | ' + ' <br> '.join(u) + ' |' for s, u in rows]
pathlib.Path(__file__).with_name('AGENCY_CONTACT_PAGES.md').write_text('\n'.join(out) + '\n')
print(len(rows), 'areas')
