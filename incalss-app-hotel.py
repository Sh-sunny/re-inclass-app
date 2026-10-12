from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="NYC Airbnb Market Dashboard",
    page_icon="🏙️",
    layout="wide",
)


@st.cache_data
def load_data(file_bytes: bytes | None, file_path: str) -> pd.DataFrame:
    if file_bytes is not None:
        df = pd.read_csv(BytesIO(file_bytes))
    else:
        df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip().str.lower()

    # Support either British or American spelling.
    if "neighborhood_group" in df.columns and "neighbourhood_group" not in df.columns:
        df = df.rename(columns={"neighborhood_group": "neighbourhood_group"})

    required_columns = {
        "neighbourhood_group",
        "room_type",
        "price",
        "availability_365",
    }
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    # Remove currency symbols and commas before converting prices to numbers.
    df["price"] = (
        df["price"]
        .astype(str)
        .str.replace(r"[$,]", "", regex=True)
        .str.strip()
    )
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["availability_365"] = pd.to_numeric(
        df["availability_365"], errors="coerce"
    )

    df["neighbourhood_group"] = (
        df["neighbourhood_group"].fillna("Unknown").astype(str)
    )
    df["room_type"] = df["room_type"].fillna("Unknown").astype(str)

    return df


st.title("NYC Airbnb Market Dashboard | Team 4")
st.caption(
    "For multi-listing Airbnb hosts: compare asking prices and listing supply "
    "by borough and room type to guide pricing and promotion decisions."
)

data_path = Path(__file__).resolve().parent / "nyc_airbnb_2024.csv"
uploaded_file = None

if not data_path.exists():
    st.info(
        "Place nyc_airbnb_2024.csv in the same folder as this app, "
        "or upload the CSV below."
    )
    uploaded_file = st.file_uploader(
        "Upload nyc_airbnb_2024.csv",
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


with st.sidebar:
    st.header("Filters")

    borough_options = sorted(
        df["neighbourhood_group"].dropna().unique().tolist()
    )
    selected_boroughs = st.multiselect(
        "Borough",
        options=borough_options,
        default=borough_options,
    )

    room_type_options = sorted(
        df["room_type"].dropna().unique().tolist()
    )
    selected_room_types = st.multiselect(
        "Room type",
        options=room_type_options,
        default=room_type_options,
    )


filtered_df = df[
    df["neighbourhood_group"].isin(selected_boroughs)
    & df["room_type"].isin(selected_room_types)
].copy()

valid_prices = filtered_df[
    filtered_df["price"].notna() & (filtered_df["price"] > 0)
]
valid_availability = filtered_df[
    filtered_df["availability_365"].between(0, 365)
]

listing_count = (
    filtered_df["id"].nunique()
    if "id" in filtered_df.columns
    else len(filtered_df)
)
median_price = valid_prices["price"].median()
median_availability = valid_availability["availability_365"].median()

metric1, metric2, metric3 = st.columns(3)

metric1.metric("Listings in selection", f"{listing_count:,}")
metric2.metric(
    "Median nightly asking price",
    f"${median_price:,.0f}" if pd.notna(median_price) else "N/A",
)
metric3.metric(
    "Median days available in next 365 days",
    f"{median_availability:.0f}"
    if pd.notna(median_availability)
    else "N/A",
)


st.subheader("Median Asking Price by Borough")

price_by_borough = (
    valid_prices.groupby("neighbourhood_group")["price"]
    .median()
    .sort_values(ascending=False)
)

if price_by_borough.empty:
    st.warning("No valid prices are available for these filters.")
else:
    st.bar_chart(
        price_by_borough,
        y_label="Median nightly asking price (USD)",
        x_label="Borough",
    )


st.subheader("Number of Listings by Borough")

listings_by_borough = (
    filtered_df.groupby("neighbourhood_group")
    .size()
    .sort_values(ascending=False)
)

if listings_by_borough.empty:
    st.warning("No listings are available for these filters.")
else:
    st.bar_chart(
        listings_by_borough,
        y_label="Number of listings",
        x_label="Borough",
    )


st.caption(
    "Data period: January 5, 2024 snapshot, from Kaggle / Inside Airbnb. "
    "Proposed production refresh: weekly; host review: weekly."
)

st.caption(
    "This is listing data, not booking or transaction data. Asking price is "
    "not the final price paid, and days available are not occupancy."
)