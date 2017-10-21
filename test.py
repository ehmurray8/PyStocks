import http.client
import pandas as pd

conn = http.client.HTTPConnection("download.finance.yahoo.com")

headers = {
    'cache-control': "no-cache",
    'postman-token': "c6c3e450-15eb-4d8b-1095-e4abdcb6d51a"
    }


entries = pd.read_csv("stockinfo.csv", skip_blank_lines=True)
count = 0
url_exts = []
url = "/d/quotes.csv?s="
for e in entries['Symbol']:
    url += "%20" + e
    count += 1
    if count == 200:
        url += "&f=nspomkjm3m4va5b6a2"
        url_exts.append(url)
        url = "/d/quotes.csv?s="
        count = 0

if count != 200:
    url += "&f=nspomkjm3m4va5b6a2"
    url_exts.append(url)

for u in url_exts:
    #conn.request("GET", "/d/quotes.csv?s=ZNWAA%20ZION%20ZIONW%20ZIONZ%20ZIOP%20ZIXI%20ZGNX%20ZSAN%20ZUMZ%20ZYNE%20ZNGA%0A&f=nspomkjm3m4va5b6a2", headers=headers)
    conn.request("GET", u, headers=headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))
    print("\n\n")
