from pathlib import Path
import subprocess

import yfinance as yf

OUTPUT = Path("data")
OUTPUT.mkdir(exist_ok=True)

ticker = "NQ=F"

print("Downloading price data...")

df = yf.download(
    ticker,
    period="7d",
    interval="1m",
    auto_adjust=False
)

df = df.reset_index()

print(f"Earliest candle: {df['Datetime'].min()}")
print(f"Latest candle:   {df['Datetime'].max()}")

if hasattr(df.columns, "levels"):
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

df.to_csv(OUTPUT / "NQ_1m.csv", index=False)

print(f"Saved {len(df)} candles.")
print("Importing new candles into PostgreSQL...")

subprocess.run(
    ["python", "scripts/import_yahoo.py"],
    check=True,
)
