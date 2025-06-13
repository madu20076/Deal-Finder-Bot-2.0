import os
import pandas as pd
import streamlit as st
import requests
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# --- CONFIGURATION (set via environment variables) ---
APIFY_TASK_ID = os.getenv("APIFY_TASK_ID")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
DISCOUNT_THRESHOLD = float(os.getenv("DISCOUNT_THRESHOLD", 0.25))
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM")

# --- Fetch data from Apify Zillow actor ---
def fetch_zillow_data():
    url = f"https://api.apify.com/v2/actor-tasks/{APIFY_TASK_ID}/runs/last/dataset/items?token={APIFY_TOKEN}"
    resp = requests.get(url)
    if resp.status_code != 200:
        st.error(f"Failed to fetch: {resp.status_code}")
        return pd.DataFrame()
    data = resp.json()
    df = pd.json_normalize(data)
    return df

# --- Filter deals 25%+ below Zestimate ---
def filter_deals(df):
    df = df.dropna(subset=["price", "zestimate", "detailUrl", "address"])
    df["discount_pct"] = 1 - (df["price"] / df["zestimate"])
    return df[df["discount_pct"] >= DISCOUNT_THRESHOLD].sort_values("discount_pct", ascending=False)

# --- Send email digest ---
def send_email(df):
    if df.empty:
        return
    rows = df.to_dict("records")
    body = "<h3>Real Estate Deals—25%+ Below Market</h3><ul>"
    for r in rows:
        pct = round(r["discount_pct"] * 100)
        body += f"<li><a href='{r['detailUrl']}'>{r['address']}</a>: ${r['price']} (~{pct}% below market)</li>"
    body += "</ul>"
    msg = Mail(
        from_email=ALERT_EMAIL_FROM,
        to_emails=ALERT_EMAIL_TO,
        subject="🏠 New Real Estate Deals Alert",
        html_content=body
    )
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(msg)

# --- Streamlit UI ---
def main():
    st.title("🏠 Real-Time Zillow Deal Finder")
    st.caption(f"Last checked: {datetime.now():%Y-%m-%d %H:%M:%S}")

    df = fetch_zillow_data()
    if df.empty:
        st.error("No data received.")
        return

    deals = filter_deals(df)
    st.success(f"Found {len(deals)} deals ≥ {int(DISCOUNT_THRESHOLD*100)}% below market")

    st.dataframe(deals[["address", "price", "zestimate", "discount_pct", "daysOnZillow", "detailUrl"]])

    # Trigger one-time email send
    if st.button("Send Now"):
        send_email(deals)
        st.info("Email sent!")

if __name__ == "__main__":
    main()
