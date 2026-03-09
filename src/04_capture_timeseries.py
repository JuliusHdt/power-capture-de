from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "clean.parquet"
OUT_METRICS = ROOT / "outputs" / "metrics"
OUT_CHARTS = ROOT / "outputs" / "charts"

OUT_METRICS.mkdir(parents=True, exist_ok=True)
OUT_CHARTS.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(DATA_FILE)

# Stunden ohne Preis entfernen, weil Capture sonst nicht sauber berechnet werden kann
df = df.dropna(subset=["price_eur_mwh"]).copy()

def capture_price(price: pd.Series, generation: pd.Series) -> float:
    mask = price.notna() & generation.notna()
    p = price[mask]
    g = generation[mask]

    if g.sum() <= 0:
        return np.nan

    return float((p * g).sum() / g.sum())

rows = []

for period_start, group in df.resample("W-MON"):
    base_price = group["price_eur_mwh"].mean()

    wind_cp = capture_price(group["price_eur_mwh"], group["wind_total_mwh"])
    solar_cp = capture_price(group["price_eur_mwh"], group["solar_pv_mwh"])

    rows.append(
        {
            "week_start": period_start,
            "base_price_eur_mwh": base_price,
            "wind_capture_price_eur_mwh": wind_cp,
            "solar_capture_price_eur_mwh": solar_cp,
            "wind_capture_ratio": wind_cp / base_price if pd.notna(base_price) and base_price != 0 else np.nan,
            "solar_capture_ratio": solar_cp / base_price if pd.notna(base_price) and base_price != 0 else np.nan,
            "hours_in_week": len(group),
        }
    )

weekly = pd.DataFrame(rows).sort_values("week_start")

csv_path = OUT_METRICS / "capture_ratio_weekly.csv"
weekly.to_csv(csv_path, index=False)

plt.figure(figsize=(10, 5))
plt.plot(weekly["week_start"], weekly["wind_capture_ratio"], label="Wind capture ratio")
plt.plot(weekly["week_start"], weekly["solar_capture_ratio"], label="Solar capture ratio")
plt.axhline(1.0, linestyle="--")
plt.title("Weekly Capture Ratios (DE/LU)")
plt.xlabel("Week")
plt.ylabel("Capture ratio")
plt.legend()
plt.tight_layout()

png_path = OUT_CHARTS / "capture_ratio_weekly.png"
plt.savefig(png_path, dpi=150)

print("Saved metrics:", csv_path)
print("Saved chart:", png_path)
print()
print(weekly.round(4))
