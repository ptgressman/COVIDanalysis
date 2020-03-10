from sympy import *
import textmanip
import re

sort_bins = [[0,1],[2,3],[4,6],[7,10],[11,15],[16,999]]
sort_labels = [
'  <2 days  ',
'  2-3 days ',
'  4-6 days ',
'  7-10 days',
' 11-15 days',
'  >15 days ']
state_labels = ['   1    case ',' 2 - 3  cases',' 4 - 7  cases', ' 8 - 15 cases', '16 - 31 cases', '32 - 63 cases','64 -127 cases','128-255 cases','256-511 cases']
report = ''


def timesort(daynumber,sort_bins):

    for index,item in enumerate(sort_bins):
        if (daynumber >= item[0] and daynumber <= item[1]):
            return index

CSVlocation = "../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"

with open(CSVlocation,"r") as file:
    rawdata = file.read()
    file.close()

CSV = textmanip.csv_parse(rawdata)

report = 'US County-level COVID-19 Confirmed Case Profile: ' + CSV[0][-1] + '\n'
report += 'Maximum Likelihood Estimation of Duration Periods:\n'
report += '(PAST = # counties having experienced/exceeded level; CURR = # counties presently at level)\n'

data = {}
for index,item in enumerate(CSV):
    if index > 0 and re.search('County',item[0]):
        data[item[0]] = []
        for subind,subit in enumerate(item):
            if subind > 3:
                data[item[0]].append(textmanip.atof(subit))

def max_likelihood_distro(exacts,atleasts):
    # Events are 0,1,...,len(exacts)-1
    # exacts counts how many completed draws had specific values
    # atleasts counts how many ongoing draws had given lower bounds
    prob = []
    denom = []
    accumprob = 0.0
    for eventno in range(len(exacts)):
        if eventno == 0:
            totaldraws = 0
            for counter in range(len(exacts)):
                totaldraws += exacts[counter] + atleasts[counter]
            denom.append(totaldraws - atleasts[0])
            prob.append(exacts[0]/denom[0])
            accumprob += prob[0]
        elif eventno < len(exacts) - 1:
            denom.append(denom[eventno-1] - atleasts[eventno]/(1-accumprob))
            prob.append(exacts[eventno]/denom[eventno])
            accumprob += prob[eventno]
        else:
            prob.append(1.0-accumprob)
    return prob

def instate(value):
    cumlsum = 0
    comparator = 1.0
    while value >= comparator:
        cumlsum += 1
        comparator *= 2
    return cumlsum

transitions = []
pre_exact = []
pre_ongo  = []
global_max_state = 0
for item in data.keys():
    state_durations = {}
    currentstate = 0
    total = 0
    maxstate = 0
    for value in data[item]:
        thisstate = instate(value)
        if (thisstate != currentstate) :
            if currentstate != 0:
                state_durations[currentstate] = total
                if currentstate > maxstate:
                    maxstate = currentstate
                    if (maxstate > global_max_state):
                        global_max_state = maxstate
            currentstate = thisstate
            total = 1
        else:
            total += 1
    if currentstate > global_max_state:
        global_max_state = currentstate
    if currentstate > maxstate + 1:
        maxstate = currentstate - 1
    for index in range(maxstate):
        if (index+1) in state_durations:
            pre_exact.append([index+1,state_durations[index+1]])
        else:
            pre_exact.append([index+1,0])
    if currentstate > 0:
        pre_ongo.append([currentstate,total])

distribution = {}
occur_types = {}
if (global_max_state > 1+len(state_labels)):
    global_max_state = 1+len(state_labels)
for index in range(global_max_state):
    stateval = index + 1
    max_duration = 0
    exacts = {}
    ongoings = {}
    previous_count = 0
    current_count = 0
    for item in pre_exact:
        if item[0] == stateval:
            if item[1] not in exacts:
                exacts[item[1]] = 0
            exacts[item[1]] += 1
            previous_count += 1
            if max_duration < item[1]:
                max_duration = item[1]
    for item in pre_ongo:
        if item[0] == stateval:
            if item[1] not in ongoings:
                ongoings[item[1]] = 0
            ongoings[item[1]] += 1
            current_count += 1
            if max_duration < item[1]:
                max_duration = item[1]
    for newind in range(max_duration+1):
        if newind not in exacts:
            exacts[newind] = 0
        if newind not in ongoings:
            ongoings[newind] = 0
    distribution[stateval] = max_likelihood_distro(exacts,ongoings)
    occur_types[stateval] = [previous_count,current_count]

report += ' ' * 15
report += 'PAST|CURR '
for item in sort_labels:
    report += item
report += '\n'

for state in distribution:
    report += state_labels[state-1]
    report += ' (%4d|%4d)' % (occur_types[state][0],occur_types[state][1])
    for item in sort_bins:
        prob = 0.0
        for index, value in enumerate(distribution[state]):
            if index >= item[0] and index <= item[1]:
                prob += value
        if prob > 0:
            probstr = "%5.2f" % (prob*100) + '%'
            if probstr == '100.00%':
                probstr = '100.0%'
        else:
            probstr = "      "
        report += '   ' + probstr + '  '
    report += '\n'


print(report)
