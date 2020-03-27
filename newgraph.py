import ast,math
from sympy import *
import re
import matplotlib.pyplot as plt
import numpy as np
import urllib.request, urllib.error, urllib.parse

oneovere = 0.36787944117
threshold = 0.2

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
    return [slope,itp,oscillation]


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
        for index in range(predict):
            beginat = sequence[-1]
            if len(results) > 0:
                beginat = results[-1]
            results.append(beginat + math.exp(data[0]*(index+predict)+data[1]+scenarios[case])-oneovere)
        all[case] = results
    return all

def produce(sequence,tolerance,*,image_name='default.png',title='Default',date=''):
    fig = plt.figure(figsize=(8,8))
    time = []
    magnitude = []
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
    plt.plot(time,magnitude,"b",zorder=10)
    if predict > 0:
        plt.fill(ranget,rangeh,"gray",zorder=5)
    plt.title(date + ' ' + title + ' ' + str(predict) + '-Day Prediction')
    fig.tight_layout(pad=2.0)
    plt.yscale('log')
    fig.savefig(image_name)

    outstring = date + ' ' + title + ' ' + str(predict) + '-Day Prediction\n'
    if predict > 0:
        for values in [rangel,rangem,rangeh]:
            for index in range(predict+1):
                outstring += '% 8i' % int(values[index] + 0.4999) + ' '
            outstring += '\n'
    return outstring


url = 'https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/total-cases-onset.json'
response = urllib.request.urlopen(url)
webbytes = response.read()
url_content = webbytes.decode('utf-8')

#raw_in = ast.literal_eval(open('archiveNYT/recent.py','r').read())
#sequence = raw_in['United States']
#del sequence[-1]

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

result = produce(timeseries,0.25,image_name='USA.png',title='United States',date=dates[-1])

with open('daily_update.txt','r') as file:
    oldcontents = file.read()
    file.close()

with open('daily_update.txt','w') as file:
    file.write(result + '=' * 80 + '\n' + oldcontents)
    file.close()
