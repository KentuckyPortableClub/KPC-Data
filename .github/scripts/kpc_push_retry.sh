#!/usr/bin/env bash
# PUSH WITH FETCH-AND-RETRY (Nov 9 2026 weekly batch; breakage: the picture tracer's board / tools-out push hit a rebase conflict
# and every later try failed, because the old loops were 'git commit && git pull --rebase && git push': after the first try the
# commit step had nothing to commit, so the chain stopped before the push, and a stopped rebase was left half done).
#
#   kpc_push_retry.sh <branch> <tries> "<generated paths>" ["<board redo command>"]
#
# Run inside the git work tree that holds this run's commit(s). Each try: push; if refused, fetch the newest <branch> and rebase.
# A rebase conflict is settled only where it is safe:
#   - a file under one of <generated paths> (space list, e.g. "picture-trace" or "parcels"): this run's copy wins (the tool's own
#     output folder; the newest run's outputs are the ones to keep);
#   - data/status/bots/<bot>.json (with a board redo command): this run's copy (only this bot writes it);
#   - data/status/board.json: the newest copy is taken and <board redo command> writes this bot's line again on top of it
#     (kpc_status.py merges data/status/bots/*.json, so no other bot's line is lost);
#   - anything else: the rebase is aborted (nothing is half done) and the next try starts from a fresh fetch.
# Loud: a save that never lands prints ::error and exits 1 (the caller decides whether that turns the job red). Never force-pushes.
set -u
b=$1; tries=${2:-5}; gen=" ${3:-} "; redo=${4:-}
is_gen() { local f=$1 p; for p in $gen; do case "$f" in "$p"|"$p"/*) return 0 ;; esac; done; return 1; }
for i in $(seq 1 "$tries"); do
  git push -q origin "HEAD:$b" 2>/dev/null && { echo "saved to $b (try $i)"; exit 0; }
  git fetch -q origin "+refs/heads/$b:refs/remotes/origin/$b" || { sleep $((3 * i)); continue; }
  if ! git rebase -q "origin/$b" >/dev/null 2>&1; then
    n=0
    while [ -d "$(git rev-parse --git-path rebase-merge)" ] || [ -d "$(git rev-parse --git-path rebase-apply)" ]; do
      bad=0; n=$((n + 1)); [ "$n" -gt 50 ] && bad=1
      for f in $(git diff --name-only --diff-filter=U); do
        if is_gen "$f"; then
          # in a rebase, --theirs = the commit being replayed = this run's output
          if git cat-file -e ":3:$f" 2>/dev/null; then git checkout -q --theirs -- "$f" && git add -- "$f"; else git rm -q -- "$f"; fi
        elif [ -n "$redo" ] && case "$f" in data/status/bots/*) true ;; *) false ;; esac; then
          git checkout -q --theirs -- "$f" && git add -- "$f"      # this bot's own line file: this run's copy
        elif [ "$f" = data/status/board.json ] && [ -n "$redo" ]; then
          git checkout -q --ours -- "$f" && (eval "$redo") >/dev/null 2>&1; git add -- data/status
        else bad=1; fi
      done
      [ "$bad" = 0 ] || { echo "::warning title=Save::rebase conflict outside this bot's own files on try $i; aborted, retrying from the newest $b"; git rebase --abort; break; }
      GIT_EDITOR=true git rebase --continue >/dev/null 2>&1 || { git diff --name-only --diff-filter=U | grep -q . || { git rebase --skip >/dev/null 2>&1 || true; }; }
    done
  fi
  sleep $((RANDOM % 8 + 3 * i))
done
echo "::error title=Save::not saved to $b after $tries tries; the next run tries again"
exit 1
