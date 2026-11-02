# kpc_site_check (T5): test report

Run on 2026-10-31 (America/Chicago) on the shared Linux box with Python 3.12, playwright 1.55.0 and Google Chrome
(`--chrome /usr/bin/google-chrome`; Playwright's own Chromium is not installed on this box). Every number below
comes from those runs.

## Self test (offline)
`python kpc_site_check.py --selftest` prints **PASS** (14 ok lines, 0 FAIL). It serves `tests/fixture_site/`, a
local page with a small fake Leaflet, and checks 3 K4TEST parks on the phone and the desktop:
- K4TEST-1: official, with the 2-fer line. Every check passes.
- K4TEST-2: the key says official but the page says "Approximate outline". It is flagged as a wrong label.
- K4TEST-3: pin only, a card wider than the phone, and a console error. It is flagged for the fit and the
  console error. The pin dot and the trail-pane shape are not counted as an outline.

It also checks the label wording, including that "Pin only (no official outline yet)" is read as pin and not as
official, that summary.md puts failures first, and that screenshots are 1600 px or less.

## Acceptance 1: live site, `tests/sample_live44.json` × 2 devices
The sample was built from the keys with seed 7:
- 10 official, 10 approximate and 10 pin parks, plus 10 parks that have a live 2-fer spot. They come from the
  US-KS, US-MO and US-TN keys and the KS/MO/TN 2-fer files, with "dropped" spots left out.
- 2 Canada parks from CA-ON (1 official, 1 approximate).
- 2 world parks from FI (1 with an EEA match = official, 1 with no match = pin).

That makes 44 parks and 88 checks. US parks go to the US planner (the spec's 5 steps); Canada and world parks go
to the Kit, because the US planner only knows US refs.

**Run time: 88 checks in 10.7 min (target under 30 min for 40 × 2): met.** Exit 0. Output is in `runs/t5_live/`:
88 JPEG screenshots, 15 MB in total, the largest 1600 px. The run ended at 20:21 CDT.

What a guest saw:
| check | result |
|---|---|
| label matches the key | 86 of 88. The 2 misses are both US-8313 Mountains-to-Sea Trail. My sample took it from the **US-TN key (g "pin", joined_in US-NC)**, but the **US-NC key says "official"**, and the planner shows "Official outline … (5 pieces)". The two state keys disagree. |
| outline drawn when the key says official/approximate | all of them, 0 misses |
| 2-fer line word for word | 20 of 20 2-fer checks. In every case it is the static line in the page's notice box, **not in the park's card** (`fers_line_where: page`). |
| information notice on the page | 88 of 88 |
| card fits the phone | 27 of 44 phone checks. **17 don't fit**, all on the US planner: the popup sticks out to the right (8), to the left (6) or off the top (3), e.g. card box x = −66 to 251 on a 390 px screen. Kit checks all fit. |
| console errors | **all 88 checks** have at least one. On the planner the main one is `KPC-Data/locations.json` 404 (80×). Others: `data/sota/t/<lat>_<lon>.json` 404, `data/unofficial.json` 404, `data/us-key/US-KY.json` and `data/access/US-KY.json` 404, and api.weather.gov 400 for a point in Finland. |
| button does nothing | **80 of 80 US planner checks.** See below. |

**A real bug found on the planner:** after "click the first suggestion" the park's card is already open. The next
step, clicking the park's row (`a.ref`), re-draws the open card, and its buttons lose their click handlers. So
**SHOW THIS PARK'S OUTLINE does nothing**: I saw `onclick` go from set to null about 0.5 s after the row click. A
visitor following the same steps would hit the same dead button. The robot reports it as "a button did nothing when
clicked". It then follows the recipe's `if_dead` steps: close the card, click the row again, click the button.
That works, so the other checks can still run. All of this is data in `tests/recipes.json`.

## Acceptance 2: a wrong label on purpose (local copy)
I made a local copy of the live `KPC-Data/data/us-key/US-MO.json` and edited two parks: US-8308 Pilot Knob CA
official → "approximate", and US-11134 P.F. Barnes CA official → "pin". US-8502 Mussel Fork CA was left as it is,
as a control. The run used `--local-copy runs/t5_localcopy_src` with the sample still saying "official" for all 3
(`runs/t5_wronglabel/`, 0.8 min):
- US-8308: the page showed "Approximate outline": **flagged** on the phone and the desktop.
- US-11134: the page showed "Sorry, no boundary available" / "Pin only": **flagged** (wrong label and no outline)
  on both.
- US-8502 (not edited): the label is official, as expected. **No label flag.**

**4 of 4 edited checks flagged, 0 false label flags: met.** Note: the site's service worker answers data requests
itself, which the local copy can't reach, so `--local-copy` blocks service workers for that run only. Live runs
keep them.

## Known gaps / not tested
- **Kentucky is not in the sample.** There is no `data/us-key/US-KY.json` (the site asks for it and gets 404), so
  KY parks have no key grade to compare. I used KS/MO/TN instead. Chat 10 can add KY parks with an `expect` taken
  from the KY outlines.
- The **park_info and in_park recipes are written but not run live**, and **overlap_finder is members-only**
  (it is not in kpc-gate.js PUBLIC), so a guest sees the sign-in door and the robot reports that. No password is
  used. Only us_planner and kit were run.
- Outline detection counts Leaflet shapes added to the map, because the outline is drawn on a canvas and the SVG
  path count does not change. On the Kit a shape was also drawn for the "pin only" Finnish park (FI-0076). The
  robot does not flag "outline drawn for a pin park", because the spec doesn't ask for it.
- `fits_phone` is measured after scrolling the card into view (a visitor scrolls). A Leaflet popup is measured
  where it sits on the map.
- The 2-fer check passes when the line is anywhere on the page. `fers_line_where` says whether it was in the card.
  Today it never is.
- `.us-grade` in the planner card is read first. When it is empty, the label comes from `#us-status`, then the card.
