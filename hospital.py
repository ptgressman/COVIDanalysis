import csv,ast
import matplotlib.pyplot as plt

url = 'https://healthdata.gov/api/views/anag-cw7u/rows.csv?accessType=DOWNLOAD'
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from urllib.request import urlretrieve
filename = 'COVIDHHS.csv'
urlretrieve(url, filename)

#filename = 'COVID-19_Reported_Patient_Impact_and_Hospital_Capacity_by_Facility.csv'
adult_covid = 'total_adult_patients_hospitalized_confirmed_and_suspected_covid_7_day_avg'
child_covid = 'total_pediatric_patients_hospitalized_confirmed_covid_7_day_avg'
week = 'collection_week'

filedata = open('./census/fipsdata.py','r').read()
codes = ast.literal_eval(filedata)
county_neighborhoods = {0 : ['42045']}
neighborhood_totals = {0 : {}}
max_radius = 6 # Can go up to 12
for radius in range(1,max_radius):
    neighborhood_totals[radius] = {}
    county_neighborhoods[radius] = []
    for code in county_neighborhoods[radius-1]:
        if code not in county_neighborhoods[radius]:
            county_neighborhoods[radius].append(code)
        for code2 in codes[code]['adjacent']:
            if code2 not in county_neighborhoods[radius]:
                county_neighborhoods[radius].append(code2)
population = {}
for radius in county_neighborhoods:
    population[radius] = 0
    for county in county_neighborhoods[radius]:
        population[radius] += codes[county]['pop2019']
capture_fips = {}
for key in county_neighborhoods:
    for fips_code in county_neighborhoods[key]:
        if fips_code not in capture_fips:
            capture_fips[fips_code] = []
        capture_fips[fips_code].append(key)

class CSV(object):
    def __init__(self,filename):
        self.filename = filename
        self.headers = None
        self.numerical = []

    def __iter__(self):
        self.csvfile = open(self.filename,mode='r', encoding='utf-8-sig')
        self.reader = csv.reader(self.csvfile)
        self.headers = None
        self.csviterator = self.reader.__iter__()
        return self
    def __next__(self):
        try:
            if self.headers is None:
                self.headers = self.csviterator.__next__()
                self.columns = len(self.headers)
            cells = self.csviterator.__next__()
            result = {}
            for index,item in enumerate(cells):
                if index < self.columns:
                    field = self.headers[index]
                    if field in self.numerical:
                        try:
                            if item == '':
                                item = '0'
                            item = float(item)
                            if item < 0:
                                item = 2
                        except:
                            pass
                    result[field] = item
            return result
        except:
            raise StopIteration

summarydata = {}
myfile = CSV(filename)
myfile.numerical.append(adult_covid)
myfile.numerical.append(child_covid)
all_dates = {}
for data in myfile:
    if data['fips_code'] in capture_fips:
        obsweek = data[week]
        all_dates[obsweek] = True
        obsadult = data[adult_covid]
        obschild = data[child_covid]
        for level in capture_fips[data['fips_code']]:
            if level not in summarydata:
                summarydata[level] = {}
            if obsweek not in summarydata[level]:
                summarydata[level][obsweek] = 0
            summarydata[level][obsweek] += int(obsadult + obschild+0.8)

all_dates = list(all_dates.keys())
all_dates.sort()
date_index = {}
for index,item in enumerate(all_dates):
    date_index[item] = index

toplot = []
for level in range(max_radius):
    tosort = []
    for key in summarydata[level]:
        tosort.append([key,summarydata[level][key]])
    tosort.sort()
    timetick = []
    values = []
    for date,value in tosort:
        timetick.append(date_index[date])
        values.append(value)
    toplot.append([timetick,values])

fig, ax = plt.subplots(len(toplot),1,figsize=(15,20))
tickno = []
tickl = []
for index in range(len(all_dates)):
         if (index - len(all_dates)+1) % 4 == 0:
             tickno.append(index)
             tickl.append(all_dates[index][5:10])
for index,datapair in enumerate(toplot):
    timeticks,values = datapair
    plt.subplot(ax[index])
    plt.xticks(tickno,tickl)
    ax[index].grid(axis='y',linestyle=':')
    for choice in [3]:
        ax[index].plot(timeticks,values)
        ax[index].set_ylim(bottom=0,top=max(values)*1.05)
fig.savefig('hospital.png',bbox_inches='tight')
