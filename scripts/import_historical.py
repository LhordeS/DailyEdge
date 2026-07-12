from pathlib import Path
import pandas as pd

DATA_FILE = Path("data/nq-1m_bk.csv")

df = pd.read_csv(
    DATA_FILE,
    sep=";",
    header=None,
    names=[
        "Date",
        "Time",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ],
    skiprows=5_883_000,
    nrows=2000,
)

df["Timestamp"] = pd.to_datetime(
    df["Date"] + " " + df["Time"],
    format="%d/%m/%Y %H:%M"
)

day = df[
    (df["Timestamp"] >= "2026-06-30")
    & (df["Timestamp"] < "2026-07-01")
]

print(len(day))
print(day.head())
print(day.tail())
