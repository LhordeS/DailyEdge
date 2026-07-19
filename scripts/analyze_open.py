import pandas as pd
import psycopg

def compute_daily_atr(df):
    daily = (
        df.groupby("SessionDate").agg(
            Open=("Open", "first"),
            High=("High", "max"),
            Low=("Low", "min"),
            Close=("Close", "last")
        )
    )

    daily["PrevClose"] = daily["Close"].shift(1)

    daily["TR"] = (
        pd.concat(
            [
                daily["High"] - daily["Low"],
                (daily["High"] - daily["PrevClose"]).abs(),
                (daily["Low"] - daily["PrevClose"]).abs()
            ],
            axis=1,
        ).max(axis=1)
    )

    daily["ATR14"] = daily["TR"].rolling(14).mean().shift(1)

    return daily

IMPULSE = 100

def load_data():
    query = """
        SELECT
            timestamp,
            open,
            high,
            low,
            close,
            volume
        FROM candles
        ORDER BY timestamp;
    """

    with psycopg.connect("dbname=dailyedge_development") as connection:
        df = pd.read_sql(query, connection)

    print(df.columns.tolist())

    df.rename(columns={
        "timestamp": "Datetime",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    }, inplace=True)

    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df["Date"] = df["Datetime"].dt.date

    df["SessionDate"] = (
        df["Datetime"] + pd.to_timedelta((df["Datetime"].dt.hour >= 17).astype(int), unit="D",)
    ).dt.date


    return df

def get_rth_session(df, date):
    session = df[df["Date"] == date]

    return (
        session
        .set_index("Datetime")
        .between_time("09:30", "15:55")
        .reset_index()
    )


def first_impulse(rth):
    opening_price = rth.iloc[0]["Open"]

    up_target = opening_price + IMPULSE
    down_target = opening_price - IMPULSE

    for index, (_, candle) in enumerate(rth.iterrows()):
        hit_up = candle["High"] >= up_target
        hit_down = candle["Low"] <= down_target

        if hit_up and hit_down:
            return "Unknown", None

        if hit_up:
            return "Up", index

        if hit_down:
            return "Down", index

    return "Neither", None


def analyze(df):
    results = []

    sessions = df.groupby("Date")

    for date, rth in sessions:
        rth = (
            rth.set_index("Datetime").between_time("08:30", "14:55").reset_index()
        )

        print(date, len(rth))

        if rth.empty:
            continue


        print(rth.iloc[0]["Datetime"])
        print(rth.iloc[0]["Open"])
        print(rth["High"].max())
        print(rth["Low"].min())

        direction, impulse_index = first_impulse(rth)
        print(direction, impulse_index)
        break

        opening_price = rth.iloc[0]["Open"]

        impulse_mfe = None
        impulse_mae = None

        if direction == "Up":
            reference = opening_price + IMPULSE
            post_impulse = rth.iloc[impulse_index:]

            impulse_mfe = post_impulse["High"].max() - reference
            impulse_mae = reference - post_impulse["Low"].min()

        elif direction == "Down":
            reference = opening_price - IMPULSE
            post_impulse = rth.iloc[impulse_index:]

            impulse_mfe = reference - post_impulse["Low"].min()
            impulse_mae = post_impulse["High"].max() - reference

        results.append({
            "Date": date,
            f"First{IMPULSE}": direction,
            "ImpulseMFE": impulse_mfe,
            "ImpulseMAE": impulse_mae
        })

    return pd.DataFrame(results)

def main():
    df = load_data()
    results = analyze(df)
    daily = compute_daily_atr(df)

    results.to_csv(f"output/open_firstImpulse{IMPULSE}.csv", index=False)

    print(results.head())
    print(f"\nAnalyzed {len(results)} sessions.")
    print(daily[["High", "Low", "Close", "PrevClose", "ATR14"]].head(20))


if __name__ == "__main__":
    main()
