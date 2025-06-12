# Zillow Deal Finder Bot (MVP)
# Phase 1: Mock Data + Filter + Streamlit Dashboard + Daily Email

import pandas as pd
import streamlit as st
from datetime import datetime

# ---------------------------
# MOCK DATA
# ---------------------------
mock_data = [
    {
        "address": "123 Oak St, Atlanta, GA",
        "price": 150000,
        "zestimate": 215000,
        "daysOnZillow": 42,
        "detailUrl": "https://www.zillow.com/homedetails/123oak"
    },
    {
        "address": "456 Maple Ave, Dallas, TX",
        "price": 190000,
        "zestimate": 260000,
        "daysOnZillow": 35,
        "detailUrl": "https://www.zillow.com/homedetails/456maple"
    },
    {
        "address": "789 Pine Rd, Charlotte, NC",
        "price": 170000,
        "zestimate": 200000,
        "daysOnZillow": 15,
        "detailUrl": "https://www.zillow.com/homedetails/789pine"
    },
    {
        "address": "321 Birch Blvd, Phoenix, AZ",
        "price": 300000,
        "zestimate": 300000,
        "daysOnZillow": 5,
        "detailUrl": "https://www.zillow.com/homedetails/321birch"
    }
]

# ---------------------------
# FUNCTION: Filter Deals
# ---------------------------
def filter_deals(data):
    df = pd.DataFrame(data)
    df = df[df['zestimate'].notnull() & df['price'].notnull()]
    df['discount_pct'] = 1 - (df['price'] / df['zestimate'])
    df_filtered = df[df['discount_pct'] >= 0.25]
    return df_filtered.sort_values(by='discount_pct', ascending=False)

# ---------------------------
# STREAMLIT DASHBOARD
# ---------------------------
st.title("🏠 Zillow Deal Finder - 25%+ Below Market (Mock Data)")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with st.spinner("Using mock property data..."):
    df_deals = filter_deals(mock_data)

    if not df_deals.empty:
        st.success(f"Found {len(df_deals)} deals 25%+ below market.")
        st.dataframe(df_deals[['address', 'price', 'zestimate', 'discount_pct', 'daysOnZillow', 'detailUrl']])
    else:
        st.warning("No deals found with 25% discount or more.")
