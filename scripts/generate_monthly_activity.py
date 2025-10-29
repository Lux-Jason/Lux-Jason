#!/usr/bin/env python3
"""
Generate a monthly commits activity bar chart for the last N months.

Usage (in CI via GITHUB_REPOSITORY and GITHUB_TOKEN envs):
  python3 scripts/generate_monthly_activity.py

Outputs:
  assets/monthly-activity.png
"""
import os
import sys
import datetime
from collections import Counter

# PyGithub import with Auth token support (avoid DeprecationWarning)
try:
    from github import Github, Auth
except Exception:
    # older PyGithub may not have Auth; fallback to simple Github(token)
    from github import Github  # type: ignore
    Auth = None  # type: ignore

# Use non-interactive backend before importing pyplot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dateutil.relativedelta import relativedelta

# Config
REPO = os.environ.get("GITHUB_REPOSITORY")
TOKEN = os.environ.get("GITHUB_TOKEN")
OUT_PATH = "assets/monthly-activity.png"
MONTHS = int(os.environ.get("MONTHS", "12"))  # last N months (default 12)

if not REPO or not TOKEN:
    print("Error: GITHUB_REPOSITORY and GITHUB_TOKEN must be set in the environment", file=sys.stderr)
    sys.exit(1)

# Authenticate using preferred method
if "Auth" in globals() and Auth is not None:
    gh = Github(auth=Auth.Token(TOKEN))
else:
    # fallback (works but may raise deprecation warning on some versions)
    gh = Github(TOKEN)

repo = gh.get_repo(REPO)
print(f"Generating monthly activity for repository: {REPO}")

# compute month labels (YYYY-MM) for the last MONTHS months including current month
now = datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
months = []
for i in range(MONTHS - 1, -1, -1):
    m = now - relativedelta(months=i)
    months.append(m.strftime("%Y-%m"))

# list commits since earliest month start
earliest = now - relativedelta(months=MONTHS - 1)
print("Fetching commits since:", earliest.isoformat())
commits = repo.get_commits(since=earliest)

counts = Counter()
fetched = 0
for c in commits:
    fetched += 1
    try:
        dt = c.commit.author.date
    except Exception:
        # skip commits without author date (rare)
        continue
    ym = dt.strftime("%Y-%m")
    if ym in months:
        counts[ym] += 1
print(f"Fetched {fetched} commits (counted {sum(counts.values())} in range)")

# ensure zero for months without commits
ordered_counts = [counts.get(m, 0) for m in months]

# Choose a plotting style with fallbacks to available styles
available = plt.style.available
preferred = [
    "seaborn-darkgrid",
    "seaborn-v0_8-darkgrid",
    "seaborn",
    "ggplot",
    "fivethirtyeight",
    "default",
]
for s in preferred:
    if s in available:
        plt.style.use(s)
        print("Using matplotlib style:", s)
        break
else:
    print("No preferred style available; using matplotlib default")

# Plot
fig, ax = plt.subplots(figsize=(10, 4))
bars = ax.bar(months, ordered_counts, color="#2b6cb0")
ax.set_title(f"Monthly Activity (commits) — last {MONTHS} months")
ax.set_ylabel("Commits")
ax.set_xlabel("Month")
ax.set_xticklabels(months, rotation=45, ha="right")
# annotate bars
for rect, val in zip(bars, ordered_counts):
    ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height(), str(val), ha="center", va="bottom", fontsize=8)

plt.tight_layout()
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
plt.savefig(OUT_PATH, dpi=150)
print("Saved monthly activity image to", OUT_PATH)
