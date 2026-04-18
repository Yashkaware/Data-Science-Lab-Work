"""
Premier League Data Analysis Project
=====================================
Dataset: Premier League Stats (2006-2018)
Source: https://www.kaggle.com/datasets/thefc17/epl-results-19932018

Run: python epl_analysis.py
Outputs: charts saved as PNG files + summary printed to console
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

# ── Colour palette ─────────────────────────────────────────────────────────────
COLOURS = ["#378ADD", "#D85A30", "#1D9E75", "#BA7517", "#533AB7",
           "#D4537E", "#639922", "#888780", "#185FA5", "#993C1D"]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#F8F8F8",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#DDDDDD",
    "grid.linewidth": 0.6,
    "font.family": "DejaVu Sans",
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
})

# ── 1. Load / generate data ────────────────────────────────────────────────────
# If you have the Kaggle CSV, replace this block with:
#   df = pd.read_csv("results.csv")
# The synthetic data below mirrors the real dataset's structure exactly.

np.random.seed(42)
seasons  = [f"{y}/{str(y+1)[-2:]}" for y in range(2009, 2019)]
teams    = [
    "Man City", "Liverpool", "Chelsea", "Arsenal",
    "Man United", "Tottenham", "Leicester", "Everton",
    "West Ham", "Southampton"
]

rows = []
for season in seasons:
    for home in teams:
        for away in teams:
            if home == away:
                continue
            hg = np.random.poisson(1.6)
            ag = np.random.poisson(1.1)
            rows.append({
                "Season": season, "HomeTeam": home, "AwayTeam": away,
                "FTHG": hg, "FTAG": ag,
                "FTR": "H" if hg > ag else ("A" if ag > hg else "D"),
                "HS": np.random.randint(8, 20),
                "AS": np.random.randint(5, 16),
                "HST": max(0, hg + np.random.randint(0, 5)),
                "AST": max(0, ag + np.random.randint(0, 4)),
            })

df = pd.DataFrame(rows)
print(f"✅  Dataset loaded — {len(df):,} matches across {df['Season'].nunique()} seasons\n")

# ── 2. Build season standings ──────────────────────────────────────────────────
def season_table(season_df):
    """Return a league table for one season."""
    records = {t: {"P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"Pts":0} for t in teams}
    for _, r in season_df.iterrows():
        h, a = r.HomeTeam, r.AwayTeam
        records[h]["P"] += 1; records[a]["P"] += 1
        records[h]["GF"] += r.FTHG; records[h]["GA"] += r.FTAG
        records[a]["GF"] += r.FTAG; records[a]["GA"] += r.FTHG
        if r.FTR == "H":
            records[h]["W"] += 1; records[a]["L"] += 1
            records[h]["Pts"] += 3
        elif r.FTR == "A":
            records[a]["W"] += 1; records[h]["L"] += 1
            records[a]["Pts"] += 3
        else:
            records[h]["D"] += 1; records[a]["D"] += 1
            records[h]["Pts"] += 1; records[a]["Pts"] += 1
    tbl = pd.DataFrame(records).T
    tbl["GD"] = tbl["GF"] - tbl["GA"]
    return tbl.sort_values("Pts", ascending=False).reset_index().rename(columns={"index":"Team"})

all_tables = {s: season_table(df[df.Season == s]) for s in seasons}

# ── 3. Aggregate stats ─────────────────────────────────────────────────────────
agg = pd.concat([t.assign(Season=s) for s, t in all_tables.items()])
total_pts = agg.groupby("Team")["Pts"].sum().sort_values(ascending=False)
total_wins = agg.groupby("Team")["W"].sum().sort_values(ascending=False)
avg_gf     = agg.groupby("Team")["GF"].mean().sort_values(ascending=False)

# ── 4. Home vs Away advantage ──────────────────────────────────────────────────
home_wr = df[df.FTR=="H"].groupby("HomeTeam").size()
away_wr = df[df.FTR=="A"].groupby("AwayTeam").size()
total_m = df.groupby("HomeTeam").size()
home_rate = (home_wr / total_m * 100).reindex(teams).fillna(0)
away_rate = (away_wr / total_m * 100).reindex(teams).fillna(0)

# ── 5. Title winners (most points per season) ──────────────────────────────────
champions = {s: t.iloc[0]["Team"] for s, t in all_tables.items()}
title_counts = pd.Series(champions.values()).value_counts()

# ── 6. Shots-on-target → goals conversion ─────────────────────────────────────
home_conv = df.groupby("HomeTeam").apply(lambda x: x.FTHG.sum() / x.HST.sum() * 100)
away_conv = df.groupby("AwayTeam").apply(lambda x: x.FTAG.sum() / x.AST.sum() * 100)
conv = ((home_conv + away_conv) / 2).reindex(teams).sort_values(ascending=False)

# ── 7. Season goal totals ──────────────────────────────────────────────────────
season_goals = df.groupby("Season").apply(lambda x: (x.FTHG + x.FTAG).sum())

# ══════════════════════════════════════════════════════════════════════════════
# PLOTS
# ══════════════════════════════════════════════════════════════════════════════

fig, axes = plt.subplots(3, 2, figsize=(14, 16))
fig.suptitle("Premier League Analysis  |  2009–2019", fontsize=16, fontweight="bold", y=0.98)

# ── Plot 1: Total points ───────────────────────────────────────────────────────
ax = axes[0, 0]
bars = ax.barh(total_pts.index[::-1], total_pts.values[::-1],
               color=[COLOURS[i % len(COLOURS)] for i in range(len(total_pts))], edgecolor="none")
ax.set_title("Total Points (All Seasons)")
ax.set_xlabel("Points")
for bar in bars:
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
            str(int(bar.get_width())), va="center", fontsize=9)

# ── Plot 2: Title count ────────────────────────────────────────────────────────
ax = axes[0, 1]
ax.bar(title_counts.index, title_counts.values,
       color=COLOURS[:len(title_counts)], edgecolor="none")
ax.set_title("League Titles Won")
ax.set_ylabel("Titles")
ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
for i, v in enumerate(title_counts.values):
    ax.text(i, v + 0.05, str(v), ha="center", fontsize=10, fontweight="bold")

# ── Plot 3: Home vs Away win % ─────────────────────────────────────────────────
ax = axes[1, 0]
x = np.arange(len(teams))
w = 0.35
ax.bar(x - w/2, home_rate.values, w, label="Home win %", color=COLOURS[0], edgecolor="none")
ax.bar(x + w/2, away_rate.values, w, label="Away win %", color=COLOURS[1], edgecolor="none")
ax.set_xticks(x)
ax.set_xticklabels(teams, rotation=35, ha="right", fontsize=9)
ax.set_title("Home vs Away Win Rate (%)")
ax.set_ylabel("Win %")
ax.legend(fontsize=9)

# ── Plot 4: Shot conversion rate ──────────────────────────────────────────────
ax = axes[1, 1]
ax.bar(conv.index, conv.values,
       color=[COLOURS[i % len(COLOURS)] for i in range(len(conv))], edgecolor="none")
ax.set_title("Shot-on-Target Conversion Rate (%)")
ax.set_ylabel("Conversion %")
ax.set_xticklabels(conv.index, rotation=35, ha="right", fontsize=9)

# ── Plot 5: Goals per season trend ────────────────────────────────────────────
ax = axes[2, 0]
ax.plot(season_goals.index, season_goals.values, marker="o",
        color=COLOURS[0], linewidth=2.2, markersize=7)
ax.fill_between(season_goals.index, season_goals.values,
                alpha=0.12, color=COLOURS[0])
ax.set_title("Total Goals Scored per Season")
ax.set_ylabel("Goals")
ax.set_xticklabels(season_goals.index, rotation=35, ha="right", fontsize=9)

# ── Plot 6: Avg goals for per season ─────────────────────────────────────────
ax = axes[2, 1]
top5 = avg_gf.head(5).index.tolist()
for i, team in enumerate(top5):
    team_by_season = agg[agg.Team == team].set_index("Season")["GF"]
    ax.plot(team_by_season.index, team_by_season.values,
            marker="o", label=team, color=COLOURS[i], linewidth=1.8, markersize=5)
ax.set_title("Avg Goals For — Top 5 Teams by Season")
ax.set_ylabel("Avg Goals")
ax.legend(fontsize=8)
ax.set_xticklabels(seasons, rotation=35, ha="right", fontsize=8)

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig("epl_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("📊  Chart saved → epl_analysis.png")

# ── Console summary ────────────────────────────────────────────────────────────
print("\n" + "="*50)
print("  PREMIER LEAGUE — KEY INSIGHTS")
print("="*50)
print(f"\n🏆  Most titles:      {title_counts.idxmax()} ({title_counts.max()})")
print(f"📌  Most total pts:   {total_pts.idxmax()} ({int(total_pts.max())} pts)")
print(f"⚽  Best conversion:  {conv.idxmax()} ({conv.max():.1f}%)")
print(f"🏠  Highest home WR:  {home_rate.idxmax()} ({home_rate.max():.1f}%)")
print(f"✈️   Highest away WR:  {away_rate.idxmax()} ({away_rate.max():.1f}%)")
print(f"\n📅  Season with most goals: {season_goals.idxmax()} ({int(season_goals.max())} goals)")
print("\n" + "="*50)
print("  FINAL LEAGUE TABLE — 2018/19")
print("="*50)
print(all_tables[seasons[-1]][["Team","P","W","D","L","GF","GA","GD","Pts"]].to_string(index=False))
print()
