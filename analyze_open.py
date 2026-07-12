import pandas as pd


def load_data():
    df = pd.read_csv("data/NQ_5m.csv")
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df["Date"] = df["Datetime"].dt.date
    return df


def get_rth_session(df, date):
    session = df[df["Date"] == date]

    return (
        session
        .set_index("Datetime")
        .between_time("09:30", "15:55")
        .reset_index()
    )


def first_35_result(rth):
    opening_price = rth.iloc[0]["Open"]

    up_target = opening_price + 35
    down_target = opening_price - 35

    for _, candle in rth.iterrows():
        hit_up = candle["High"] >= up_target
        hit_down = candle["Low"] <= down_target

        if hit_up and hit_down:
            return "Unknown"

        if hit_up:
            return "Up"

        if hit_down:
            return "Down"

    return "Neither"


def analyze(df):
    opening_candles = df[
        df["Datetime"].dt.time == pd.Timestamp("09:30").time()
    ]

    results = []

    for date in opening_candles["Date"]:
        rth = get_rth_session(df, date)

        results.append({
            "Date": date,
            "First35": first_35_result(rth)
        })

    return pd.DataFrame(results)


def main():
    df = load_data()

    results = analyze(df)

    results.to_csv("output/open_first35.csv", index=False)

    print(results.head())
    print(f"\nAnalyzed {len(results)} sessions.")


if __name__ == "__main__":
    main()
