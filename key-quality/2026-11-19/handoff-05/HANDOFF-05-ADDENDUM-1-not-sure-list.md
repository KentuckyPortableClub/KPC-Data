# Hand-off 05, ADDENDUM 1: the shared NOT-SURE LIST (19 Nov 2026, 3:15 PM CST)

Goes with `README-START-HERE.md`. It changes nothing in part 1. It adds one small module to part 2.

The owner, 3:07 PM: "the system should do the work before and leaves us less head scratching ... all these bots should
be wired together to share the load and help to solve mysteries ... we should also keep a list of parks we're not 100%
sold on and why".

## The idea in three lines

One list. Every bot writes a row when it is not sure about a park, with the reason in plain words. Every bot reads the
rows it can help with and adds what it found. A row closes only when evidence settles it, with who and how. What no
bot can settle is what a person or an outside agent gets, and nothing else.

That list is also the answer to "who makes the reader's list": the reader works the open rows that want page facts.
The list drops of section 9 stay as written (any tool may still hand over a plain list).

## What you build (part 2): `.github/scripts/kpc_not_sure.py`

A small shared module with a command line. Standard library only, no network, pure file work, so every club bot can
import it.

- **Where the list lives:** KPC-Data branch `tools-out`, folder `not-sure/`: `<area>.json` (one file per area, rows
  sorted by park number then code, so two bots writing the same facts make the same file), `summary.md`, `README.md`.
  The seed the club made today is there now (`not-sure-parks.json` / `.csv`, 104 rows): split it by area on first run.
- **One row = one park + one doubt:**
  `{ref, area, name, code, how_sure, shows_now, why, wants: [...], found_by, first_seen, last_seen,
    evidence: {source, saw, date}, tried: [{by, date, result, quote}], status, settled: {by, date, how, link}}`
  - `how_sure`: `wrong likely` / `unsure` / `incomplete` / `unchecked` / `fairly sure`
  - `status`: `open` / `parked` (waits on a rule or the owner) / `settled` / `gone` (the doubt no longer shows up)
  - `wants`: what would settle it, from a short fixed list: `page facts`, `official size`, `map`, `official layer`,
    `far-join evidence`, `a person`, `the owner`, `random sample`
  - class rows (a doubt about a whole group, `ref` = `(class)`) are allowed and are never worked by a bot.
- **Functions (and the same as commands):** `add(row)` (same park + code again = `last_seen` moves, nothing doubles),
  `tried(ref, code, by, result, quote)`, `settle(ref, code, by, how, link)`, `open_rows(area=None, wants=None)`,
  `summary()`. Nothing is ever deleted: a settled row keeps its whole story.
- **Who may settle:** a person, the reviewer, or a bot whose rule sheet says it may. The page reader may NOT settle
  (law 1). It adds `tried` notes with the quote it saw. Its own rows turn `gone` when its question no longer comes up.
- **Codes:** keep the ones in the seed and the reader's question codes of section 8; a new code needs one line in
  `not-sure/README.md` saying in plain words what it means. No free-text codes.

## How the reader uses it

1. Worklist order gets a new first step: open rows whose `wants` holds `page facts`, `official size` or `map`,
   `wrong likely` before `unsure`, busiest park first.
2. After reading a park: `tried(...)` on each of that park's open rows, with what the page said (the quote) or "page
   silent" / "refused" / "script-built".
3. Each question the reader asks (section 8) becomes a row via `add`, `found_by: "park page reader"`.
4. `summary.md` (one phone screen): open rows by `how_sure`, the 15 busiest `wrong likely` parks with their plain
   reason, how many rows were closed since last time and by whom, how many no bot could help with.

## Tests

Add to `tests/test_park_pages_nov19.py` or its own file: add twice = one row; tried / settle keep history; two writers
in either order give byte-identical files; a row with an unknown code or `wants` word is refused; a class row is never
handed to a bot; the seed loads whole (104 rows) and splits by area with none lost.

## Not yours

Wiring the club's other bots to write rows (the key run, the fact check, the size checker, the drop guard, the layer
keeper, the owner's PC tools). The club does that once your module is merged. Put the row shape and two examples in
`docs/park-pages.md` so they can.
