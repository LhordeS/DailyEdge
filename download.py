from pathlib import Path

import yfinance as yf

OUTPUT = Path("data")
OUTPUT.mkdir(exist_ok=True)

ticker = "NQ=F"

print("Downloading price data...")

df = yf.download(
    ticker,
    period="2y",
    interval="1d",
    auto_adjust=False
)

df = df.reset_index()

if hasattr(df.columns, "levels"):
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

df.to_csv(OUTPUT / "NQ.csv", index=False)

print(f"Saved {len(df)} trading days.")
