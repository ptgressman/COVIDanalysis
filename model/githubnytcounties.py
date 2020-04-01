import textmanip
import re

nycounties = ['36005','36081','36047','36061','36085']
nycrel     = [1.4,2.5,1.6,2.2,0.5]


CSVlocation = "../../covid-19-data/us-counties.csv"

with open(CSVlocation,"r") as file:
    rawdata = file.read()
    file.close()

CSV = textmanip.csv_parse(rawdata)

counties_sorted = {}
days = []
for index,item in enumerate(CSV):
    if index > 0:
        if item[3] != '':
            if item[3] not in counties_sorted:
                counties_sorted[item[3]] ={}
            counties_sorted[item[3]][item[0]] = int(item[4])
            if item[0] not in days:
                days.append(item[0])
        else:
            if item[1] == 'New York City':
                for ind2,code in enumerate(nycounties):
                    if code not in counties_sorted:
                        counties_sorted[code] = {}
                    counties_sorted[code][item[0]] = int(int(item[4])*nycrel[ind2]/sum(nycrel))

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
