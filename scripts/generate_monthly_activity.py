#!/usr/bin/env python3
import os
import datetime
from collections import Counter, OrderedDict
from github import Github
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

# Settings
REPO = os.environ.get("GITHUB_REPOSITORY")
TOKEN = os.environ.get("GITHUB_TOKEN")
OUT_PATH = "assets/monthly-activity.png"
MONTHS = 12  # last N months

if not REPO or not TOKEN:
    raise SystemExit("GITHUB_REPOSITORY and GITHUB_TOKEN must be set in the environment")

gh = Github(TOKEN)
repo = gh.get_repo(REPO)

# compute month boundaries (YYYY-MM) for the last MONTHS months including current month
now = datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
months = []
for i in range(MONTHS - 1, -1, -1):
    m = now - relativedelta(months=i)
    months.append(m.strftime("%Y-%m"))

# list commits since earliest month start
earliest = now - relativedelta(months=MONTHS - 1)
since = earliest
commits = repo.get_commits(since=since)

counts = Counter()
for c in commits:
    # commit.commit.author may be None for some commits (rare)
    try:
        dt = c.commit.author.date
    except Exception:
        continue
    ym = dt.strftime("%Y-%m")
    if ym in months:
        counts[ym] += 1

# ensure zero for months without commits
ordered_counts = [counts.get(m, 0) for m in months]

# Plot
plt.style.use("seaborn-darkgrid")
fig, ax = plt.subplots(figsize=(10, 4))
bars = ax.bar(months, ordered_counts, color="#2b6cb0")
ax.set_title("Monthly Activity (commits) — last {} months".format(MONTHS))
ax.set_ylabel("Commits")
ax.set_xlabel("Month")
ax.set_xticklabels(months, rotation=45, ha="right")
for rect, val in zip(bars, ordered_counts):
    ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height(), str(val), ha="center", va="bottom", fontsize=8)

plt.tight_layout()
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
plt.savefig(OUT_PATH, dpi=150)
print("Saved monthly activity image to", OUT_PATH)
