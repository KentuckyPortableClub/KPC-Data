#!/usr/bin/env bash
# THE ONE PLACE that moves the Pages branch 'site' (KPC owner, 2026-11-11). kpc-pages-sync.yml and the watchdog's repair path
# (kpc_watchdog.py) both call it, so they cannot drift; tests/test_site_writers_nov11.py fails if anything else writes 'site'.
#   bash .github/scripts/kpc_site_publish.sh "<why>"
# env: GH_TOKEN, R (owner/repo), FILTER (on = default | off), RUNNER_TEMP, GITHUB_STEP_SUMMARY (both optional)
# FILTER=on : builds the filtered commit (kpc_site_filter.py: only .github/site-allow-list.txt paths, one commit on top of main's
#             commit) and force-pushes it to 'site'. Run inside a checkout of this repo (any depth; blobless is fine).
#             If the filter refuses, NOTHING is published: 'site' stays the last good copy and an error is written (red run).
# FILTER=off: the old way, 'site' = main's newest commit (everything published). The rollback switch: repo variable KPC_SITE_FILTER=off.
# Exit 0 = published or nothing to do; 3 = the filter refused; 1 = could not read main / could not push.
set -u
WHY=${1:-}; FILTER=${FILTER:-on}; T=${RUNNER_TEMP:-/tmp}
say() { echo "$1"; [ -z "${GITHUB_STEP_SUMMARY:-}" ] || echo "- $1" >> "$GITHUB_STEP_SUMMARY"; }
stale() { echo "::error title=Pages copy::$1 (the site would stay stale)"; echo "Pages copy - $1 (the site would stay stale)" | tee -a "$T/kpc-hidden-errors.txt" >> "$T/kpc-hidden.txt"; }
M=$(gh api "repos/$R/git/ref/heads/main" --jq .object.sha 2>/dev/null) || M=""
case "$M" in [0-9a-f]*) ;; *) stale "could not read main"; exit 1 ;; esac
S=$(gh api "repos/$R/git/ref/heads/site" --jq .object.sha 2>/dev/null) || S=none; case "$S" in [0-9a-f]*) ;; *) S=none ;; esac
if [ "$FILTER" = off ]; then
  if [ "$S" = none ]; then o=$(gh api -X POST "repos/$R/git/refs" -f ref=refs/heads/site -f sha="$M" 2>&1); else o=$(gh api -X PATCH "repos/$R/git/refs/heads/site" -f sha="$M" -F force=true 2>&1); fi \
    && { say "Pages copy: site moved ${S:0:8} -> ${M:0:8} ($WHY; filter off: everything published)"; exit 0; } \
    || { stale "could not move site: $(echo $o | head -c 300)"; exit 1; }
fi
F_=""; [ "$(git config --get remote.origin.promisor)" = true ] && F_="--filter=blob:none"   # a blobless checkout stays blobless
git fetch -q --depth 1 $F_ origin "$M" || { stale "could not fetch main ${M:0:8}"; exit 1; }
PREV=""
if [ "$S" != none ] && git fetch -q --depth 1 $F_ origin "+refs/heads/site:refs/remotes/origin/site"; then PREV=origin/site; fi
python3 .github/scripts/kpc_site_filter.py build --repo . --rev "$M" --previous "$PREV" | tee "$T/site-filter.txt"; rc=${PIPESTATUS[0]}
C=$(grep '^COMMIT=' "$T/site-filter.txt" | cut -d= -f2)
if [ "$rc" != 0 ] || [ -z "$C" ]; then stale "the site filter refused (exit $rc, see the log): site left as it was (${S:0:8})"; exit 3; fi
if [ "$C" = "$S" ]; then say "Pages copy: the filtered site of ${M:0:8} is already live: nothing to publish"; exit 0; fi
if git -c user.name='github-actions[bot]' -c user.email='41898282+github-actions[bot]@users.noreply.github.com' push -q --force origin "$C:refs/heads/site"; then
  say "Pages copy: site = filtered copy of main ${M:0:8} ($WHY; $(head -1 "$T/site-filter.txt"))"; exit 0
fi
stale "could not push the filtered site ${C:0:8}"; exit 1
