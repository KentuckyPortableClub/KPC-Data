"""Where the engine lives and what it may touch (club answers, round 3).

- KPC_DATA_REPO  = KentuckyPortableClub/KPC-Data : the engine runs here, reads club data here, and writes its
  results ONLY to this repo's `tools-out` branch (never to main, never to club data files).
- KPC_LINKS_REPO = KentuckyPortableClub/KPC-Links : the website (world maps + Kentucky files). READ-ONLY, always.
Env vars of the same names override these (for forks / try-outs).
"""
import os

KPC_DATA_REPO = os.environ.get('KPC_DATA_REPO') or 'KentuckyPortableClub/KPC-Data'
KPC_LINKS_REPO = os.environ.get('KPC_LINKS_REPO') or 'KentuckyPortableClub/KPC-Links'
RESULTS_BRANCH = os.environ.get('KPC_RESULTS_BRANCH') or 'tools-out'
READ_ONLY_REPOS = (KPC_LINKS_REPO,)        # never written; KPC-Data is written only on RESULTS_BRANCH
WRITE_TARGET = (KPC_DATA_REPO, RESULTS_BRANCH)


def can_write(repo, branch):
    """True only for KPC-Data's tools-out branch."""
    return (repo, branch) == WRITE_TARGET
