"""Testing financial analysis using Udacity ML Finance course."""

# pylint:disable=import-error, superfluous-parens
import os
import json
import math
import http.client
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as spo
from alpha_key import API_KEY


RF_RATE = 0


def get_pickle_path(symbol):
    """Returns the path of where the pickled dataframe should be stored."""
    return os.path.join("stock_pickles", "{}.pickle".format(symbol))


def pickle_stock_data(all_stocks, col_names):
    """Pickles data from alpha vantage using dataframes for the specified stocks."""
    conn = http.client.HTTPSConnection("www.alphavantage.co")
    num_conns = 0
    for symbol in all_stocks:
        done = False
        while num_conns < 3 and not done:
            try:
                conn.request("GET",
                             "/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&outputsize=full&apikey={}"
                             .format(symbol, API_KEY))
                res = conn.getresponse()
                data = res.read()
                data = json.loads(data.decode("utf-8"))
            except (http.client.RemoteDisconnected, json.decoder.JSONDecodeError):
                conn = http.client.HTTPSConnection("www.alphavantage.co")
                num_conns += 1
                continue

            data = data["Time Series (Daily)"]

            stock_df = pd.DataFrame.from_dict(data, "index")
            stock_df.rename(columns=col_names, inplace=True)
            stock_df.to_pickle(get_pickle_path(symbol))
            print(symbol)
            done = True


def create_main_df(all_stocks, start, end):
    """Creates the main_df using specified dates, and adjusted closes for specified stocks."""
    dates = pd.date_range(start, end)
    main_df = pd.DataFrame(index=dates)
    for symbol in all_stocks:
        temp_df = pd.read_pickle(get_pickle_path(symbol))
        temp_df.rename(columns={"Adj. Close": symbol}, inplace=True)
        main_df = main_df.join(temp_df[symbol])

    main_df.dropna(how="all", inplace=True)
    main_df.fillna(method="ffill", inplace=True)
    main_df.fillna(method="backfill", inplace=True)
    main_df = main_df.astype(float)
    return main_df


def plot_main(main_df):
    """Plots the main_df."""
    main_df.plot(title="Plot of Main Data Frame")
    plt.xlabel("Time (day)")
    plt.ylabel("Price ($)")
    plt.show()


def plot_bollinger_bands(main_df, symbol, window):
    """Plots the bollinger bands for a specified stock."""
    rmean = main_df[symbol].rolling(center=False, window=window).mean()
    rstddev = main_df[symbol].rolling(center=False, window=window).std()

    upper_band, lower_band = get_bollinger_bands(rmean, rstddev)

    ax1 = main_df[symbol].plot(title="Bollinger Bands {}".format(symbol), label=symbol)
    rmean.plot(label='Rolling mean', ax=ax1)
    upper_band.plot(label='upper band', ax=ax1)
    lower_band.plot(label='lower band', ax=ax1)
    ax1.legend(loc='upper left')

    plt.show()


def compute_daily_returns(main_df):
    """Compute and return the daily return values."""
    returns = (main_df / main_df.shift(1)) - 1
    returns.ix[0, :] = 0
    return returns


def compute_cumulative_rets(main_df):
    """Compute and return the cumulative return values."""
    returns = (main_df.ix[-1, :] / main_df.ix[0, :]) - 1
    return returns


def get_bollinger_bands(rmean, rstd):
    """Return upper and lower Bollinger Bands."""
    upper_band = 2 * rstd + rmean
    lower_band = -2 * rstd + rmean
    return upper_band, lower_band


def create_daily_rets_hist(daily_rets, symbol):
    """Creates a histogram for the daily returns."""
    daily_rets[symbol].hist(bins=20)

    mean = daily_rets[symbol].mean()
    stddev = daily_rets[symbol].std()

    plt.axvline(x=mean, color='w', linestyle='dashed', linewidth=2)
    plt.axvline(x=stddev, color='r', linestyle='dashed', linewidth=2)
    plt.axvline(x=-stddev, color='r', linestyle='dashed', linewidth=2)
    plt.title("Daily returns histogram for {}".format(symbol))
    plt.show()


def compare_scatter(daily_rets, sym1, sym2):
    """Creates a scatter plot to compare two stocks."""
    daily_rets.plot(kind='scatter', x=sym1, y=sym2)
    beta2, alpha2 = np.polyfit(daily_rets[sym1], daily_rets[sym2], 1)
    plt.plot(daily_rets[sym1], beta2 *
             daily_rets[sym1] + alpha2, '-', color='r')
    plt.title("{} vs. {}".format(sym1, sym2)) 
    plt.show()


def calculate_sharpe_ratio(daily_returns, rf_rate):
    """Calculates the sharpe ratios for the stocks."""
    #mean_daily_rets = daily_returns.mean()
    daily_rets_offset = (daily_returns - rf_rate).mean()
    risk = daily_returns.std()
    sharpe_ratio = math.sqrt(252) * (daily_rets_offset / risk)
    return sharpe_ratio


def total_sharpe(splits, daily_rets, rf_rate):
    """Calculates the opposite of the total sharpe ratio."""
    return -1 * (splits * calculate_sharpe_ratio(daily_rets, rf_rate)).sum()


def maximize_sharpe(splits, daily_rets, total_sharpe_func, rf_rate):
    """Maximize sharpe ratio."""
    bounds = [(0, 1)] * len(daily_rets.columns)
    print(bounds)
    cons = ({'type': 'eq', 'fun': lambda x: x.sum() - 1})
    result = spo.minimize(total_sharpe_func, splits, args=(daily_rets, rf_rate), method='SLSQP',
                          options={'disp': True}, bounds=bounds, constraints=cons)
    return result.x


def optimize_portfolio_sr(daily_rets, rf_rate):
    """Optimizes portfolio using sharpe ratio."""
    print("Original sharpe ratios")
    init_sharpes = calculate_sharpe_ratio(daily_rets, rf_rate)
    print(init_sharpes)

    even_split = 1.0 / float(len(daily_rets.columns))
    starting_splits = [even_split] * len(daily_rets.columns)
    print("Starting sharpe sum")
    print((init_sharpes * starting_splits).sum())
    print("Starting daily returns")
    print((daily_rets * starting_splits).mean().sum())
    print("Starting splits:")
    print(starting_splits)

    final_splits = maximize_sharpe(
        starting_splits, daily_rets, total_sharpe, rf_rate)
    print("Final splits")
    print(final_splits)
    print(final_splits.sum())
    print("Final sharpe sum")
    print((init_sharpes * final_splits).sum())
    print("Final daily returns")
    print((daily_rets * final_splits).mean().sum())


def update_stock_data(stocks):
    """Sets up and gets the proper data from alpha vantage using pickle_stock_data"""
    alpha_vantage_cols = ["1. open", "2. high", "3. low", "4. close",
                          "5. adjusted close", "6. volume", "7. dividend amount",
                          "8. split coefficent"]
    new_col_names = ["Open", "High", "Low", "Close",
                     "Adj. Close", "Volume", "Dividend", "Split Coefficent"]
    col_names = dict(zip(alpha_vantage_cols, new_col_names))
    pickle_stock_data(stocks, col_names)


def main():
    """Main execution of tests currently."""

    # Used for generating the pickled data frames from alpha vantage.
    all_stocks = ["SPY", "UAA", "MSFT", "MU", "V", "ADBE", "AMGN", "SBUX"]
    #every_stock = pd.read_csv("stockinfo.csv", skip_blank_lines=True)["Symbol"].tolist()
    #update_stock_data(all_stocks)

    start = "2000-01-01"
    end = pd.to_datetime('today')

    main_df = create_main_df(all_stocks, start, end)
    # plot_main(main_df)

    # Used to create a graph of bollinger bands for a stock
    window = 20
    plot_bollinger_bands(main_df, "UAA", window)
    daily_returns = compute_daily_returns(main_df)
    print("Kurtosis:")
    print(daily_returns.kurtosis())
    cumulative_rets = compute_cumulative_rets(main_df)

    create_daily_rets_hist(daily_returns, "UAA")

    print("\nPearson correlation:")
    print(daily_returns.corr(method='pearson'))
    compare_scatter(daily_returns, "SPY", "UAA")

    print("\nDaily returns:")
    print(daily_returns.head())
    print("\nCumulative returns:")
    print(cumulative_rets)
    print("\nMean daily returns:")
    print(daily_returns.mean())
    print("\nRisk:")
    print(daily_returns.std())
    sharpe_ratio = calculate_sharpe_ratio(daily_returns, RF_RATE)
    print("\nSharpe ratio")
    print(sharpe_ratio)

    optimize_portfolio_sr(daily_returns, RF_RATE)


if __name__ == "__main__":
    main()
