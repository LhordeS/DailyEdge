from pathlib import Path

import pandas as pd

DATA_FILE = Path("data/NQ.csv")
OUTPUT_FILE = Path("output/daily_stats.csv")

def direction(row):
    return "Bull" if row["Close"] > row["Open"] else "Bear"

def extension(row):
    if direction(row) == "Bull":
        return row["High"] - row["Open"]
    else:
        return row["Open"] - row["Low"]

def counter_move(row):
    if direction(row) == "Bull":
        return row["Open"] - row["Low"]
    else:
        return row["High"] - row["Open"]

def main():
    df = pd.read_csv(DATA_FILE)

    df["Direction"] = df.apply(direction, axis=1)
    df["Extension"] = df.apply(extension, axis=1)
    df["Counter"] = df.apply(counter_move, axis=1)

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(df[["Date", "Direction", "Extension", "Counter"]].head())
    print(f"\nSaved {len(df)} rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
