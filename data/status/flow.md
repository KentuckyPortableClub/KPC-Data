# Flow board (2026-11-03 20:22Z, kpc_flow.py)
Every pile of work, who it waits on and when it last moved. STUCK = work in it and no move for 2+ days. Fix the STUCK ones first.

## STUCK (9)
- STUCK 3 d · **3** · HELD campinfo files (a check failed; data/waiting/today.md says why) · waits on **chat 2 (fix) + chat 11** · US-MA, US-NC, US-NY
- STUCK 3 d · **49** · HELD docs files (a check failed; data/waiting/today.md says why) · waits on **chat 2 (fix) + chat 11** · US-ID, US-IL, US-ME, US-MO, US-IN, US-AK, US-AL, US-AR, US-AZ, US-CA, US-CO, US-CT, US-DC, US-DE, US-FL, US-GA, US-HI, US-KS, US-LA, US-MA, US-MD, US-MI, US-MN, …
- STUCK 2 d · **146** · questions/not-sure-for-chat9.json waiting for an answer · waits on **chat 9**
- STUCK 2 d · **35** · HELD fers files (a check failed; data/waiting/today.md says why) · waits on **chat 2 (fix) + chat 11** · US-AR, US-AZ, US-FL, US-GA, US-IL, US-MA, US-MI, US-NC, US-NE, US-OK, US-PA, US-SD, US-TN, US-TX, CA-BC, CA-ON, US-AK, US-CA, US-CO, US-CT, US-ID, US-MD, US-MN, …
- STUCK 2 d · **3** · HELD trails files (a check failed; data/waiting/today.md says why) · waits on **chat 2 (fix) + chat 11** · US-9905, US-9906, finds-lines-report
- STUCK 2 d · **9** · HELD truth files (a check failed; data/waiting/today.md says why) · waits on **chat 2 (fix) + chat 11** · US-CT, US-MA, US-MD, US-ME, US-MN, US-MS, US-NY, US-OK, US-TX
- STUCK 2 d · **1** · 2-fer checker: found work · waits on **chat 2 + chat 11** · weekly re-test of live 2-fers (last run 2026-11-01; the bot is fine, red was the old status rule) · chat 2 rechecks + chat 11 grades 461 SHRUNK / GONE / MOVED rows (data/fers-check/alerts.md
- STUCK 2 d · **1** · Storage keeper (weekly): found work · waits on **HQ** · STORAGE WARNING: KPC-Data 546 MB (line 400) / KPC-Links 621 MB (line 650) — the bot is fine; over th · HQ (storage step 2, Mon Nov 2 evening at the earliest)
- STUCK 2 d · **1** · T5 site checker: found work · waits on **chat 3** · 60 checks failed on Nov 1; tuned Nov 2 (outline button on an already drawn outline = fine; failed fi · chat 3 fixes the 404s; then the weekly run

## Waiting on each chat (open work, oldest first)
### chat 2
- STUCK 3 · HELD campinfo files (a check failed; data/waiting/today.md says why) · since 2026-10-31
- STUCK 49 · HELD docs files (a check failed; data/waiting/today.md says why) · since 2026-10-31
- STUCK 35 · HELD fers files (a check failed; data/waiting/today.md says why) · since 2026-11-01
- STUCK 3 · HELD trails files (a check failed; data/waiting/today.md says why) · since 2026-11-01
- STUCK 9 · HELD truth files (a check failed; data/waiting/today.md says why) · since 2026-11-01
- STUCK 1 · 2-fer checker: found work · since 2026-11-01
- 1 · HELD world-key files (a check failed; data/waiting/today.md says why) · since 2026-11-03
### chat 3
- STUCK 1 · T5 site checker: found work · since 2026-11-01
### chat 9
- STUCK 146 · questions/not-sure-for-chat9.json waiting for an answer · since 2026-11-01
### chat 10
- 1 · key-doctor: found work · since 2026-11-02
- 1 · Key bots: errors and silence: RED (the bot is broken) · since 2026-11-03
- 1 · Website copy (site branch): RED (the bot is broken) · since 2026-11-03
### chat 11
- STUCK 3 · HELD campinfo files (a check failed; data/waiting/today.md says why) · since 2026-10-31
- STUCK 49 · HELD docs files (a check failed; data/waiting/today.md says why) · since 2026-10-31
- STUCK 35 · HELD fers files (a check failed; data/waiting/today.md says why) · since 2026-11-01
- STUCK 3 · HELD trails files (a check failed; data/waiting/today.md says why) · since 2026-11-01
- STUCK 9 · HELD truth files (a check failed; data/waiting/today.md says why) · since 2026-11-01
- STUCK 1 · 2-fer checker: found work · since 2026-11-01
- 2 · questions/aliases-nov1.json waiting for an answer · since 2026-11-02
- 28 · questions/aliases-nov2.json waiting for an answer · since 2026-11-02
- 1,937 · questions/hardlook.json waiting for an answer · since 2026-11-02
- 45 · questions/nearmiss-nov2.json waiting for an answer · since 2026-11-02
- 20 · questions/gis-hunter.json waiting for an answer · since 2026-11-03
- 470 · questions/layers.json waiting for an answer · since 2026-11-03
- 132 · questions/map-audit.json waiting for an answer · since 2026-11-03
- 115 · questions/parked.json waiting for an answer · since 2026-11-03
- 1 · HELD world-key files (a check failed; data/waiting/today.md says why) · since 2026-11-03
- 114 · files waiting for a grader (data/status/grade-queue.md) · since 2026-11-03
### bots
- STUCK 1 · Storage keeper (weekly): found work · since 2026-11-01
- 1 · Cell coverage (FCC): found work · since 2026-11-02
- 304 · layers in the list the intake bot has not checked yet · since 2026-11-03

## The whole line
| stage | pile | count | waits on | last moved |
|---|---|---|---|---|
| 1 finders | world harvester A leads not in the layer list yet | 0 | intake bot (daily 8:41 UTC) | 2026-11-02 |
| 1 finders | discovery bot map-layer leads not in the layer list yet | 0 | intake bot (daily 8:41 UTC) | 2026-11-02 |
| 1 finders | engine crawler layers (US + Canada) the engine tries at the pins | 516 | park-info engine (every run) | 2026-11-03 |
| 2 outside files | files on branch intake-files no reader has taken yet | 0 | chat 10 (the reader of that kind) | 2026-11-02 |
| 3 layer list | layers in the list the intake bot has not checked yet | 304 | intake bot (daily, 40 a night) | 2026-11-03 |
| 4 engine | engine finds handed to the collector (last hand-back) | 0 | layer collector (every 2 h) | 2026-11-01 |
| 5 collector | outside-research layer x park pairs not pin-tested yet | 0 | layer collector (every 2 h) | 2026-11-01 |
| 6 questions | questions/aliases-nov1.json waiting for an answer | 2 | chat 11 | 2026-11-02 |
| 6 questions | questions/aliases-nov2.json waiting for an answer | 28 | chat 11 | 2026-11-02 |
| 6 questions | questions/aliases-oct31.json waiting for an answer | 0 | chat 11 | 2026-11-01 |
| 6 questions | questions/gis-hunter.json waiting for an answer | 20 | chat 11 | 2026-11-03 |
| 6 questions | questions/hardlook.json waiting for an answer | 1,937 | chat 11 | 2026-11-02 |
| 6 questions | questions/key-pieces.json waiting for an answer | 0 | chat 11 | 2026-11-01 |
| 6 questions | questions/layers.json waiting for an answer | 470 | chat 11 | 2026-11-03 |
| 6 questions | questions/lost-finds-nov1.json waiting for an answer | 0 | chat 11 | 2026-11-01 |
| 6 questions | questions/map-audit.json waiting for an answer | 132 | chat 11 | 2026-11-03 |
| 6 questions | questions/nearmiss-nov2.json waiting for an answer | 45 | chat 11 | 2026-11-02 |
| 6 questions | questions/no-recheck.json waiting for an answer | 0 | chat 11 | 2026-11-01 |
| 6 questions | questions/not-sure-for-chat9.json waiting for an answer | 146 | chat 9 | 2026-11-01 **STUCK** |
| 6 questions | questions/parked.json waiting for an answer | 115 | chat 11 | 2026-11-03 |
| 6 questions | questions/world-finder.json waiting for an answer | 0 | chat 11 | 2026-11-01 |
| 7 waiting room | HELD campinfo files (a check failed; data/waiting/today.md says why) | 3 | chat 2 (fix) + chat 11 | 2026-10-31 **STUCK** |
| 7 waiting room | HELD docs files (a check failed; data/waiting/today.md says why) | 49 | chat 2 (fix) + chat 11 | 2026-10-31 **STUCK** |
| 7 waiting room | HELD fers files (a check failed; data/waiting/today.md says why) | 35 | chat 2 (fix) + chat 11 | 2026-11-01 **STUCK** |
| 7 waiting room | HELD trails files (a check failed; data/waiting/today.md says why) | 3 | chat 2 (fix) + chat 11 | 2026-11-01 **STUCK** |
| 7 waiting room | HELD truth files (a check failed; data/waiting/today.md says why) | 9 | chat 2 (fix) + chat 11 | 2026-11-01 **STUCK** |
| 7 waiting room | HELD world-key files (a check failed; data/waiting/today.md says why) | 1 | chat 2 (fix) + chat 11 | 2026-11-03 |
| 7 waiting room | files waiting for a grader (data/status/grade-queue.md) | 114 | chat 11 | 2026-11-03 |
| 8 bots | 2-fer checker: found work | 1 | chat 2 + chat 11 | 2026-11-01 **STUCK** |
| 8 bots | Cell coverage (FCC): found work | 1 | HQ | 2026-11-02 |
| 8 bots | Key bots: errors and silence: RED (the bot is broken) | 1 | chat 10 | 2026-11-03 |
| 8 bots | Storage keeper (weekly): found work | 1 | HQ | 2026-11-01 **STUCK** |
| 8 bots | T5 site checker: found work | 1 | chat 3 | 2026-11-01 **STUCK** |
| 8 bots | Website copy (site branch): RED (the bot is broken) | 1 | chat 10 | 2026-11-03 |
| 8 bots | key-doctor: found work | 1 | chat 10 | 2026-11-02 |
