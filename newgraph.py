import ast,math
from sympy import *
import re
import matplotlib.pyplot as plt
import numpy as np
import data_tools

prediction_frontier = 5

oneovere = 0.36787944117

def delta(valuelist,minimum=0):
    result = []
    previous = None
    for item in valuelist:
        if previous is not None:
            delta = max(item-previous,minimum)
            result.append(delta)
        previous = item
    return result

def best_uniform_line(valuelist):
    oscillation = None
    for index1 in range(len(valuelist)):
        for index2 in range(index1+2,len(valuelist)):
            slope = (valuelist[index2] - valuelist[index1]) / (index2 - index1)
            minitp = None
            maxitp = None
            for index3 in range(len(valuelist)):
                itp = valuelist[index3] - slope * index3
                if minitp is None or itp < minitp:
                    minitp = itp
                if maxitp is None or itp > maxitp:
                    maxitp = itp
            osc = maxitp - minitp
            if oscillation is None or osc < oscillation:
                found_slope = slope
                found_itp   = (maxitp + minitp) * 0.5
                oscillation = osc
    return [found_slope,found_itp,oscillation*0.5]


def extrapolate(sequence,tolerance):
    if len(sequence) < 3:
        return {'low' : [], 'medium' : [], 'high' : []}
    def log_delta_capture(sequence,number):
        result = []
        for index in range(len(sequence)-number,len(sequence)):
            result.append(math.log(oneovere + sequence[index] - sequence[index-1]))
        return result
    frozen = False
    data = None
    predict = 0
    for length in range(3,len(sequence)):
        if not frozen:
            mydata = best_uniform_line(log_delta_capture(sequence,length))
            if mydata[-1] <= tolerance:
                data = mydata
                predict = length
            else:
                frozen = True
    if predict == 0:
        return {'low' : [], 'medium' : [], 'high' : []}
    scenarios = {'low' : -data[2], 'medium' : 0, 'high' : data[2]}
    all = {}
    for case in scenarios:
        results = []
        deltas = []
        for index in range(predict):
            beginat = sequence[-1]
            if len(results) > 0:
                beginat = results[-1]
            thisdelta = math.exp(data[0]*(index+predict)+data[1]+scenarios[case])-oneovere
            results.append(beginat + max(thisdelta,0))
        for index in range(-predict,predict):
            thisdelta = math.exp(data[0]*(index+predict)+data[1]+scenarios[case])-oneovere
            deltas.append(thisdelta)
        all[case] = results
        all[case+'deltas'] = deltas
    return all

def produce(sequence,*,tolerance=0.1,days=0,image_name='default.png',title='Default',date='',**kwargs):
    smoothing = False
    if 'smooth' in kwargs and kwargs['smooth'] == True:
        smoothing = True
        logseq = []
        previtem = 0
        oldseq = []
        for item in sequence:
            oldseq.append(item)
            logseq.append(math.log(oneovere + item - previtem))
            previtem = item # This smooths increments
            previtem = 0 # This smooths cumulative total
        logseq = data_tools.smooth_it(logseq,tolerance*0.25,1e-12)
        sequence = []
        prevtotal = 0
        for item in logseq:
            prevtotal += max(0,math.exp(item) - oneovere)
            sequence.append(prevtotal)
            prevtotal = 0 # This smooths cumulative total
        for index in range(len(sequence)):
            sequence[index] = int(sequence[index]+0.4999)
    if days > 0:
        tolerance = 0.05
        predicted = 0
        while predicted < prediction_frontier:
            tolerance += 0.05
            predicted = len(extrapolate(sequence,tolerance)['medium'])
    fig = plt.figure(figsize=(8,8))
    time = []
    magnitude = []
    outstring = ''
    moetext = ''
    for index in range(len(sequence)):
        time.append(index+1-len(sequence))
        magnitude.append(sequence[index])
    scenarios = extrapolate(sequence,tolerance)
    ranget = [time[-1]]
    rangeh = [sequence[-1]]
    rangem = [sequence[-1]]
    rangel = [sequence[-1]]
    predict = len(scenarios['medium'])
    for index,item in enumerate(scenarios['medium']):
        time.append(time[-1]+1)
        magnitude.append(item)
        ranget.append(ranget[-1]+1)
        rangeh.append(scenarios['high'][index])
        rangem.append(item)
        rangel.append(scenarios['low'][index])

    for index in range(predict+1):
        ranget.append(ranget[predict-index])
        rangeh.append(rangel[predict-index])
    plt.plot(time,magnitude,"b",zorder=10,label='Total Confirmed Cases')
    plt.plot(range(-len(sequence)+2,1),delta(sequence,0.75),"g",label='New Daily Cases')
    if smoothing is True:
        sequence = oldseq
#        plt.plot(range(-len(sequence)+1,1),sequence,"b",dashes=[6,2],zorder=10,label='Raw Total')
        plt.plot(range(-len(sequence)+2,1),delta(sequence,0.75),"g",dashes=[6,2],label='Raw Daily Cases')

    if predict > 0:
        plt.fill(ranget,rangeh,"gray",zorder=5)
        future = range(-predict+1,predict+1)
        plt.plot(future,scenarios['lowdeltas'],"gray",zorder=5)
        plt.plot(future,scenarios['highdeltas'],"gray",zorder=5)
#        plt.plot(future,scenarios['mediumdeltas'],"gray",zorder=5)

        factor = scenarios['highdeltas'][0] / scenarios['mediumdeltas'][0]
        factor = int((factor - 1)*100+0.49999)
        moetext = r'$\pm$'+str(factor)+'% margin of error in daily cases'
        #plt.text(-3,1,moe,horizontalalignment='center')
#    plt.title(date + ' ' + title + ' ' + str(predict) + '-Day COVID-19 Trend Extrapolation')
    fig.tight_layout(pad=2.0)
    plt.yscale('log')

    outstring = '   ' + date + ' ' + title + ' ' + str(predict) + '-Day COVID-19 Trend Extrapolation\n'
    if predict > 0:
        label = ['low ','mid ','hi  ']
        for posn, values in enumerate([rangel,rangem,rangeh]):
            outstring += label[posn]
            for index in range(predict+1):
                outstring += '% 8i' % int(values[index] + 0.4999) + ' '
            outstring += '\n'

    plt.text(-len(sequence),sequence[-1],outstring+moetext,va='top',fontdict={'family' : 'monospace','size' : 'small'})
    plt.legend(loc='lower right')
    fig.savefig(image_name)
    plt.clf()
    plt.close()
    return outstring


#url = 'https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/total-cases-onset.json'
#response = urllib.request.urlopen(url)
#webbytes = response.read()
#url_content = webbytes.decode('utf-8')

#raw_in = ast.literal_eval(open('archiveNYT/recent.py','r').read())
#sequence = raw_in['United States']
#del sequence[-1]


import urllib.request, urllib.error, urllib.parse
import urldailyarchive

def get_EUCDC():
    request = { 'url' : 'https://opendata.ecdc.europa.eu/covid19/casedistribution/json/',
    'archive' : 'archiveEUCDC/', 'checktimes' : [0,1,2,3], 'extension' : '.json'}
    url_content = urldailyarchive.get_asset(request)

    object = ast.literal_eval(url_content)
    reports = object['records']
    by_geoId = {}
    for record in reports:
        converted = {}
        for field in record:
            if field in ['day','month','year','cases','deaths']:
                try:
                    converted[field] = int(record[field])
                except:
                    converted[field] = record[field]
        if record['geoId'] not in by_geoId:
            by_geoId[record['geoId']] = {
            'countryterritoryCode' : record['countryterritoryCode'],
            'countriesAndTerritories' : record['countriesAndTerritories'],
            'popData2018' : record['popData2018'],
            'data' : []
            }
        by_geoId[record['geoId']]['data'].append(converted)
    return by_geoId

def get_cases(EUCDCdata,geoId):
    records = []
    for item in EUCDCdata[geoId]['data']:
        records.append([item['year'],item['month'],item['day'],item['cases']])
    records.sort()
    result = []
    for index in range(len(records)):
        if index > 0:
            records[index][-1] = records[index][-1] + records[index-1][-1]
        result.append(records[index][-1])
    return {
    'date' : str(records[-1][0]) + '/' + str(records[-1][1]) + '/' + str(records[-1][2]),
    'name' : re.sub('_',' ',EUCDCdata[geoId]['countriesAndTerritories']),
    'ctc' : EUCDCdata[geoId]['countryterritoryCode'],
    'timeseries' : result
    }

if __name__ == '__main__':
    raw_data = get_EUCDC()
    for item in raw_data:
        identifier = item + ' ' + raw_data[item]['countriesAndTerritories'] + ' ' * 20
        identifier = identifier[0:18]
        print(identifier,' ', end='')
    print()

    monitor = ['US','CA','MX','CN','KR','IT','ES','FR','DE','UK','AU','SA']
    monitor.reverse()
    for country in monitor:
        datapack = get_cases(raw_data,country)
        filename = 'archiveEUCDC/' + datapack['ctc'] + '.png'
        result = produce(datapack['timeseries'],days=5,image_name=filename,title=datapack['name'],date=datapack['date'],smooth=True)

        with open('daily_update.txt','r') as file:
            oldcontents = file.read()
            file.close()

        with open('daily_update.txt','w') as file:
            file.write(result + '=' * 80 + '\n' + oldcontents)
            file.close()
    quit()

if __name__ == '__main__':

    request = { 'url' : 'https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/total-cases-onset.json',
    'archive' : 'archiveCDC/cases', 'checktimes' : [0,1,2,3], 'extension' : '.json'}
    url_content = urldailyarchive.get_asset(request)

    url_content = re.sub('null','None',url_content)
    url_content = re.sub('false','False',url_content)
    url_content = re.sub('true','True',url_content)


    raw_in = ast.literal_eval(url_content)
    raw_in = raw_in['data']['columns']

    dates = raw_in[0]
    del dates[0]
    timeseries = []
    for index in range(len(raw_in[1])):
        if index > 0:
            timeseries.append(int(raw_in[1][index]))

    result = produce(timeseries,days=5,image_name='USA.png',title='United States',date=dates[-1])

    with open('daily_update.txt','r') as file:
        oldcontents = file.read()
        file.close()

    with open('daily_update.txt','w') as file:
        file.write(result + '=' * 80 + '\n' + oldcontents)
        file.close()
