import http.client

conn = http.client.HTTPConnection("download.finance.yahoo.com")

headers = {
    'cache-control': "no-cache",
    'postman-token': "c6c3e450-15eb-4d8b-1095-e4abdcb6d51a"
    }

conn.request("GET", "/d/quotes.csv?s=ZNWAA%20ZION%20ZIONW%20ZIONZ%20ZIOP%20ZIXI%20ZGNX%20ZSAN%20ZUMZ%20ZYNE%20ZNGA%0A&f=nspomkjm3m4va5b6a2", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
