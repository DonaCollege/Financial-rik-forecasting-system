import yfinance as yf  # getting the source stock data (looking for premium alternatives)
import matplotlib.pyplot as plt  #to visualize stock data
import argparse # handling cli arguments (thinking of adding feature to let users specify ticker and period)

def fetch_stock_data(ticker, period):  #defining the arguments (discuss with malhar, what more variables are needed)
    stock = yf.Ticker(ticker) 
    data = stock.history(period=period)
    return data

def plot_price(data, ticker):
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data["Close"])
    plt.title(f"{ticker} Closing Price")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Stock Price Visualizer")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--period", type=str, default="1y", help="Time period (e.g., 1mo, 3mo, 1y, 5y)")

    args = parser.parse_args()

    data = fetch_stock_data(args.ticker, args.period)
    plot_price(data, args.ticker)

if __name__ == "__main__":
    main()