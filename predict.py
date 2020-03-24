
from sympy import *
import re
import matplotlib.pyplot as plt
import numpy as np

backlog = 0

def polyfit(snippet,degree):
    size = len(snippet)
    basis = []
    my_sample = []
    for index in range(size+1):
        my_sample.append(0.0)
    for index in range(degree+1):
        basisvec = []
        for subind in range(size+1):
            if index == 0:
                basisvec.append(1)
            else:
                basisvec.append(subind**index)
        basis.append(basisvec)
        for prevind in range(len(basis)-1):
            dpsum = 0.0
            for subindex in range(size):
                dpsum += basis[prevind][subindex] * basis[-1][subindex]
            for subindex in range(size+1):
                basis[-1][subindex] = basis[-1][subindex] - basis[prevind][subindex] * dpsum
        dpsum = 0.0
        for subindex in range(size):
            dpsum += basis[-1][subindex] * basis[-1][subindex]
        for subindex in range(size+1):
            basis[-1][subindex] = basis[-1][subindex] / sqrt(dpsum)
        dpsum = 0.0
        for subind in range(size):
            dpsum += snippet[subind]*basis[index][subind]
        old_sample = []
        for i in range(len(my_sample)):
            old_sample.append(my_sample[i])
        searching = True
        factor = 1.0
        while searching:
            for i in range(len(my_sample)):
                my_sample[i] = old_sample[i]
            dpsum = 0.0
            for subind in range(size):
                dpsum += snippet[subind]*basis[index][subind]
            for subind in range(size+1):
                my_sample[subind] += factor * dpsum * basis[index][subind]
            delta = my_sample[-1] - my_sample[-2]
            if delta >= 0.0 and (index <=1 or delta <= 1.01428*slope):
                searching = False
            else:
                factor *= 0.95
        if index == 1:
            slope = factor * dpsum * (basis[1][1] - basis[1][0])

    return my_sample

import data_analyze
big_outbreaks = 1000


def gen_samples(size):
    samples = []
    for slopeno in range(301):
        slope = slopeno / 300.0 * 5.0
        packet = []
        for index in range(size+1):
            packet.append(slope * index)
        samples.append(packet)
    for slopeno in range(31):
        slope = slopeno / 30.0 * 2.0
        for coeffno in range(31):
            coeff = coeffno / 30.0 * 7.0 + 1.0
            packet = []
            for index in range(size+1):
                packet.append(exp(index * slope-coeff))
            samples.append(packet)
            packet = []
            for index in range(size+1):
                packet.append(-exp(-index * slope-coeff))
            samples.append(packet)
    return samples






def instate(value):
    cumlsum = 0
    comparator = 1.0
    while value >= comparator:
        cumlsum += 1
        comparator *= 2
    return cumlsum

silent = False



def matchscore(list1,list2):
    sum = 0.0
    dotp = 0.0
    for index in range(len(list1)):
        sum += (list1[index] - list2[index])**2
        dotp += (list1[index] - list2[index])
    return [sum*len(list1) - (dotp * dotp),dotp / len(list1)]

def find_analogue(thislist,datadict,samples,neededspace=1):
    score = 999999.0
    future = None
    size = len(thislist)
    using_real_data = False
#    for index in range(301):
#        shortlist = []
#        for subind in range(size+1):
#            shortlist.append(subind*index/100)
    special_samples = [polyfit(thislist,1),polyfit(thislist,2)]
    for shortlist in special_samples:
        matchdat = matchscore(thislist,shortlist)
        newfuture = shortlist[-1] + matchdat[1]
        ratejump = newfuture - thislist[-1] - (thislist[-1] - thislist[0])/len(thislist)
        if (matchdat[0] < score) and (newfuture >= thislist[-1]): #and (ratejump < 0.0):
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
                            if not using_real_data:
                                print("X",end='')
                                using_real_data =True
                        elif (matchdat[0] < score) and (newfuture >=thislist[-1]) and ((future is not None) and (newfuture <= future)):
                            score = matchdat[0]
                            future = newfuture
                            if not using_real_data:
                                print("X",end='')
                                using_real_data =True
    if (score > 4.0):
        return None
    if future is not None and linear_future is not None:
        future = 0.1 * future + 0.9 * linear_future
    return future

def do_analysis(remove):
    print('To remove',remove)
    datapackage = data_analyze.DataProcessor(remove)
    data = datapackage.my_aggregate_smoothlog
    my_aggregate_data = datapackage.my_aggregate_data
    samples = gen_samples(5)

    notable_labels = []
    for place in my_aggregate_data:
        if place != 'date' and place in data:
            if not silent:
                print(place + ' ',end='',flush=True)
            stopped = False
            reference = data[place][-1]
            if reference < ln(big_outbreaks):
                stopped = True          #Too Few Cases To Forecast
            for loop in range(7):
                shortlist = data[place][len(data[place])-7:len(data[place])]
                if not stopped:
                    outcome = find_analogue(shortlist,data,samples,3)
                    if outcome != None:
                        if not silent:
                            print(exp(outcome),end=', ',flush=True)
                        data[place].append(outcome)
                    else:
                        stopped = True
            if not stopped:
                notable_labels.append(place)
            if not silent:
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

    if remove == 0:
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
                today = exp(data[key][-8])/10
                next  = exp(data[key][-1])
                axs[int(count/2),count%2].plot([0,0],[today,next])



        fig.tight_layout(pad=2.0)
        plt.yscale('log')
        fig.savefig('topten.png')
    return report

fullreport = ''
for number in range(-backlog,1):
    fullreport += '=' * 80 + '\n'
    report = do_analysis(-number)
    fullreport = report + fullreport

print(fullreport)
