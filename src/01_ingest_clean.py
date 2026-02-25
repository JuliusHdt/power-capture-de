from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data_raw"
DATA_OUT = ROOT / "data"
DATA_OUT.mkdir(parents=True, exist_ok=True)

PRICE_FILE = DATA_RAW / "smard_day_ahead_price_hourly_20260113_20260224.csv"
GEN_FILE   = DATA_RAW / "smard_generation_hourly_20260113_20260224.csv"
LOAD_FILE  = DATA_RAW / "smard_load_hourly_20260113_20260224.csv"

def read_smard_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=";",
        decimal=",",
        thousands=".",
        na_values=["-", "–", ""],
        encoding="utf-8",
    )

def add_timestamp_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ts = pd.to_datetime(df["Datum von"], dayfirst=True, errors="coerce")
    df.insert(0, "ts", ts)
    df = df.drop(columns=["Datum von", "Datum bis"], errors="ignore")
    df = df.set_index("ts").sort_index()
    return df

def find_col(prefix: str, df: pd.DataFrame) -> str:
    hits = [c for c in df.columns if c.startswith(prefix)]
    if len(hits) != 1:
        raise ValueError(f"Spalte nicht eindeutig für '{prefix}': {hits}")
    return hits[0]

def main():
    # Load
    df_price_raw = read_smard_csv(PRICE_FILE)
    df_gen_raw   = read_smard_csv(GEN_FILE)
    df_load_raw  = read_smard_csv(LOAD_FILE)

    # Timestamp index
    df_price = add_timestamp_index(df_price_raw)
    df_gen   = add_timestamp_index(df_gen_raw)
    df_load  = add_timestamp_index(df_load_raw)

    # Select columns
    price_col = [c for c in df_price.columns if c.startswith("Deutschland/Luxemburg") and "€/MWh" in c]
    if len(price_col) != 1:
        raise ValueError(f"Preis-Spalte nicht eindeutig gefunden: {price_col}")
    price_col = price_col[0]
    price = df_price[[price_col]].rename(columns={price_col: "price_eur_mwh"})

    col_wind_off = find_col("Wind Offshore", df_gen)
    col_wind_on  = find_col("Wind Onshore", df_gen)
    col_pv       = find_col("Photovoltaik", df_gen)
    gen = df_gen[[col_wind_off, col_wind_on, col_pv]].rename(columns={
        col_wind_off: "wind_offshore_mwh",
        col_wind_on:  "wind_onshore_mwh",
        col_pv:       "solar_pv_mwh",
    })
    gen["wind_total_mwh"] = gen["wind_offshore_mwh"] + gen["wind_onshore_mwh"]

    col_load = find_col("Netzlast [MWh]", df_load)
    load = df_load[[col_load]].rename(columns={col_load: "load_mwh"})

    # Merge
    df = price.join(gen, how="inner").join(load, how="inner")
    df["residual_load_calc_mwh"] = df["load_mwh"] - df["wind_total_mwh"] - df["solar_pv_mwh"]

    # Quick sanity prints
    print("Rows:", len(df), "| from:", df.index.min(), "| to:", df.index.max())
    print("Missing % (top):")
    print((df.isna().mean().sort_values(ascending=False) * 100).round(2).head(10))

    # Save
    out_parquet = DATA_OUT / "clean.parquet"
    out_csv = DATA_OUT / "clean.csv"
    try:
        df.to_parquet(out_parquet, index=True)
        print("Saved:", out_parquet)
    except Exception as e:
        df.to_csv(out_csv, index=True)
        print("Parquet not available, saved CSV instead:", out_csv)
        print("Reason:", repr(e))

if __name__ == "__main__":
    main()
