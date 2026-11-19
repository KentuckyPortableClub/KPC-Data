# KPC hand-off 07: REVIEW THE WHOLE MAP PIPELINE (layers, store room, keys, matching, 2-fers, helper bots)

From: Kentucky Portable Club (owner Brandon White, KZ4CP), written by the club's reviewer (Fable), 19 Nov 2026, 4:15 PM CST (C2 added 4:35 PM).
For: an outside reviewer. **You read and you report. You change nothing, start nothing, merge nothing.**

How to read the dates in this file: **[19 Nov]** = checked by the reviewer today in the code or data. **[18 Nov]** /
**[17 Nov]** = taken from that day's club notes and NOT re-checked: treat those as claims to test. Where the notes and
the code disagree, the code is right, and the disagreement is a finding we want.

---

## 1. The job

The club draws official park boundaries for every park the three programs number (POTA first), and from them finds
"2-fers": places where two parks' official boundaries overlap. It is run by one owner on a phone, several AI chats, a
set of GitHub bots, outside agents, and the owner's PC. It grew fast: most of what is below was built in four weeks.

The owner's bar, in his words:

- "your responsibility is to make sure we are producing the best maps possible and efficiently and we have very little
  errors and we catch and fix it" (19 Nov)
- "better to be right then wrong" (19 Nov) and "we can not trust old information" (18 Nov)
- "We need not make up rules ... we dont add rules to POTA" (17 Nov): the club matches POTA and is only "a touch
  stricter to account for map errors"
- "anything a bot can do we set it up like that" (31 Oct) and "lets optimize my claude usage ... stop rerun and rerun"
  (27 Oct)

**We want a fresh pair of eyes on the whole chain, end to end:** where can a wrong map still get through, what is
fragile, what is wasted, what should a bot do that a chat does now, and what would you do first. Section 9 says exactly
what to send back.

## 2. Where everything is

| Repo | What | Open to you? |
|---|---|---|
| `KentuckyPortableClub/KPC-Links` | the website, the key builders, the 2-fer bot, the rule files, the notes (`.claude/`) | public |
| `KentuckyPortableClub/KPC-Data` | bot work files, the helper bots, the waiting room; side branches `tools-out`, `intake-files`, `lookup`, `picture-maps` | public |
| `KPC-Store` | the outline store ("store room"), the layer keeper, the PC tools | may be private: if you cannot open it, say so and review its reader side from KPC-Links |

Start here, in this order:

1. KPC-Links `.claude/CLAUDE.md` (the house rules) and `.claude/RULES-NOW.md` (the rules in force, word for word).
2. `.claude/notes/key-quality.md`: the top (the seven rules of the grade, section 0 "what went wrong"), sections 9 to 11,
   then section 19 items 34 to 39 (today). The file is 150 KB: do not read it all.
3. `.claude/notes/matching-plan.md` (how the matcher is meant to work), `.claude/notes/fers-fix-later.md` (2-fers),
   `.claude/notes/layer-refresh.md` (a parked plan), `.claude/inbox/LEDGER.md` (every promise: DONE / OPEN).
4. `docs/key-rules-change.txt` (every rule change, with its hash), `docs/fers-from-store.md` (the store rules).
5. KPC-Data branch `tools-out`: `key-quality/2026-11-18/` and `2026-11-19/` (fact checks, grades, hand-offs 02 to 06),
   `not-sure/` (the list of parks we are not sure of, and why).

## 3. The chain, stage by stage

### A. Layers (where the outlines come from)

- US: `data/state-gis.json` lists every state layer and says what each is: owned land / designation line / water /
  register / compilation (ruling D11; it is a rule file, under the US rules hash). PAD-US is read as one national layer.
  World: `data/world-key/layers.json`; EU compilations are used as "approximate"; WDPA shapes never go public (licence).
- The **layer keeper** (KPC-Store) checks every layer for change and asks for what is missing or short
  (`layer-requests.json`, KPC-Data `data/keeper-asks/latest.json`). About 589 layers. The two monthly "download
  everything" jobs are switched off (plan parked in `layer-refresh.md`, grey areas R-LR1 to R-LR4).
- Research order the owner set: the state's open-data portal first, the agency's own park page second, a web search
  last. Bots are polite by one module (`kpc_manners`: robots.txt, pace, refusals). Rule sheet R-NET1 (who the bots may
  ask) is written; its code is not built **[19 Nov]**.

Known issues:
- **Missing and short layers.** Some parks' true boundary is in no layer we hold (Tillamook State Forest, Tallgrass
  Prairie, Timucuan, Craters of the Moon's BLM land, Longview Saline). Three layers look cut off at 200 rows (CO
  `sgcoa`, OR / WA `sgorf`) **[19 Nov notes]**.
- **No completeness gate.** The owner, 19 Nov: "We should also only build keys if we have most of our layers so we dont
  rebuild over and over". A key build today does not know whether its state's layers are all present. Not built.
- **Hand downloads have no working path yet.** Layers no bot may read (blocked host, sign-in, download-only) are meant
  to go to the owner's PC (`tools/kpc_pc_helper.py`, `data/needs-download.json`). Not set up **[19 Nov notes]**.

### B. The store room (the outline store)

- One store of park outlines at about 2 m detail, built on the owner's PC by numbered steps (`.bat` files, for example
  `6-CONFIRM-TERMS`, `7-MERGE-VERIFIED-ROWS`, `8-FETCH-OWNED-LAND`). A **private** store holds everything; a **public
  shelf** (`tools/kpc_store_public.py`) holds only parks whose every record passes the licence gate, and is published
  as a KPC-Data release.
- Coverage **[17 Nov]**: 13,118 of 15,403 parks on the shelf, 85.2%. 23 of 66 areas were under 90% (US-HI 9.5%, US-VT
  11.9%, US-MN 19.1% ... US-AK 89.2%). Why parks are off: 1,699 records whose terms a tool read but no person
  confirmed, 896 records with no credit line, 81 share-alike (rightly refused), 649 parks with no public view. 40
  layers hold it back; the 12 biggest are worth about 1,406 parks. The list went to the owner
  (`SHELF-LAYERS-TO-CONFIRM.csv`).

Known issues:
- **The backlog is licence confirmation by one person on one PC**, not a fault in the shelf.
- **The PC push check refused good work [17 Nov, status unknown].** `keeper/fers_push_check.py` refused 24 finished
  areas of the 16 Nov run (72 problems): every area's withheld list sits in one shared folder and every file is checked
  against all of them, so a border pair named by a neighbouring area is refused. 14 processes were also killed by the
  memory guard. It was diagnosed, with the fix described, and not fixed. It is the one guard between a private outline
  and a public repo, so it needs tests, not a patch. Until it is fixed the PC's 2-fer results cannot be published.
- The public 2-fer bot has never been switched onto the shelf (parked by the owner until the keys are good).

### C. Keys and matching (which official record is which park)

- The **key** of an area says, for each park number, which official records are its land: `data/us-key/US-XX.json`,
  `parks[ref] = {n, m: [[record id, name, acres, how]], c: [check rows], g: official / approximate / pin}`. Builders:
  `.github/scripts/kpc_us_key.py`, `kpc_key_rules.py`, `kpc_match.py`, `kpc_key_facts.py`; Canada, world and Kentucky
  have their own.
- A join needs pin + name + similar size; no sure match = pin only. Rules D1 to D11 (17 Nov), "the contest" (a record
  goes to the park it fits best), and the 19 Nov rules: Q1 (a "closest land" answer becomes a pin), R-PP1 / 1a / 1b (park
  and preserve), R-FJ1 (a person's evidence may join a named record far from the pin: "pins are only references").
- Each rule sits behind a switch, per state, in `.github/key-switches.json`. Every rule change moves a **rules hash**,
  declares its **scope**, gets a changelog line, goes on a branch as a draft pull request and is merged only after the
  reviewer has read it (`key-quality.md` section 13).
- **Saved answers** (`overrides`): a person's or an agent's yes / no for a park, now only with evidence (who, source,
  what was seen, date).
- **The drop guard**: a state that would lose even one official outline is held, red, and nothing is saved until the
  lost parks are named in `.github/key-drop-approved.json`. Standing rule since 19 Nov 1:56 PM: a state is released
  when every lost or shrinking park passes a two-agent size check and the reviewer judges the error rate low.
- **How a key is checked**: `kpc_key_factcheck.py` (witnesses per park: pin, name, agency, second layer, designation,
  size, code; a class: verified / two / one / none / flagged / pin; all US in 5 minutes) and `kpc_key_grade.py`
  (seeded samples, blind line-ups with planted known answers, two graders, a gold set with a SEALED half). A review
  packet bot (KPC-Data #124, #125) writes old-against-new per state.

Numbers:
- US key **[18 Nov]**: 13,118 parks; 11,715 with an outline; verified by facts 8,304 (70%; 87% by activations); flagged
  549 (4%). Join rows by method: **name 120,575**, a person's answer 12,904, words 4,430, the rest under 1,600. 1,257
  parks rest on one name-only record; 506 records are joined to two or more parks.
- **Official size on file for about 4% of parks** (488 witnesses; 634 usable sizes) **[18 Nov]**.
- Saved answers **[18 Nov]**: 5,038 parks have one; 3,307 carry the same bulk-import reason. The owner: "My hand check
  answers were not mine and not trustworthy." 610 parks' outlines rest on a saved answer alone.
- 19 Nov: 13 states were held; Idaho and Oregon were saved at 11:16 AM; the other 11 (AK AR DE FL GA MT NC RI UT VA WY)
  were let through by one run started 2:54 PM, 50 parks named, every one by a planned rule. The key was saved to main
  at 3:52 PM (`6e110a6`). Read at 4 PM: no state held, the 50 named parks are exactly the 50 that lost an outline; the
  run still ended red on the outline master check (408 problems; 412 on the runs before it). **That is the KEY on main.
  It is not the map people see: read C2.**

Known issues:
- **The name rule makes almost the whole key and has never been graded on a random sample.** The bar the owner set on
  18 Nov (wrong land under 1% of outlines, none wrong in the 25 busiest parks of each state) is NOT proven: every
  CHANGE of the release was checked, the unchanged outlines were not. The random sample ("kit D") is still to run.
- **Size cannot be checked at scale** (4%). Both Montana faults of 19 Nov were outlines that had quietly shrunk.
- **Old saved answers.** Many are a bulk import; ids renumber when a layer is refreshed (288 of 3,677 saved ids sat on
  a different name on 18 Nov; the engine re-finds by name + acres). Classing them by evidence is planned, not done.
- **Name traps found by grading [18 Nov, check whether fixed]:** the matcher drops a last word ("Cheatham WMA" and
  "Cheatham Lake WMA" became one name); a bare name takes no kind from its layer (Gold Butte, Red Cliffs, Mount
  Irish); small name slips cost pieces (a wrong initial, "Park (Unit Area)" records).
- **A rule change rebuilds all 50 states** (3 jobs of about 69 minutes), because any edit moves the code hash, although
  per-area hashes exist. Two daily starts made red runs, and emails, all the while states were held on purpose.
- **Canada, Kentucky and the world are not graded.** The tools need loaders for them. World **[17 Nov]**: 45,933 of
  60,512 rows carry no grade label at all; Japan 185 of 1,241 parks joined, Slovenia 144 of 1,181, Hungary 23 of 246
  (missing sources more than bad matching).
- **The 18 Nov grade went wrong in ways worth knowing** (`key-quality.md` section 0): it was circular (rules graded
  against the answers the key obeys), a grader judged the raw file and not the built key, a false finding was told to
  the owner and corrected the same day, a number went out without its range.

### C2. From the saved key to the map people see (found 19 Nov, 4:30 PM)

- The public pages never read a working file. They read `data/released/` only, through `data/released/RELEASED.json`
  ("written only by kpc_release.py, the by-hand Release workflow"). A US park is drawn from the released copy of
  `data/outlines/US-XX.geojson.gz` (one outline per park), with the released copy of its key.
- The Release (`.github/workflows/kpc-release.yml`): by hand only, only the owner's login may start it, one area at a
  time, from a commit on main, and only for an area that is green, "no worse than live", and has a RELEASE-READY: YES
  in a Quality verdicts file (`data/status/quality/verdicts.json`, which is not on main today).
- **State [19 Nov, checked]: the last US Release was 11 Nov 22:10 UTC; Canada and Kentucky 12 Nov. Nothing since.** The
  working outline files (`data/outlines/US-XX`) were also last written on 11 Nov: since store mode (15 Nov) the key run
  skips its outline step. So every key change of 12 to 19 Nov is in the working key only.
- What that looks like: Seven Sisters (US-12918) is on the public map with the 1,554-acre wildlife area records; today's
  key gives it the 8-acre fishing access site. Flathead and Custer Gallatin are on the map with the state's copy;
  today's key has the Forest Service records. Laurel (US-12938) is approximate, 1,093 acres, on the map; official,
  1,378 acres, in the key. Montana: 50 of 254 parks differ between the map and today's key; Delaware: 29 of 89.

Known issues:
- **"Released" has meant two things.** All day on 19 Nov the notes said a state was "released" when the drop guard let
  its key be saved. The reviewer wrote "all 11 released" and "wrong land on today's map: 9 to 0" without checking what
  the map reads. The map did not change.
- **Two steps have no owner and no trigger**: writing outline files that agree with the saved key (in store mode), and
  the by-hand Release with its verdict file. The chat that used to write the verdicts ("Quality") is retired.
- A Release today would pair today's key with 11 Nov outlines. The red master check may be counting exactly that.

### D. 2-fers

- `.github/scripts/kpc_fers.py` (5,197 lines) and helpers. Three passes on finer grids (20 / 10 / 5 m); a 2-fer needs a
  spot 25 yards across (25 to 50 = "very tight", members only; 50 to 100 = "small"); trails and rivers by POTA's 100 ft.
  It never writes that a pair is NOT a 2-fer. Runs: GitHub workflows in KPC-Data, or the owner's PC
  (`tools/pc-runner/`) on the private store. Each area's run leaves a receipt (proof of work).
- Privacy fails closed: a withheld outline is never named in a public file; a write guard, a final redaction and the
  push check all stand in the way.
- **State [19 Nov]:** all 2-fer runs and schedules are parked until the keys are good. Every 2-fer row on file was
  made by the old system on old keys (the public files date from 9 Nov **[17 Nov]**). On 17 Nov 2,769 rows were shown,
  276 of them on parks whose only land is a designation line.
- The owner answered the seven open 2-fer questions today (rules R-2F0 to R-2F7, `tools-out`
  `key-quality/2026-11-19/handoff-06/RULE-SHEET.md`). **None of it is in the code yet**: hand-off 06 is with the
  outside agent.

Known issues:
- **One very large file**, rules kept as dated comments beside the code, a separate Kentucky path, behaviour set by
  environment variables that each runner must pass (D10 was silently off on the PC until 17 Nov).
- **A built switch that would have misfired [19 Nov]:** the "never past a key rebuild" age check compares a row with
  the id of the last key RUN, which changes on every run, so it would have thrown away every copied row twice a day.
- **A note that lied for two days [19 Nov]:** `fers-fix-later.md` said "nothing below is built" while most of it had
  been merged three hours after it was written (#269). The ledger said DONE; the note said shelved.
- Near a size line the 5 m grid cannot tell the side: a true 16 to 22 m overlap can read 23 to 27 m **[19 Nov,
  measured]**.

### E. The helper bots (KPC-Data)

| Bot | What it does | State |
|---|---|---|
| link harvester | finds an official page or map when POTA gives none | in place **[19 Nov notes]** |
| truth bot (size checker) | reads a park's official size from its page (`data/truth`) | in place; few usable sizes, some bad page reads (Washington Crossing "14 acres") |
| docs bot | official map and rules links (`data/docs`) | in place; check whether its queue is running or paused |
| tripwires T1 to T5 | warning checks on every join (shared record, cut-off land, pin off its land) | merged, report only; its list is not on main yet **[19 Nov]** |
| review packet bot | old key against new, per state: who shrinks, who gains, who lost an outline | merged; within 1 to 2% of the records' own acres |
| PDF finder, tracer | finds picture maps; traces nothing yet | built, off by default |
| park page reader | reads POTA's own link for a park: name, "& Preserve", "inside of", sizes, tracts, each with its quote | hand-off 05: four draft pull requests (KPC-Data #126, #127, #129, #130); review says NOT YET, three small changes |
| the NOT-SURE list | one shared list: park + doubt + why + what would settle it; every bot writes, every bot reads | 104 seed rows on `tools-out`; the module is in #127; no other bot writes to it yet |
| waiting room | where bot output waits for a yes | 497 files on 17 Nov, some since 31 Oct; the numbered chats that approved them are retired **[17 Nov, status unknown]** |

What the day of 19 Nov showed: every hard case (the six "National Park & Preserve" parks, Red Cliffs, Laurel,
Flathead, Custer Gallatin) was settled by reading the park's OWN page and the agency's own acre table. The owner:
"our bots and them gathering information for the ones our program dont solve from the beginning we have way less
issues". The page reader and the not-sure list are the answer to that. Neither has run on real pages yet, and the
reader's "0 wrong" rests on 26 facts.

### F. Who does what

- Fable: rules, reviews of rule changes, grading design, hand-offs. Opus: builds, merges, runs. Sonnet: blind graders.
  Outside agents: builds from hand-offs, and research kits in two blind passes with planted answers (a row counts only
  where both passes agree). The owner's PC: the store, 2-fer runs, hand downloads. The owner decides grey areas.
- Memory between chats is the notes: `CLAUDE.md`, one topic file per area, one ledger line per promise.

## 4. What works well (do not break it)

1. **Guards that fail closed**: the drop guard (limit 0), the privacy write guard, the rules hash + scope + changelog, a
   missing rulings file stops the bot, proof-of-work receipts instead of exit codes.
2. **Evidence over opinion**: saved answers need who / source / saw / date; rule changes show "only these parks change"
   on a test build before merge; the reviewer reads every rule change.
3. **Blind two-pass kits with planted answers**: both graders passed the plants and never split YES against NO.
4. **The fact check**: all US in 5 minutes, and its classes sort the risk the right way (verified parks: 0 wrong land
   in the pilot).
5. **Reading the park's own page first** settles what name matching cannot.
6. **Rules first**: a rule sheet in the owner's words before anything that decides for people is built.

## 5. What does not work well, worst first (the reviewer's own ranking: argue with it)

1. **The map people see is eight days behind the key, and nobody was watching the gap** (C2). A week of fixes, the
   known wrong outlines included, is not on the public map, and the word "released" hid it.
2. No real error rate exists for the key: the name rule is ungraded on a random sample, and size is known for 4%.
3. Layers: missing, short and blocked ones, with no gate that says "this state is ready to build".
4. Status lives in hand-written notes that go stale within hours; chats then plan on a stale note. The notes are huge
   (`mapping.md` 446 KB, `key-quality.md` 150 KB, `new-chat-starters.md` 128 KB) and cost usage every time one is opened.
5. Work is passed between many chats and agents; each pass re-derives context. A promise can be DONE in the ledger and
   "not built" in the note.
6. The 2-fer side: all data old, one huge file, rules as switches each runner must remember, runs parked.
7. The store: licence backlog on one PC; the push check blocks finished work; memory kills.
8. Rebuild cost: 50 states for any rule edit; red-by-design scheduled runs that send email.
9. Repo size **[17 Nov]**: KPC-Data 1.4 GB on GitHub (its line is 400 MB), KPC-Links about 800 MB (line 650). Bots
   save every few minutes (about 137 commits a day) and rewrite big files; the waiting room alone wrote 161 MB in 119
   commits; 26,117 small files; 2.2 GB of workflow artifacts; 38 and 72 branches. A seven-step fix list was written on
   17 Nov; we do not know how much was done.
10. Canada, Kentucky and the world are outside every grade.
11. The waiting room has no owner since the numbered chats were retired.

## 6. Usage and cost

- **The owner's time** is the scarcest thing. He works from a phone. Rule: reports short, ask him only what the chats
  and agents cannot settle, by park number.
- **AI usage**: never wait on a bot (start it, end the turn, read it next session); one run per change; read by grep,
  not whole files; one reviewer sitting per block of work, not per item; legwork to outside agents and the PC.
- **GitHub**: a failed run emails him. Runs are started as rarely as possible; probe runs must never fail.
- **Storage**: new tools write to side branches of KPC-Data, never to main; nothing over 1 MB on main without asking;
  picture maps small and on their own branch.

## 7. The reviewer's thoughts for improvement (test these, do not take them as given)

1. **Measure before more rules.** Run the random sample (kit D) now and after every release: a fixed small sample per
   state, two blind passes, the SEALED gold half growing. Report four numbers with ranges: wrong land, too big, missing
   pieces, coverage.
2. **A size witness from the agencies' own tables** (NPS, FWS, Forest Service, state systems), refreshed yearly by a
   bot. It lifts the 4% and catches the quiet shrinks.
3. **Evidence first, by bots**: page reader + size witness + not-sure list for every park the rules leave unsure;
   only what no bot settles goes to a person or an agent. Finish it, then measure it blind before any rule reads it.
4. **A readiness board per state, made by a bot, not by hand**: layers present / short / blocked, key build and rules
   hash, held or released, fact-check classes, not-sure rows, shelf coverage, the date of its 2-fer file. One page a
   chat reads in place of 150 KB of notes. Build a state only when its row says ready.
5. **Cheaper proof of a rule change**: a "who changes" run from the saved shapes for the states in the change's scope
   before any full build, and a full build only on release.
6. **Rules as data**: switch files and rule tables the code reads (the keys have this; hand-off 06 gives it to
   2-fers), every run's receipt recording the settings it ran with.
7. **Shrink the notes**: a short "state of the maps" page per area and an archive; status lines generated from the
   repo where they can be.
8. **Fix the push check with tests**, then one fresh private-store 2-fer run per area on the new keys, graded on a
   sample before anything is public.
9. **Repo size**: finish the 17 Nov list (write only on change, gzip, status files daily, side branches, delete merged
   branches and artifacts), then restart history once.
10. **Name an owner** for the waiting room and for each bot family, and take the retired chat numbers out of the rules.

## 8. Questions we most want answered

1. Reading the key builder cold: where can a park still get ANOTHER park's land, or lose its own, with every guard
   green? Give park numbers.
2. Is the drop guard's "limit 0, name every park" the right guard, or does it only catch losses and not wrong gains
   and quiet shrinks?
3. Which of the name traps of section C are still in `kpc_us_key.py` / `kpc_key_rules.py` today?
4. Is the fact check's "verified" strong enough to be the release bar? What would fool it?
5. Is the saved-answer path (join / no, fingerprint by name + acres, evidence fields) safe against a layer refresh?
6. The store: is the licence gate right, and what is the smallest fix that makes the push check correct and tested?
7. The 2-fer bot: with R-2F0 to R-2F7 applied, what can still show a 2-fer that is not one? What would you split out
   of the 5,197-line file first?
8. The helper bots: which overlap, which are dead weight, which outputs does nothing read?
9. Where do the notes and the code disagree today? List every case you find.
10. Where is usage wasted: Actions minutes, repeat rebuilds, commits, files a chat must read to start work?
11. What should be a bot that is a chat's job now, and what is a bot's job now that needs a person?
12. If you had two weeks: your order of work, and what you would stop doing.
13. From a saved key to the public map: list every step and guard and who may run each. What would let a key reach
    the map without its outlines, or outlines without their key? How should the club see, every day, how far the
    public map is behind the key?

## 9. What to send back

One report (markdown), findings ranked by risk to map accuracy first, then cost. For each finding: what you saw (file
and line, or park number and area), how you checked it, how sure you are, the smallest fix, how to test the fix, and
the effort (small / medium / large). Then: five things that are well built and must not be broken; every place the
notes and the code disagree; your order of work.

Rules for the review:

- Check in the code and the data, not in the notes. A number you did not re-measure is quoted with its date.
- Honest numbers, with their range and how they were made. "I could not check this" is a good line.
- Read-only. No pull request, no branch, no workflow started, no comment on an issue, no request to any agency site.
- Never name a park the store withholds, and never copy anything out of a private folder.
- No new rules for POTA and no new numbers: say where one seems to be needed and leave it as a question for the owner.
- Do not ask the owner for a key, a token or a password.
