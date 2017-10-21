import pandas as pd


entries = pd.read_csv("stockinfo.csv", skip_blank_lines=True)
print("Symbols\n")
print(entries['Symbol'])
print("Names\n")
print(entries['Name'])
print("Sectors\n")
print(entries['Sector'])
