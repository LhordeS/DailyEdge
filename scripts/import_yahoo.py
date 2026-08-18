from pathlib import Path
import psycopg
import pandas as pd

DATA_FILE = Path("data/NQ_1m.csv")

df = pd.read_csv(DATA_FILE)

df["Datetime"] = pd.to_datetime(df["Datetime"])

df["Timestamp"] = (
    df["Datetime"]
    .dt.tz_convert("America/Chicago")
    .dt.tz_localize(None)
)

df = df[
    [
        "Timestamp",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]
]

with psycopg.connect("dbname=dailyedge_development") as connection:
    print("Connected to PostgreSQL")

    with connection.cursor() as cursor:
        inserted_rows = 0
        for row in df.itertuples(index=False):
            cursor.execute(
                """
                INSERT INTO CANDLES (
                    timestamp,
                    open,
                    high,
                    low,
                    close,
                    volume
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (timestamp) DO NOTHING
                RETURNING id
                """,
                (
                    row.Timestamp,
                    row.Open,
                    row.High,
                    row.Low,
                    row.Close,
                    row.Volume,
                ),
            )
            if cursor.fetchone() is not None:
                inserted_rows += 1

    connection.commit()
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(timestamp) FROM CANDLES")
        latest_timestamp = cursor.fetchone()[0]

print(f"Import complete. Added {inserted_rows:,} new candles.")
print(f"Database current through: {latest_timestamp} CT")
