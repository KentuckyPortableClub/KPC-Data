# kpc_site_check (T5): site checker robot

Opens the club's map tools as a guest, on a phone (390×844) and on a desktop (1280×900), for a sample of
parks. `navigator.webdriver` is set to false before the page loads. It reports what a visitor sees:
- an outline is drawn (it counts the Leaflet outline shapes, SVG or canvas)
- the label matches the key (Official / Approximate / Pin only)
- the 2-fer line is there word for word
- the information notice is on the page
- the card fits the phone (not cut off, no sideways scroll)
- any console errors
- a button that does nothing when clicked

The steps for each tool are data in `tests/recipes.json`: us_planner, kit, park_info, in_park and overlap_finder.
Change selectors there, not in the code. It never edits the site.

Install:

```
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
```

Instead of the last step, you can pass `--chrome /usr/bin/google-chrome`.

Example:

```
python kpc_site_check.py --sample sample.json --tools us_planner,kit --out out/ --max-minutes 50 --resume
```

`sample.json` = `[{"ref": "US-0291", "expect": "official", "fers": []}, {"ref": "CA-1571", "expect": "official"}]`.
`tests/sample_live44.json` is the sample used for the acceptance run. US parks go to the US planner; Canada and
world parks go to the Kit (`only_prefixes` / `skip_prefixes` in the recipes).

Test a change before it goes live: `--local-copy DIR` serves `DIR/KPC-Links/...` and `DIR/KPC-Data/...` in place
of the live files. Example: an edited `DIR/KPC-Data/data/us-key/US-KS.json`.

Output:
- `out/site_check.json`: `{ref: [{tool, device, outline_drawn, label, label_ok, fers_line_ok, notice_ok,
  fits_phone, console_errors[], dead_buttons[], screenshot, why, ...}]}`
- `out/summary.md`: one page, failures first
- `out/screens/*.jpg`: 1600 px or less, quality 70
- `summary.json` and `run_log.txt`

Exit codes: 0 done, 3 out of time, 2 bad input. Self test, offline, on a local fixture page:
`python kpc_site_check.py --selftest`.
