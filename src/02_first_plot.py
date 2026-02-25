from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "clean.parquet"
OUT_DIR = ROOT / "outputs" / "charts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(DATA)

start = df.index.min()
end = start + pd.Timedelta(days=7)
sub = df.loc[start:end].copy()
sub = sub.dropna(subset=["price_eur_mwh"])

plt.figure()
plt.plot(sub.index, sub["price_eur_mwh"])
plt.title("Day-Ahead Price DE/LU (1-week sample)")
plt.xlabel("Time")
plt.ylabel("€/MWh")
plt.tight_layout()

out = OUT_DIR / "price_timeseries_1week.png"
plt.savefig(out, dpi=150)
print("Saved chart:", out)
