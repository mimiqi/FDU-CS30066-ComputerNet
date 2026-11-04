"""Render the exact P3-7 distribution-time calculations as a static chart."""

from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[1]
ROOT.joinpath("assets").mkdir(exist_ok=True)
F, US, D = 20 * 10**9, 30 * 10**6, 2 * 10**6
N_VALUES = [10, 100, 1000]
cs = [max(Fraction(n * F, US), Fraction(F, D)) for n in N_VALUES]
series = [("CS", cs, "#222222", "s")]
for upload, label, color, marker in [
    (300000, "P2P: u = 300 Kbps", "#29689b", "o"),
    (700000, "P2P: u = 700 Kbps", "#b56824", "^"),
    (2000000, "P2P: u = 2 Mbps", "#43806a", "D"),
]:
    values = [max(Fraction(F, US), Fraction(F, D), Fraction(n * F, US + n * upload)) for n in N_VALUES]
    series.append((label, values, color, marker))

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig, ax = plt.subplots(figsize=(8.6, 5.1), dpi=180)
for label, values, color, marker in series:
    ax.plot(N_VALUES, [float(value) for value in values], label=label,
            color=color, marker=marker, linewidth=1.8, markersize=6)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xticks(N_VALUES, [str(n) for n in N_VALUES])
ax.set_yticks([10000, 20000, 50000, 100000, 200000, 500000, 1000000])
ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
ax.set_ylim(7500, 1000000)
ax.set_xlim(8, 1300)
ax.set_xlabel("Number of peers, N (log scale)")
ax.set_ylabel("Minimum distribution time (seconds, log scale)")
ax.set_title("P3-7: File distribution time", loc="left", weight="bold", pad=14)
ax.grid(axis="y", which="major", color="#dddddd", linewidth=0.6)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="upper left", frameon=False)
fig.text(0.12, 0.025, "Source: Homework 3, P3-7. Ideal fluid model; F = 20 Gbit, server upload = 30 Mbps, peer download = 2 Mbps.", fontsize=8)
fig.tight_layout(rect=(0, 0.055, 1, 1))
output = ROOT / "assets" / "p3_7_distribution_time.png"
fig.savefig(output, facecolor="white")
plt.close(fig)
print(output)
