#!/bin/sh
# Double-click or run this. It asks one question and writes a zip next to itself.
cd "$(dirname "$0")" || exit 1
LOG=run-log.txt
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.10 or newer was not found." | tee -a "$LOG"
  echo "The details are in run-log.txt."
  exit 0
fi
printf 'Which state? (blank = continue the list) '
IFS= read -r STATE
if [ -f scripts/kpc_park_pages.py ]; then
  PY=scripts/kpc_park_pages.py
  DATA=data
else
  PY=../../.github/scripts/kpc_park_pages.py
  DATA=../../data
fi
mkdir -p out
python3 "$PY" --pc read --data "$DATA" --out out --state out/state.json --areas "$STATE" --max-minutes 50 >>"$LOG" 2>&1
DAY=$(date +%Y-%m-%d)
rm -f "park-pages-$DAY.zip"
python3 - "$DAY" <<'PY'
import sys, zipfile
from pathlib import Path
day = sys.argv[1]
root = Path('out')
with zipfile.ZipFile(f'park-pages-{day}.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for f in root.rglob('*'):
        if f.is_file():
            z.write(f, f.as_posix())
PY
echo "Done. Send the file park-pages-$DAY.zip to the chat."
