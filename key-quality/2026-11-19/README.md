# Outside-agent kits A, B, C (Opus, 19 Nov 2026; key-quality.md section 15)
Each kit/ folder is what Brandon gives the agent; it starts with README-FOR-THE-AGENT.md. Answers come back on KPC-Data branch
intake-files as key-quality/<kit>.answers.csv (or attached in a chat). One agent is ONE grader: nothing joins the gold set and no
saved answer is written from one pass alone.
- kitA-second-pass: second-look 01 again, letters reshuffled (seed second-pass-2026-11-19), 3 NEW plants (US-3486, US-4179,
  US-4560), briefed to prove each outline wrong. kit-keys/ is the answer key: NEVER give it to the agent. Score with
  kpc_key_grade.py score WITHOUT --gold (score --gold adds the graded parks to the gold set; that is Fable's call).
- kitB-park-preserve: 23 NPS unit codes with a preserve: one unit or two parts, NPS official acres per part, POTA ref per part,
  which boundary record is which. Known answer: DENA (NPS: Park 4,740,091 ac, Preserve 1,334,118 ac).
- kitC-acreage: the NPS acreage summary, the FWS lands report and the USFS land areas report as three tables (step 6).
