"""ONE board file (PART 5): engine/board.md, per kind and per area: missing yesterday -> found today -> still missing, top
why-not tags, blocked hosts, pass 1 vs pass 2 solves. Chat 10 posts the one-line summary at the top."""
import collections, datetime as dt, json, pathlib


def write(out_dir, gaps, prev_gaps, results_by_kind, pass_stats, blocked_rows, extra=None):
    out_dir = pathlib.Path(out_dir)
    L = [f'# Engine board, {dt.date.today().isoformat()}', '']
    tot_found = sum(1 for rs in results_by_kind.values() for r in rs if r.get('status') in ('found', 'candidate'))
    tot_miss = sum(len(v) for v in gaps.values())
    L.append(f'**One line:** {tot_found} new candidates across {len(results_by_kind)} kinds; {tot_miss} parks with a gap; '
             f'{len({b["domain"] for b in blocked_rows})} hosts blocked.')
    L += ['', '| kind | area | missing yesterday | missing today | found / candidate today | still missing | top why-not |', '|---|---|---|---|---|---|---|']
    for kind, rs in results_by_kind.items():
        by_area = collections.defaultdict(list)
        for r in rs: by_area[r.get('area')].append(r)
        for area in sorted(set(list(by_area) + [a for a in gaps])):
            today = sum(1 for x in (gaps.get(area) or {}).values() if kind in x.get('kinds', []) or (kind == 'docs' and {'map', 'page'} & set(x.get('kinds', []))))
            yest = sum(1 for x in (prev_gaps.get(area) or {}).values() if kind in x.get('kinds', [])) if prev_gaps else '-'
            got = sum(1 for r in by_area[area] if r.get('status') in ('found', 'candidate'))
            tags = collections.Counter((r.get('whynot') or {}).get('tag') or r.get('status') for r in by_area[area] if r.get('status') not in ('found', 'candidate'))
            if not today and not got and not by_area[area]: continue
            L.append(f"| {kind} | {area} | {yest} | {today} | {got} | {max(0, today - got)} | {', '.join(f'{t} {n}' for t, n in tags.most_common(3))} |")
    L += ['', '## Pass 1 vs pass 2', '', '| kind | pass 1 | pass 2 | solved in pass 2 |', '|---|---|---|---|']
    for k, s in pass_stats.items():
        L.append(f"| {k} | {json.dumps(s.get('pass1'))} | {json.dumps(s.get('pass2'))} | {s.get('pass2_solved', '-')} |")
    L += ['', '## Blocked hosts (blocked is not "not found"; retried next night)', '']
    hosts = collections.Counter((b['domain'], b['reason'][:80]) for b in blocked_rows)
    for (h, why), n in hosts.most_common(40): L.append(f'- {h}: {why} ({n})')
    if extra: L += ['', extra]
    (out_dir / 'board.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
