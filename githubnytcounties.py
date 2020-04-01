import textmanip
import re

CSVlocation = "../covid-19-data/us-counties.csv"

with open(CSVlocation,"r") as file:
    rawdata = file.read()
    file.close()

CSV = textmanip.csv_parse(rawdata)

counties_sorted = {}
days = []
for index,item in enumerate(CSV):
    if index > 0:
        if item[3] not in counties_sorted:
            counties_sorted[item[3]] ={}
        counties_sorted[item[3]][item[0]] = int(item[4])
        if item[0] not in days:
            days.append(item[0])

days.sort()

county_timeseries = {}

for item in counties_sorted:
    tseries = [0]
    for day in days:
        if day in counties_sorted[item]:
            tseries.append(counties_sorted[item][day])
        else:
            tseries.append(tseries[-1])
    county_timeseries[item] = tseries
