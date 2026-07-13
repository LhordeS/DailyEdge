from pathlib import Path

import pandas as pd
import psycopg
import io

DATA_FILE = Path("data/nq-1m_bk.csv")

with psycopg.connect("dbname=dailyedge_development") as connection:
    print("Connected to PostgreSQL")

    total_rows = 0

    for chunk in pd.read_csv(
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
            "Volume",
        ],
        skiprows=5_800_000,
        chunksize=100_000,
    ):
        chunk["Timestamp"] = pd.to_datetime(
            chunk["Date"] + " " + chunk["Time"],
            format="%d/%m/%Y %H:%M"
        )

        chunk = chunk.drop_duplicates(subset=["Timestamp"])

        duplicates = chunk[chunk["Timestamp"].duplicated(keep=False)]

        if not duplicates.empty:
            print(duplicates)

        chunk = chunk.drop(columns=["Date", "Time"])

        chunk = chunk[
            [
                "Timestamp",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
        ]

        buffer = io.StringIO()
        chunk.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        with connection.cursor() as cursor:
            with cursor.copy(
                """
                COPY candles (
                    timestamp,
                    open,
                    high,
                    low,
                    close,
                    volume
                )
                FROM STDIN WITH (FORMAT CSV)
                """
            ) as copy:
                copy.write(buffer.read())
        connection.commit()


        total_rows += len(chunk)
        print(f"Imported {total_rows:,} rows...")
