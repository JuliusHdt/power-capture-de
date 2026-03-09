from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "clean.parquet"
OUT_METRICS = ROOT / "outputs" / "metrics"
OUT_CHARTS = ROOT / "outputs" / "charts"

OUT_METRICS.mkdir(parents=True, exist_ok=True)
OUT_CHARTS.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(DATA_FILE)

# Stunden ohne Preis entfernen
df = df.dropna(subset=["price_eur_mwh"]).copy()

# Stunde des Tages aus dem Zeitindex ziehen
df["hour"] = df.index.hour

hourly = (
    df.groupby("hour")
    .agg(
        avg_price_eur_mwh=("price_eur_mwh", "mean"),
        avg_solar_pv_mwh=("solar_pv_mwh", "mean"),
        avg_wind_total_mwh=("wind_total_mwh", "mean"),
        n_hours=("price_eur_mwh", "size"),
    )
    .reset_index()
)

csv_path = OUT_METRICS / "hourly_profile.csv"
hourly.to_csv(csv_path, index=False)

fig, ax1 = plt.subplots(figsize=(11, 6))

# Preis auf linker Achse
line1 = ax1.plot(
    hourly["hour"],
    hourly["avg_price_eur_mwh"],
    label="Avg price (€/MWh)",
    color="black",
    linewidth=2,
)
ax1.set_xlabel("Hour of day")
ax1.set_ylabel("Avg price (€/MWh)")

# Solar + Wind auf rechter Achse
ax2 = ax1.twinx()
line2 = ax2.plot(
    hourly["hour"],
    hourly["avg_solar_pv_mwh"],
    label="Avg solar (MWh)",
    color="goldenrod",
    linewidth=2,
)
line3 = ax2.plot(
    hourly["hour"],
    hourly["avg_wind_total_mwh"],
    label="Avg wind (MWh)",
    color="steelblue",
    linewidth=2,
)
ax2.set_ylabel("Avg generation (MWh)")

lines = line1 + line2 + line3
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc="upper right")

plt.title("Hourly Price and Generation Profiles")
plt.tight_layout()

png_path = OUT_CHARTS / "hourly_price_solar_profile.png"
plt.savefig(png_path, dpi=150)

print("Saved metrics:", csv_path)
print("Saved chart:", png_path)
print()
print(hourly.round(2))
