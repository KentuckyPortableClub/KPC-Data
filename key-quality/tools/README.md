# Chat-side helpers for the key fact check (saved 19 Nov so a fresh chat has them)
- `fccompare.py OLD_FC NEW_FC OUT_PREFIX`: two fact-check folders -> one line per state + a CSV of every park that changed.
- `hardnosize.py OLD NEW`: hard flags other than size, and the states where they rise.
- `build.py REPO OUT STATES... [--jobs N] [--set K=V]`: offline key build of some states (no shapely in the chat box: sizes
  are rows added up, so size flags mean nothing there). Use it only for the states a PR touches.
