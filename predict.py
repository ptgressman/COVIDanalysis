
from sympy import *
import re
import matplotlib.pyplot as plt
import numpy as np


import data_analyze
big_outbreaks = 200
data = data_analyze.data

def instate(value):
    cumlsum = 0
    comparator = 1.0
    while value >= comparator:
        cumlsum += 1
        comparator *= 2
    return cumlsum


transitions = []
for item in data.keys():
    if re.search('County',item):
        currentstate = 0
        total = 0
        prevtotal = 0
        for value in data[item]:
            thisstate = instate(value)
            if (thisstate != currentstate) :
                if currentstate != 0 and currentstate <= 7:
                    if currentstate == 1:
                        prevtotal = 0
                    transitions.append([currentstate,total,prevtotal])
                currentstate = thisstate
                prevtotal = total
                total = 1
            else:
                total += 1

print('US County Transition Times')

for stateno in range(1,8):
    durations = []
    numer = 0
    denom = 0
    for item in transitions:
        if item[0] == stateno:
            numer += item[1]
            denom += 1
            durations.append(item[1])
    if len(durations) > 0:
        durations.sort()
        average = numer/denom
        median = durations[int(len(durations)/2)]
        print(2**(stateno-1),'-',2**stateno-1,'cases',median,'(med)',int(average+0.5),'(avg)',denom,'(# counties)')



for item in data.keys():
    if item != 'date':
        size = len(data[item])
        for index in range(size):
            if data[item][index] > 0:
                data[item][index] = ln(data[item][index])
            else:
                data[item][index] = -999999


def matchscore(list1,list2):
    sum = 0.0
    dotp = 0.0
    for index in range(len(list1)):
        sum += (list1[index] - list2[index])**2
        dotp += (list1[index] - list2[index])
    return [sum*len(list1) - (dotp * dotp),dotp / len(list1)]

def find_analogue(thislist,datadict,neededspace=1):
    score = 999999.0
    future = None
    size = len(thislist)
    history = len(datadict['date'])
    for index in range(size):
        if (thislist[index] < -100):
            return None
    for key in datadict:
        if (key != 'date'):
            for index in range(history):
                if index + size + neededspace < history:
                    shortlist = datadict[key][index:index+size+1]
                    valid = True
                    for locindex in range(size):
                        if shortlist[locindex] < -100:
                            valid = False
                    if valid:
                        matchdat = matchscore(thislist,shortlist)
                        newfuture = shortlist[-1] + matchdat[1]
                        if (matchdat[0] < score) and (newfuture >= thislist[-1]):
                            score = matchdat[0]
                            future = newfuture
    if (score > 4.0):
        return None
    return future

notable_labels = []
for place in data_analyze.big_labels:
    if place != 'date':
        print(place + ' ',end='',flush=True)
        stopped = False
        reference = data[place][-1]
        if reference < ln(big_outbreaks):
            stopped = True          #Too Few Cases To Forecast
        for loop in range(7):
            shortlist = data[place][len(data[place])-5:len(data[place])]
            if not stopped:
                outcome = find_analogue(shortlist,data,3)
                if outcome != None:
                    print(exp(outcome),end=', ',flush=True)
                    data[place].append(outcome)
                else:
                    stopped = True
        if not stopped:
            notable_labels.append(place)
        print('')

with open('predict.csv','w') as file:
    file.write('Locale,')
    datelist = data['date']
    for index,date in enumerate(datelist):
        file.write(date)
        if index < len(datelist)-1:
            file.write(',')
        else:
            file.write('\n')
    for locale in data.keys():
        if (locale != 'date'):
            file.write('"' + locale + '",')
            predlist = data[locale]
            for index,popn in enumerate(predlist):
                if (popn > -10):
                    outstr = str(exp(popn))
                else:
                    outstr = ''
                file.write(outstr)
                if index < len(predlist)-1:
                    file.write(',')
                else:
                    file.write('\n')

shorter_dict = {}
growth = []
for key in notable_labels:
    shorter_dict[key] = data[key]
    growth.append([exp(data[key][-1]) - exp(data[key][-8]),key])
growth.sort(reverse=True)

report = '7-Day COVID-19 Forecast: ' + data['date'][-1] + '\n'
report += 'Top Ten Largest Anticipated Increases' + '\n'

toplot = []
for index in range(10):
    lockey = growth[index][1]
    mykey = lockey
    begin_no = int(exp(shorter_dict[mykey][-8]))
    end_no =  int(exp(shorter_dict[mykey][-1]))
    if (end_no >= 2 * begin_no):
        lockey += '**'
    if (end_no >= 3 * begin_no):
        lockey += '*'
    if (end_no >= 4 * begin_no):
        lockey += '*'
    lockey = (lockey + ' ' * 17)[:17]
    toplot.append(mykey)
    report += lockey + ' ' + '%7d' % begin_no + ' +' + '%7d' % (end_no - begin_no) + ' -> ' + '%7d' % end_no + '\n'

print(report)


fig, axs = plt.subplots(5,2,sharex=True,sharey=True,figsize=(10,16))

count = -1
xmin = 99999.0
xmax = -1.0
ymin = 99999.0
ymax = -1.0
for key in toplot:
    x = []
    y = []
    baseline = data[key][-8]
    count += 1
    for index,value in enumerate(data[key]):
        if (value > -1):
            newval = exp(value)
            x.append(index-len(data[key])+8)
            y.append(newval)
            if index < xmin:
                xmin = index
            if index > xmax:
                xmax = index
            if newval < ymin:
                ymin = value
            if newval > ymax:
                ymax = value
        axs[int(count/2),count%2].plot(x,y)
        axs[int(count/2),count%2].set_title(key)


fig.tight_layout(pad=2.0)
plt.yscale('log')
fig.savefig('topten.png')
