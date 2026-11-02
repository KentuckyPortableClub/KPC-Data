"""Build the KPC tools from their sources and the one shared polite web reader (polite.py).

Each source has a line '#@@POLITE@@'; it is replaced by polite.py, so every tool ships as a single file.
  python3 build.py                 rebuild every tool whose folder sits next to _common (../<tool>/<tool>.py)
  python3 build.py --check         rebuild in memory and say whether each shipped file matches (exit 1 if not)
  python3 build.py <src> <dst>     build one file
Edit polite.py or the *_src.py files here, never the built tool files, then rebuild and run each tool's --selftest.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = {'t3_src.py': 'kpc_sitemaps', 't6_src.py': 'kpc_inspire', 't4_src.py': 'kpc_parcels', 't7_src.py': 'kpc_trail_lines'}
MARK = '#@@POLITE@@\n'


def build(src):
    s = open(src, encoding='utf-8').read()
    if s.count(MARK) != 1:
        raise SystemExit(f'{src}: expected exactly one {MARK!r} line')
    return s.replace(MARK, open(os.path.join(HERE, 'polite.py'), encoding='utf-8').read())


def main(argv):
    if len(argv) == 2 and argv[0] != '--check':
        open(argv[1], 'w', encoding='utf-8').write(build(argv[0]))
        return 0
    check, bad = argv[:1] == ['--check'], 0
    for src, tool in TOOLS.items():
        dst = os.path.join(HERE, '..', tool, tool + '.py')
        if not os.path.isdir(os.path.dirname(dst)):
            print(f'{tool}: folder not here, skipped')
            continue
        new = build(os.path.join(HERE, src))
        if check:
            same = os.path.exists(dst) and open(dst, encoding='utf-8').read() == new
            bad += not same
            print(f'{tool}: {"matches" if same else "DIFFERS from"} {src} + polite.py')
        else:
            open(dst, 'w', encoding='utf-8').write(new)
            print(f'{tool}: built from {src} + polite.py')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
