import pandas as pd

IMPULSE = 35

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
    opening_candles = df[
        df["Datetime"].dt.time == pd.Timestamp("09:30").time()
    ]

    results = []

    for date in opening_candles["Date"]:
        rth = get_rth_session(df, date)

        direction, impulse_index = first_impulse(rth)

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

    results.to_csv(f"output/open_firstImpulse{IMPULSE}.csv", index=False)

    print(results.head())
    print(f"\nAnalyzed {len(results)} sessions.")


if __name__ == "__main__":
    main()
