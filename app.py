import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import requests
import pandas as pd
import numpy as np

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Financial Risk Dashboard", layout="wide")
st.title("Financial Risk Forecasting System")

STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "Meta": "META"
}

company = st.selectbox("Select a stock", list(STOCKS.keys()))
ticker = STOCKS[company]
period = st.text_input("Time period", "1y")

confidence = st.slider(
    "Confidence Level",
    min_value=0.90,
    max_value=0.99,
    value=0.95,
    step=0.01
)
var_res = requests.get(
    "http://127.0.0.1:8000/var",
    params={
        "ticker": ticker,
        "period": period,
        "confidence": confidence
    }
)

if var_res.status_code != 200:
    st.error("Failed to fetch VaR data")
    st.stop()

var_data = var_res.json()


prices_res = requests.get(f"{BASE_URL}/prices", params={"ticker": ticker, "period": period})
vol_res = requests.get(f"{BASE_URL}/volatility", params={"ticker": ticker, "period": period})

var_res = requests.get(
    f"{BASE_URL}/var",
    params={
        "ticker": ticker,
        "period": period,
        "confidence": confidence
    }
)


if prices_res.status_code != 200 or vol_res.status_code != 200:
    st.error("Backend error")
    st.stop()

prices = pd.DataFrame(prices_res.json())
prices["Date"] = pd.to_datetime(prices["Date"])

vol = vol_res.json()

st.metric(
    "Forecasted Volatility",
    f"{vol['forecasted_volatility']:.2%}",
    f"Risk: {vol['risk_level']}"
)

st.subheader(" Value at Risk (VaR)")

v1, v2 = st.columns(2)

v1.metric(
    "Historical VaR",
    f"{var_data['historical_var']:.2%}"
)

v2.metric(
    "Parametric VaR",
    f"{var_data['parametric_var']:.2%}"
)


prices["Returns"] = prices["Close"].pct_change()
rolling_vol = prices["Returns"].rolling(30).std() * np.sqrt(252)
returns = prices["Returns"].dropna()



price_fig = go.Figure()
st.title(f"{company} ({ticker}) Price ")
price_fig.add_trace(go.Scatter(x=prices["Date"], y=prices["Close"], mode="lines"))
st.plotly_chart(price_fig, use_container_width=True)

vol_fig = go.Figure()
st.title(f"{company} ({ticker}) Rolling Volatility (30 days)")
vol_fig.add_trace(go.Scatter(x=prices["Date"], y=rolling_vol, mode="lines"))
st.plotly_chart(vol_fig, use_container_width=True)


hist_fig = px.histogram(
    returns,
    nbins=50,
    title="Return Distribution",
    labels={"value": "Daily Returns"}
)

hist_fig.add_vline(
    x=var_data["historical_var"],
    line_dash="dash",
    line_color="red",
    annotation_text="Historical VaR",
    annotation_position="top left"
)

hist_fig.add_vline(
    x=var_data["parametric_var"],
    line_dash="dash",
    line_color="orange",
    annotation_text="Parametric VaR",
    annotation_position="top right"
)
st.plotly_chart(hist_fig, use_container_width=True)
