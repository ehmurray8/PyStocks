import http.client
import json
import pandas as pd
import collections
import pickle 
conn = http.client.HTTPSConnection("www.alphavantage.co")

entries = pd.read_csv("stockinfo.csv", skip_blank_lines=True)

#conn.request("GET", "/query?function=TIME_SERIES_DAILY&symbol={}&outputsize=full&apikey=UDPSK0CEP622JWE9".format("MSFT")) 
all_stocks = []
for symbol in entries['Symbol']:
    conn.request("GET", "/query?function=TIME_SERIES_DAILY&symbol={}&outputsize=full&apikey=UDPSK0CEP622JWE9".format(symbol)) 
    res = conn.getresponse()
    data = res.read()

    obj = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(data.decode("utf-8"))

    stock = []
    try:
        for x in obj["Time Series (Daily)"].items():
            stock.append(x[1]["1. open"])
            stock.append(x[1]["2. high"])
            stock.append(x[1]["3. low"])
            stock.append(x[1]["4. close"])
            stock.append(x[1]["5. volume"])
    except KeyError:
        all_stocks.append(stock)
    print(symbol)

with open("all_stocks.pickle", "wb") as f:
    pickle.dump(all_stocks, f)
