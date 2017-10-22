import http.client
import pandas as pd
from io import StringIO

conn = http.client.HTTPConnection("download.finance.yahoo.com")

headers = {
    'cache-control': "no-cache",
    'postman-token': "c6c3e450-15eb-4d8b-1095-e4abdcb6d51a"
    }

entries = pd.read_csv("stockinfo.csv", skip_blank_lines=True)
count = 0
url_exts = []
url = "/d/quotes.csv?s="
fmt_str = "&f=nspo"
for e in entries['Symbol']:
    url += "%20" + e
    count += 1
    if count == 200:
        url += fmt_str
        url_exts.append(url)
        url = "/d/quotes.csv?s="
        count = 0

if count != 200:
    url += fmt_str
    url_exts.append(url)

for u in url_exts:
    conn.request("GET", u, headers=headers)

    res = conn.getresponse()
    data = res.read()
    
    #print(data.decode("utf-8"))
    d = StringIO(data.decode("utf-8"))
    ret_data = pd.read_csv(d, skip_blank_lines=True)

    print(ret_data)
    print("\n\n")
