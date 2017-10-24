import http.client
import json
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

def get_pickle_path(symbol):
    return os.path.join("stock_pickles", "{}.pickle".format(symbol))

def pickle_stock_data(all_stocks, col_names):
    conn = http.client.HTTPSConnection("www.alphavantage.co")
    for symbol in all_stocks:
        conn.request("GET", "/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&outputsize=full&apikey=UDPSK0CEP622JWE9".format(symbol)) 
        res = conn.getresponse()
        data = res.read()

        data = json.loads(data.decode("utf-8"))
        data = data["Time Series (Daily)"]

        stock_df = pd.DataFrame.from_dict(data, "index")
        stock_df.rename(columns=col_names, inplace=True)
        stock_df.to_pickle(get_pickle_path(symbol))


def create_main_df(all_stocks, start, end):
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
    main_df.plot()
    plt.show()

def plot_bollinger_bands(main_df, symbol, window):
    rmean = main_df[symbol].rolling(center=False, window=window).mean()
    rstddev = main_df[symbol].rolling(center=False, window=window).std()

    upper_band, lower_band = get_bollinger_bands(rmean, rstddev)

    ax = main_df[symbol].plot(title="Bollinger Bands", label=symbol)
    rmean.plot(label='Rolling mean', ax=ax)
    upper_band.plot(label='upper band', ax=ax)
    lower_band.plot(label='lower band', ax=ax)
    ax.legend(loc='upper left')

    plt.show()

def compute_daily_returns(df):
    """Compute and return the daily return values."""
    # Note: Returned DataFrame must have the same number of rows
    returns = (df/df.shift(1)) - 1
    returns.ix[0, :] = 0
    return returns

def compute_cumulative_rets(df):
    returns = (df.ix[-1, :]/df.ix[0, :]) - 1
    return returns

def get_bollinger_bands(rm, rstd):
    """Return upper and lower Bollinger Bands."""
    upper_band = 2 * rstd + rm
    lower_band = -2 * rstd + rm
    return upper_band, lower_band

def create_daily_rets_hist(daily_rets, symbol):
    daily_rets[symbol].hist(bins=20)

    mean = daily_rets[symbol].mean()
    stddev = daily_rets[symbol].std()

    plt.axvline(x=mean, color='w', linestyle='dashed', linewidth=2)
    plt.axvline(x=stddev, color='r', linestyle='dashed', linewidth=2)
    plt.axvline(x=-stddev, color='r', linestyle='dashed', linewidth=2)
    plt.show()

def compare_scatter(daily_rets, sym1, sym2):
    daily_rets.plot(kind='scatter', x=sym1, y=sym2)
    beta2, alpha2 = np.polyfit(daily_rets[sym1], daily_rets[sym2], 1)
    plt.plot(daily_rets[sym1], beta2 * daily_rets[sym1] + alpha2, '-', color='r')
    plt.show()


if __name__ == "__main__":
    every_stock = pd.read_csv("stockinfo.csv", skip_blank_lines=True)["Symbol"].tolist()
    all_stocks = ["SPY", "UAA", "UA", "MSFT", "MU", "V", "ADBE", "AMGN", "SBUX"]
    alpha_vantage_cols = ["1. open", "2. high", "3. low", "4. close", "5. adjusted close", "6. volume", "7. dividend amount", "8. split coefficent"]
    new_col_names = ["Open", "High", "Low", "Close", "Adj. Close", "Volume", "Dividend", "Split Coefficent"]
    col_names = dict(zip(alpha_vantage_cols, new_col_names))
    #pickle_stock_data(all_stocks, col_names)
    #pickle_stock_data(every_stock, col_names)

    start = "2000-01-01"
    end = pandas.to_datetime('today')
    window = 20
    
    main_df = create_main_df(all_stocks, start, end)
    #plot_main(main_df)
    #plot_bollinger_bands(main_df, "MU", window)
    daily_returns = compute_daily_returns(main_df)
    print(daily_returns.kurtosis())
    cumulative_rets = compute_cumulative_rets(main_df)

    #create_daily_rets_hist(daily_returns, "UA")

    print(daily_returns.corr(method='pearson'))
    compare_scatter(daily_returns, "SPY", "MSFT")
