from sympy import *
import textmanip
import re,ast,math

sort_bins  = [[0,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,99]]
state_bins = [[1,1],[2,3],[4,7],[8,15],[16,31],[32,63],[64,127],[128,255],
[256,511],[512,1023]]

import githubnytcounties

data = githubnytcounties.county_timeseries
date = githubnytcounties.days[-1]
print(len(data))





def in_bin(value,bins):
    for index,item in enumerate(bins):
        if value >= item[0] and value <= item[1]:
            return index
    return -1

def measure_state_duration(datalist,bin):
    started = False
    start_index = -1
    end_index = -1
    durations = []
    exceeded = False
    for index,value in enumerate(datalist):
        if value > bin[1]:
            exceeded = True
        if value >= bin[0] and value <= bin[1]:
            if not started:
                started = True
                start_index = index
        else:
            if started:
                started = False
                duration = index - start_index
                durations.append(duration)
        end_index = index
    result = {}
    if len(durations) == 0 and exceeded:
        durations = [0]
    result['complete'] = durations
    ongoing = []
    if started:
        ongoing = [end_index - start_index+1]
    result['incomplete'] = ongoing
    return result

def collate_durations(durationlist):
    maxdur = -1
    for item in durationlist:
        if len(item['complete']) > 0:
            maxdur = max(maxdur,max(item['complete']))
        if len(item['incomplete']) > 0:
            maxdur = max(maxdur,max(item['incomplete']))
    exacts = [0] * (maxdur + 1)
    ongoin = [0] * (maxdur + 1)
    for item in durationlist:
        for subitem in item['complete']:
            exacts[subitem] += 1
        for subitem in item['incomplete']:
            ongoin[subitem] += 1
    result = {'closed' : exacts, 'open' : ongoin}
    return result



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

def mldistro_from_reports(reportslist):
    totals = collate_durations(reportslist)
    return max_likelihood_distro(totals['closed'],totals['open'])

def flatten_distro(distrolist,binlist):
    result = [0] * len(binlist)
    for index,value in enumerate(distrolist):
        location = in_bin(index,binlist)
        if location >= 0:
            result[location] += value
    return result


def tostring(numberlist):
    result = ''
    for item in numberlist:
        result += '% 6.2f' % (item * 100) + '% '
    return result[0:len(result)-1]

def headerstring(sort_bins):
    width=7
    header = ''
    for item in sort_bins:
        if item[0] == item[1]:
            mini = '%i' % item[0]
        else:
            mini = '%i-%i' % (item[0],item[1])
        full = width - len(mini)
        if full > 0:
            mini =  mini + ' ' * int(full/2)
            mini = ' ' * (width - len(mini)) + mini
        header += mini + ' '
    return re.sub(r'\s*$','',header)


####

fips = ast.literal_eval(open('census/fipsdata.py').read())
del data['']
exacts = [0] * 60
ongoes = [0] * 60
for locale1 in data:
    nonzero1 = -1
    for index,item in enumerate(data[locale1]):
        if item > 0 and nonzero1 < 0:
            nonzero1 = index
    for locale2 in fips[locale1]['adjacent']:
        nonzero2 = -1
        if locale2 in data:
            for index, item in enumerate(data[locale2]):
                if item > 0 and nonzero2 < 0:
                    nonzero2 = index
    if nonzero1 > 0 and nonzero2 > 0:
        delay = abs(nonzero1 - nonzero2)
        exacts[delay] += 1
    else:
        nonzero2 = len(data[locale1])
        delay = abs(nonzero1 - nonzero2)
        ongoes[delay] += 1
print(exacts)
print(ongoes)
probs = max_likelihood_distro(exacts,ongoes)
print(tostring(probs))
for index,item in enumerate(probs):
    print(math.log(item+0.00000000001))

#####



topline = ' Case Range ( PAST| CURR)' + headerstring(sort_bins)
print(topline)
for state in state_bins:
    reports = []
    complete = 0
    incomplete = 0
    for item in data:
        myreport = measure_state_duration(data[item],state)
        reports.append(myreport)
        complete += len(reports[-1]['complete'])
        incomplete += len(reports[-1]['incomplete'])
    mydistro = mldistro_from_reports(reports)
    percents = tostring(flatten_distro(mydistro,sort_bins))
    percents = "(% 5i|% 5i)" % (complete,incomplete) + percents
    percents = "%5i-%5i" % (state[0],state[1]) + ' ' + percents
    print(percents)


#####

print('+'*80)

reports = {}
for item in data:
    first = measure_state_duration(data[item],[1,5])
    secon = measure_state_duration(data[item],[5,25])
    if len(first['complete']) > 0 and len(first['incomplete']) == 0:
        range1 = in_bin(first['complete'][-1],sort_bins)
        if range1 not in reports:
            reports[range1] = []
        reports[range1].append(secon)

for index in range(len(sort_bins)):
    if index in reports and len(reports[index]) > 0:
        mydistro = mldistro_from_reports(reports[index])
        print(tostring(flatten_distro(mydistro,sort_bins)),end='')
        result = 0
        for index,item in enumerate(mydistro):
            result += item * index
        print(result)
    else:
        print()
