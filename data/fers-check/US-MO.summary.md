# 2-fer accuracy check: US-MO

Run 2026-11-01T02:07:46Z → 2026-11-08T06:27:38Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 77 · checked: 77 · skipped (dropped / merged): 326

| verdict | rows |
|---|---|
| CONFIRMED | 62 |
| SHRUNK | 9 |
| GREW | 4 |
| MOVED | 1 |
| NOT CHECKED | 1 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 17 |
| trail line from the club saved copy (not re-read live) | 30 |
| water-only | 1 |

## For a person to look at

- **SHRUNK** `US-0374+US-4579@trail@39.066,-92.940`: only 60% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-10110+US-9757@trail@36.923,-93.590`: only 73% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-1762+US-9757@trail@38.300,-93.357`: only 72% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-1766+US-4579@trail@38.987,-92.755`: live overlap is 51% smaller (1.5 ac vs 3.0 ac stored)
- **SHRUNK** `US-1766+US-9753@trail@38.541,-93.520`: live overlap is 66% smaller (0.8 ac vs 2.3 ac stored)
- **SHRUNK** `US-1777+US-3355@area@39.791,-93.233`: live overlap is 75% smaller (11.6 ac vs 47.2 ac stored)
- **SHRUNK** `US-4566+US-4576@trail@39.071,-95.782`: only 58% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `US-4576+US-4579@trail@39.018,-94.455`: live overlap is 38% smaller (7.4 ac vs 12.0 ac stored)
- **SHRUNK** `US-6491+US-6498@area@37.082,-91.057`: live overlap is 80% smaller (0.5 ac vs 2.3 ac stored)
- **GREW** `US-11015+US-4579@trail@39.094,-94.414`: live overlap is 42% bigger (0.8 ac vs 0.5 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1766+US-3349@trail@38.780,-90.481`: live overlap is 33% bigger (0.1 ac vs 0.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1772+US-3356@same land@39.493,-91.786`: live overlap is 64% bigger (1.8 ac vs 1.1 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `US-1788+US-7836@trail@37.567,-90.724`: live overlap is 100% bigger (1.9 ac vs 1.0 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `US-11138+US-1780@same land@36.597,-93.824`: live overlap centre is 3035 m from the stored centre; 0% of the stored overlap is still inside it
- **NOT CHECKED** `US-0788+US-4009+US-6498@area@37.193,-91.160`: key has no joined official outline for US-4009 (status 'pin')

The 2-fer file was not changed. A person and the club waiting room decide.
