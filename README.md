# re-inclass-app
# NYC Airbnb Market Dashboard | Team 4

**Team members:** [Add at least four team members]

A Streamlit dashboard for multi-listing Airbnb hosts to compare asking prices and listing supply across New York City boroughs.

## 1. Dataset and Decision-Maker

**Dataset:** [New York Dataset on Kaggle](https://www.kaggle.com/datasets/vrindakallu/new-york-dataset)

This dataset is a snapshot of Airbnb listings in New York City as of January 5, 2024. The published copy used for this project contains about 20,758 listings and 22 columns. Its original source is listed as Inside Airbnb. Each row represents one listing in the snapshot. See the [dataset overview](https://github.com/Evin-Thomas/nyc-airbnb-analysis) and [Inside Airbnb data page](https://insideairbnb.com/get-the-data/).

**Decision-maker:** A New York City Airbnb host who manages multiple listings.

The host reviews the market weekly and uses the dashboard to compare similar listings by borough and room type.

## 2. Why a Dashboard?

Hosts make pricing and promotion decisions repeatedly. If a host sees that a listing’s asking price is more than 10% above the median for comparable listings in the same borough and room type, while its calendar shows many available days, the host can review the price or try a promotion. This is a proposed review rule, not a claim that a price change will cause more bookings.

Hosts can check individual listings manually, but that makes it harder to compare several boroughs and room types regularly. A dashboard supports those repeated comparisons and lets the host filter the market to relevant peers.

## 3. What the Dashboard Shows

The dashboard presents three headline metrics:

- **Listings in selection:** Number of listings matching the filters.
- **Median nightly asking price:** Median listed price among records with valid positive prices.
- **Median days available:** Median `availability_365` among records with valid availability values.

The supporting charts show median asking price and listing count by borough. The filters let the host select boroughs and room types. Headline metrics appear first, followed by the charts that help explain local price and supply differences.

### What We Chose Not to Show

- **Individual host names and listing descriptions:** They add detail but do not help the market-level pricing comparison.
- **A booking or occupancy trend:** This snapshot contains listings, not reservation transactions or actual booked nights, so it cannot support a reliable booking trend.

### Data Limitations

The snapshot is dated January 5, 2024 and is not live. Asking prices are not necessarily the final prices paid. `availability_365` describes calendar availability; it is not an occupancy rate. The dataset also represents one city and may not reflect current conditions or markets elsewhere.

Before final submission, we will use a Pandas and Matplotlib notebook to inspect data types, missing values, price distributions, and price differences by borough and room type. We will report any important missingness or outliers found in the downloaded CSV.

## 4. Refresh and Review Frequency

A production version should refresh weekly from a permitted, current listing-data source. The host should review it weekly when planning prices and promotions. A weekly refresh fits recurring pricing decisions without implying that this Kaggle snapshot updates automatically.

Stale data could make a host compare against outdated competitor prices or listing supply. The Kaggle app is a fixed historical snapshot; it does not receive these proposed production updates.

**Data period:** January 5, 2024 snapshot  
**Proposed production refresh:** Weekly  
**Suggested review cadence:** Weekly
