from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "clean.parquet"
OUT_DIR = ROOT / "outputs" / "charts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(DATA)

# 1 Woche ab Start
start = df.index.min()
end = start + pd.Timedelta(days=7)
sub = df.loc[start:end].copy()

# Missing-Preise raus
sub = sub.dropna(subset=["price_eur_mwh"])

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(sub.index, sub["price_eur_mwh"])
ax.set_title("Day-Ahead Price DE/LU (1-week sample)")
ax.set_xlabel("Time")
ax.set_ylabel("€/MWh")

# Weniger, sauberere Datumslabels
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
fig.autofmt_xdate(rotation=30)

plt.tight_layout()

png_path = OUT_DIR / "price_timeseries_1week.png"
plt.savefig(png_path, dpi=150)
print("Saved chart:", png_path)
