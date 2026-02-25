from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "clean.parquet"
OUT_DIR = ROOT / "outputs" / "metrics"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(DATA)

# 1) v0-Regel: Stunden ohne Preis raus (sonst Capture nicht definierbar)
df = df.dropna(subset=["price_eur_mwh"]).copy()

# 2) Helper: Capture Price
def capture_price(price: pd.Series, gen_mwh: pd.Series) -> float:
    # Nur Stunden nehmen, in denen auch Gen vorhanden ist
    m = gen_mwh.notna() & price.notna()
    gen = gen_mwh[m]
    p = price[m]
    denom = gen.sum()
    if denom <= 0:
        return np.nan
    return float((p * gen).sum() / denom)

base_price = float(df["price_eur_mwh"].mean())

cp_wind = capture_price(df["price_eur_mwh"], df["wind_total_mwh"])
cp_solar = capture_price(df["price_eur_mwh"], df["solar_pv_mwh"])

metrics = pd.DataFrame([
    {"metric": "base_price_eur_mwh", "value": base_price},
    {"metric": "capture_price_wind_eur_mwh", "value": cp_wind},
    {"metric": "capture_ratio_wind", "value": cp_wind / base_price if base_price else np.nan},
    {"metric": "capture_price_solar_eur_mwh", "value": cp_solar},
    {"metric": "capture_ratio_solar", "value": cp_solar / base_price if base_price else np.nan},
])

# Print nicely
print("Rows after dropping missing price:", len(df))
print(metrics)

out = OUT_DIR / "capture_metrics_20260113_20260224.csv"
metrics.to_csv(out, index=False)
print("Saved:", out)
