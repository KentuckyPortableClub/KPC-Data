#!/bin/bash
# Oct 28 (HQ 'prune old bundles: keep the last 2 per area'): before an asset is uploaded with --clobber, the copy already on the
# release becomes <name>.prev.<ext> and the older .prev is deleted, so every area keeps exactly its last two.  Never fails.
# usage: kpc_keep2.sh <owner/repo> <release tag> <asset name>
REPO=$1; REL=$2; NAME=$3
J=$(gh api "repos/$REPO/releases/tags/$REL" 2>/dev/null) || exit 0
ext="${NAME#*.}"; base="${NAME%%.*}"; PREV="$base.prev.$ext"
old=$(echo "$J" | python3 -c "import json,sys;a=[x for x in json.load(sys.stdin).get('assets',[]) if x['name']=='$PREV'];print(a[0]['id'] if a else '')")
cur=$(echo "$J" | python3 -c "import json,sys;a=[x for x in json.load(sys.stdin).get('assets',[]) if x['name']=='$NAME'];print(a[0]['id'] if a else '')")
[ -n "$old" ] && gh api -X DELETE "repos/$REPO/releases/assets/$old" >/dev/null 2>&1
[ -n "$cur" ] && gh api -X PATCH "repos/$REPO/releases/assets/$cur" -f name="$PREV" >/dev/null 2>&1
exit 0
