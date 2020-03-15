
from sympy import *
import re
import matplotlib.pyplot as plt
import numpy as np


import data_analyze
big_outbreaks = 100
data = data_analyze.my_aggregate_smoothlog

def instate(value):
    cumlsum = 0
    comparator = 1.0
    while value >= comparator:
        cumlsum += 1
        comparator *= 2
    return cumlsum





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
    for index in range(301):
        shortlist = []
        for subind in range(size+1):
            shortlist.append(subind*index/100)
        matchdat = matchscore(thislist,shortlist)
        newfuture = shortlist[-1] + matchdat[1]
        ratejump = newfuture - thislist[-1] - (thislist[-1] - thislist[0])/len(thislist)
        if (matchdat[0] < score) and (newfuture >= thislist[-1]) and (ratejump < 0.0):
            score = matchdat[0]
            future = newfuture
    linear_future = future
    #return future
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
                        ratejump = newfuture - thislist[-1] - (thislist[-1] - thislist[0])/len(thislist)
                        if (matchdat[0] < score) and (newfuture >= thislist[-1]) and (ratejump < 1.0):
                            score = matchdat[0]
                            future = newfuture
                        elif (matchdat[0] < score) and (newfuture >=thislist[-1]) and ((future is not None) and (newfuture <= future)):
                            score = matchdat[0]
                            future = newfuture
    if (score > 4.0):
        return None
    if future is not None and linear_future is not None:
        future = 0.10 * future + 0.90 * linear_future
    return future

notable_labels = []
for place in data_analyze.my_aggregate_data:
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
    growth.append([exp(data[key][-5]) - exp(data[key][-8]),key])
growth.sort(reverse=True)

report = '7-Day COVID-19 Forecast: ' + data['date'][-1] + '\n'
report += 'Biggest Anticipated Increases' + '\n'

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
    report += lockey #+ ' ' + '%7d' % begin_no + ' +' + '%7d' % (end_no - begin_no) + ' -> ' + '%7d' % end_no + '\n'
    #report += ' ' * 18
    for futureindex in range(-8,0):
        report += '%7d' % int(exp(shorter_dict[mykey][futureindex]))
    report += '\n' + ' ' * 17
    for futureindex in range(-8,0):
        report += '%+7d' % int(exp(shorter_dict[mykey][futureindex]) - exp(shorter_dict[mykey][futureindex-1]))
    report += '\n'

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
