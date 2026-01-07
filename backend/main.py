from fastapi import FastAPI, HTTPException
from VaR import historical_var, parametric_var
from data import get_price_data
from volatility import compute_daily_returns, forecast_volatility
from schemas import VolatilityResponse

app = FastAPI(title="Financial Risk API")


@app.get("/")
def root():
    return {"status": "Backend is running"}


@app.get("/prices")
def get_prices(ticker: str, period: str):
    data = get_price_data(ticker, period)
    data = data.reset_index()
    data["Date"] = data["Date"].astype(str)
    return data.to_dict(orient="records")


def risk_label(vol):
    if vol < 0.2:
        return "Low"
    elif vol < 0.4:
        return "Medium"
    else:
        return "High"


@app.get("/volatility", response_model=VolatilityResponse)
def get_volatility(ticker: str, period: str = "1y"):
    data = get_price_data(ticker, period)
    returns = compute_daily_returns(data)
    vol = forecast_volatility(returns)

    return VolatilityResponse(
        ticker=ticker,
        period=period,
        forecasted_volatility=round(vol, 4),
        risk_level=risk_label(vol),
    )


@app.get("/var")
def get_var(ticker: str, period: str = "1y", confidence: float = 0.95):
    if not 0.9 <= confidence <= 0.999:
        raise HTTPException(
            status_code=400,
            detail="Confidence must be between 0.9 and 0.999",
        )

    data = get_price_data(ticker, period)
    returns = data["Close"].pct_change().dropna()

    return {
        "ticker": ticker,
        "confidence": confidence,
        "historical_var": round(historical_var(returns, confidence), 4),
        "parametric_var": round(parametric_var(returns, confidence), 4),
    }
    