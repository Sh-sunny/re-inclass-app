from __future__ import annotations

from io import BytesIO
from pathlib import Path
import calendar

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Hotel Booking Dashboard",
    page_icon="🏨",
    layout="wide",
)


@st.cache_data
def load_data(file_bytes: bytes | None, file_path: str) -> pd.DataFrame:
    if file_bytes is not None:
        df = pd.read_csv(BytesIO(file_bytes))
    else:
        df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip().str.lower()

    required_columns = {
        "hotel",
        "is_canceled",
        "arrival_date_year",
        "arrival_date_month",
        "stays_in_weekend_nights",
        "stays_in_week_nights",
    }
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    df["is_canceled"] = pd.to_numeric(
        df["is_canceled"], errors="coerce"
    )
    df["arrival_date_year"] = pd.to_numeric(
        df["arrival_date_year"], errors="coerce"
    )

    month_numbers = {
        calendar.month_name[i]: i for i in range(1, 13)
    }
    month_numbers.update({
        calendar.month_abbr[i]: i for i in range(1, 13)
    })

    month_names = (
        df["arrival_date_month"]
        .astype("string")
        .str.strip()
        .str.title()
    )
    df["arrival_month_number"] = month_names.map(month_numbers)

    df["arrival_month"] = pd.to_datetime(
        {
            "year": df["arrival_date_year"],
            "month": df["arrival_month_number"],
            "day": 1,
        },
        errors="coerce",
    )

    for column in [
        "stays_in_weekend_nights",
        "stays_in_week_nights",
    ]:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        ).fillna(0)

    df["room_nights"] = (
        df["stays_in_weekend_nights"]
        + df["stays_in_week_nights"]
    )

    return df


st.title("Hotel Booking Dashboard | Team 4")
st.caption(
    "For hotel revenue managers: review booking cancellations by hotel "
    "and arrival month to inform channel and booking policy decisions."
)

data_path = Path(__file__).resolve().parent / "hotel_bookings.csv"
uploaded_file = None

if not data_path.exists():
    st.info(
        "Place hotel_bookings.csv in the same folder as this app, "
        "or upload the CSV below."
    )
    uploaded_file = st.file_uploader(
        "Upload hotel_bookings.csv",
        type=["csv"],
    )

    if uploaded_file is None:
        st.stop()

try:
    file_bytes = uploaded_file.getvalue() if uploaded_file else None
    df = load_data(file_bytes, str(data_path))
except Exception as error:
    st.error(f"Could not load the data: {error}")
    st.stop()


valid_arrival_months = df["arrival_month"].dropna()

if valid_arrival_months.empty:
    st.error("Could not create valid arrival dates from the data.")
    st.stop()

start_period = valid_arrival_months.min().strftime("%b %Y")
end_period = valid_arrival_months.max().strftime("%b %Y")


with st.sidebar:
    st.header("Filters")

    hotel_options = [
        "All hotels",
        *sorted(df["hotel"].dropna().unique().tolist()),
    ]
    selected_hotel = st.selectbox(
        "Hotel type",
        hotel_options,
    )

    years = sorted(
        df["arrival_date_year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )
    selected_years = st.multiselect(
        "Arrival year",
        options=years,
        default=years,
    )


filtered_df = df.copy()

if selected_hotel != "All hotels":
    filtered_df = filtered_df[
        filtered_df["hotel"] == selected_hotel
    ]

if selected_years:
    filtered_df = filtered_df[
        filtered_df["arrival_date_year"].isin(selected_years)
    ]
else:
    filtered_df = filtered_df.iloc[0:0]


booking_count = len(filtered_df)

if booking_count > 0:
    cancellation_rate = filtered_df["is_canceled"].mean()
else:
    cancellation_rate = 0

confirmed_bookings = filtered_df[
    filtered_df["is_canceled"] == 0
]
confirmed_room_nights = int(
    confirmed_bookings["room_nights"].sum()
)


st.subheader("Key Signal")
st.metric(
    "Cancellation rate",
    f"{cancellation_rate:.1%}",
)

metric1, metric2 = st.columns(2)
metric1.metric("Bookings", f"{booking_count:,}")
metric2.metric(
    "Room nights in confirmed bookings",
    f"{confirmed_room_nights:,}",
)


st.subheader("Cancellation Rate by Arrival Month")

monthly_data = filtered_df.dropna(
    subset=["arrival_month"]
).copy()
monthly_data["arrival_month_label"] = (
    monthly_data["arrival_month"].dt.strftime("%Y-%m")
)

monthly_cancellation_rate = (
    monthly_data
    .groupby("arrival_month_label")["is_canceled"]
    .mean()
    .sort_index()
)

if monthly_cancellation_rate.empty:
    st.warning("No monthly data is available for these filters.")
else:
    st.line_chart(
        monthly_cancellation_rate,
        y_label="Cancellation rate",
        x_label="Arrival month",
    )


if "market_segment" in filtered_df.columns:
    st.subheader("Cancellation Rate by Market Segment")

    segment_data = (
        filtered_df.dropna(subset=["market_segment"])
        .groupby("market_segment")["is_canceled"]
        .mean()
        .sort_values(ascending=False)
    )

    if not segment_data.empty:
        st.bar_chart(
            segment_data,
            y_label="Cancellation rate",
            x_label="Market segment",
        )


st.caption(
    f"Data period: {start_period} – {end_period} "
    "(Kaggle historical snapshot). "
    "Proposed production refresh: daily; manager review: weekly, "
    "with additional review during peak periods or cancellation spikes."
)

st.caption(
    "Metric note: cancellation rate is calculated from booking records. "
    "Room nights in confirmed bookings are not the same as occupancy "
    "or actual revenue. Room type codes are anonymized."
)