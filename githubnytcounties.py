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

if __name__ == '__main__':
    import newgraph

    stateslist = '../covid-19-data/us-states.csv'
    with open(stateslist,"r") as file:
        rawdata = file.read()
        file.close()

    CSV = textmanip.csv_parse(rawdata)

    states_sorted = {}
    states_days = []
    for index,item in enumerate(CSV):
        if index > 0:
            if item[2] not in states_sorted:
                states_sorted[item[2]] ={}
            states_sorted[item[2]][item[0]] = int(item[3])
            if item[0] not in states_days:
                states_days.append(item[0])

    states_days.sort()

    state_timeseries = {}

    for item in states_sorted:
        tseries = [0]
        for day in states_days:
            if day in states_sorted[item]:
                tseries.append(states_sorted[item][day])
            else:
                tseries.append(tseries[-1])
        state_timeseries[item] = tseries

    interest = ['53','06','42','36','29']
    name     = ['Washington','California','Pennsylvania','New York','Missouri']
    for index in range(len(interest)):
        timeseries = state_timeseries[interest[index]]
        newgraph.produce(timeseries,days=5,image_name='states' + interest[index]  + '.png',title=name[index],date=states_days[-1],smooth=True)
