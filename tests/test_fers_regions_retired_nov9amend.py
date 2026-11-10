#!/usr/bin/env python3
"""Nov 9 amendment (Quality regrade v2 must-fix e, 6:00 PM CST): the old side-by-side 2-fer regions workflow saved with if: always()
and no waiting-room divert, so it could write live data/fers. It is retired (copy kept in KPC-Archive retired-workflows/, PR #1);
kpc-fers.yml (region areas, divert first) does that job now."""
import pathlib, sys
R = pathlib.Path(__file__).resolve().parent.parent
gone = not (R / '.github/workflows/kpc-fers-regions.yml').exists()
print(('ok   ' if gone else 'FAIL ') + 'kpc-fers-regions.yml retired (archived in KPC-Archive)')
sys.exit(0 if gone else 1)
