# 2-fer accuracy check: US-FL

Run 2026-11-01T12:03:31Z → 2026-11-01T12:15:35Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 218 · checked: 218 · skipped (dropped / merged): 1055

| verdict | rows |
|---|---|
| CONFIRMED | 155 |
| SHRUNK | 14 |
| GREW | 7 |
| MOVED | 3 |
| GONE | 38 |
| RECORD CHANGED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 47 |
| trail line from the club saved copy (not re-read live) | 75 |
| water-only | 2 |

## For a person to look at

- **SHRUNK** `US-0896+US-3634@river@28.846,-81.393`: only 62% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-0896+US-4559@river@28.858,-81.435`: only 68% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-0896+US-8357@river@28.917,-81.546`: only 39% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-10552+US-4559@trail@30.417,-82.970`: live overlap is 83% smaller (0.4 ac vs 2.3 ac stored)
- **SHRUNK** `US-10602+US-4559@trail@30.384,-82.915`: live overlap is 91% smaller (0.2 ac vs 2.3 ac stored)
- **SHRUNK** `US-1866+US-4631@area@29.706,-81.299`: live overlap is 59% smaller (1.3 ac vs 3.2 ac stored)
- **SHRUNK** `US-1902+US-4559@trail@29.838,-81.950`: only 68% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-1915+US-4559@trail@29.185,-82.015`: live overlap is 36% smaller (48.3 ac vs 75.1 ac stored)
- **SHRUNK** `US-3634+US-4639@area@28.835,-81.407`: live overlap is 51% smaller (6.7 ac vs 13.5 ac stored)
- **SHRUNK** `US-3650+US-4559@trail@28.815,-81.426`: live overlap is 94% smaller (0.1 ac vs 1.3 ac stored)
- **SHRUNK** `US-4559+US-6302@trail@26.970,-81.118`: live overlap is 27% smaller (0.5 ac vs 0.6 ac stored)
- **SHRUNK** `US-4559+US-8691@trail@30.385,-82.889`: live overlap is 96% smaller (0.0 ac vs 1.2 ac stored)
- **SHRUNK** `US-4559+US-8716@trail@30.384,-82.915`: live overlap is 91% smaller (0.2 ac vs 2.3 ac stored)
- **SHRUNK** `US-4640+US-6288@area@29.843,-84.921`: live overlap is 35% smaller (4.8 ac vs 7.4 ac stored)
- **GREW** `US-0896+US-1927@river@28.714,-81.455`: live overlap is 82% bigger (10.5 ac vs 5.7 ac stored); 92% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-0896+US-4559@river@28.815,-81.419`: live overlap is 804926% bigger (4.5 ac vs 0.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-3637+US-6295+US-8368@area@29.618,-81.761`: live overlap is 97% bigger (3.9 ac vs 2.0 ac stored); 95% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-3663+US-6744@same land@27.592,-82.571`: live overlap is 65% bigger (1069.1 ac vs 646.8 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4559+US-6295@trail@29.533,-81.760`: live overlap is 27% bigger (4.8 ac vs 3.8 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4559+US-6321@trail@26.331,-80.882`: live overlap is 34% bigger (0.2 ac vs 0.2 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-4559+US-8680@trail@30.331,-82.691`: live overlap is 40% bigger (4.8 ac vs 3.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-0896+US-3650@river@28.715,-81.450`: live overlap centre is 8802 m from the stored centre; 8% of the stored overlap is still inside it
- **MOVED** `US-0896+US-4639@river@28.846,-81.447`: live overlap centre is 2047 m from the stored centre; 16% of the stored overlap is still inside it
- **MOVED** `US-1838+US-4613@same land@30.354,-82.708`: live overlap centre is 2052 m from the stored centre; 2% of the stored overlap is still inside it
- **GONE** `US-0245+US-3618@area@27.542,-81.410`: no overlap between the live official outlines near this spot
- **GONE** `US-0245+US-4640@area@27.327,-81.446`: no overlap between the live official outlines near this spot
- **GONE** `US-0245+US-6311@area@27.271,-81.324`: no overlap between the live official outlines near this spot
- **GONE** `US-0245+US-6328@area@27.297,-81.326`: no overlap between the live official outlines near this spot
- **GONE** `US-10559+US-4614@area@30.370,-82.882`: no overlap between the live official outlines near this spot
- **GONE** `US-12133+US-4634@area@26.146,-81.496`: no overlap between the live official outlines near this spot
- **GONE** `US-1878+US-3618@area@28.151,-82.243`: no overlap between the live official outlines near this spot
- **GONE** `US-1905+US-3663@area@29.397,-81.091`: no overlap between the live official outlines near this spot
- **GONE** `US-1905+US-4634@area@25.992,-81.544`: no overlap between the live official outlines near this spot
- **GONE** `US-1918+US-3618@area@26.009,-81.441`: no overlap between the live official outlines near this spot
- **GONE** `US-1924+US-3618@area@25.962,-81.360`: no overlap between the live official outlines near this spot
- **GONE** `US-1924+US-6296@area@30.573,-84.929`: no overlap between the live official outlines near this spot
- **GONE** `US-3612+US-3616@area@26.984,-82.182`: no overlap between the live official outlines near this spot
- **GONE** `US-3614+US-4628@area@28.910,-82.611`: no overlap between the live official outlines near this spot
- **GONE** `US-3616+US-6321@area@29.663,-82.538`: no overlap between the live official outlines near this spot
- **GONE** `US-3618+US-4614@area@30.919,-86.665`: no overlap between the live official outlines near this spot
- **GONE** `US-3618+US-4620@area@29.524,-81.891`: no overlap between the live official outlines near this spot
- **GONE** `US-3618+US-4628@area@30.519,-84.392`: no overlap between the live official outlines near this spot
- **GONE** `US-3618+US-5250@area@26.014,-81.376`: no overlap between the live official outlines near this spot
- **GONE** `US-3618+US-5520@area@26.049,-81.361`: no overlap between the live official outlines near this spot
- **GONE** `US-3618+US-6296@area@28.693,-82.574`: no overlap between the live official outlines near this spot
- **GONE** `US-3618+US-6310@area@26.413,-80.793`: no overlap between the live official outlines near this spot
- **GONE** `US-3637+US-5250@area@29.282,-81.942`: no overlap between the live official outlines near this spot
- **GONE** `US-3647+US-4646@area@28.755,-82.640`: no overlap between the live official outlines near this spot
- **GONE** `US-3651+US-4634@area@26.067,-81.562`: no overlap between the live official outlines near this spot
- **GONE** `US-3660+US-4559@trail@30.430,-83.036`: no overlap between the live official outlines near this spot
- **GONE** `US-3663+US-4634@area@26.011,-81.545`: no overlap between the live official outlines near this spot
- **GONE** `US-4559+US-4640@trail@28.611,-82.354`: no overlap between the live official outlines near this spot
- **GONE** `US-4614+US-4634@area@26.101,-81.482`: no overlap between the live official outlines near this spot
- **GONE** `US-4634+US-4640@area@26.021,-81.567`: no overlap between the live official outlines near this spot
- **GONE** `US-4634+US-6321@area@26.011,-81.548`: no overlap between the live official outlines near this spot
- **GONE** `US-4634+US-6328@area@26.147,-81.538`: no overlap between the live official outlines near this spot
- **GONE** `US-4640+US-4646@area@28.610,-82.356`: no overlap between the live official outlines near this spot
- **GONE** `US-4646+US-6296+US-6312@area@28.682,-82.604`: no overlap between the live official outlines near this spot
- **GONE** `US-4646+US-6312@area@28.707,-82.591`: no overlap between the live official outlines near this spot
- **GONE** `US-5250+US-6310@area@26.367,-80.794`: no overlap between the live official outlines near this spot
- **GONE** `US-6288+US-6296@area@29.796,-85.015`: no overlap between the live official outlines near this spot
- **GONE** `US-6296+US-6312@area@28.682,-82.604`: no overlap between the live official outlines near this spot
- **RECORD CHANGED** `US-3618+US-4634@area@26.049,-81.523`: US-3618: record sgflf171 renamed: key 'Fakahatchee Strand' -> live 'Save Our Everglades' (geometry now: MOVED: live overlap centre is 6312 m from the stored centre; 0% of the stored overlap is still inside it)

The 2-fer file was not changed. A person and the club waiting room decide.
