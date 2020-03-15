import re

filename = 'collected.txt'

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

def scale(number):
    if number < 1:
        return 0
    returnvalue = 0
    level = 1
    while (number >= level):
        level *= 2
        returnvalue += 1
    return returnvalue

def read_file(filename):
    read_pattern = re.compile(r'(?P<description>.*?)\s*{(?P<day>\d*):(?P<state>(\w| )*):(?P<county>(\w| )*):(?P<number>\d*)}')
    with open(filename,'r') as file:
        rawtxt = file.read()
        file.close()
    records = []
    coverage = {}
    for item in re.finditer(read_pattern,rawtxt):
        descr = item.group('description')
        day   = int(item.group('day'))
        state = item.group('state')
        county = item.group('county')
        number = int(item.group('number'))
        if state not in coverage:
            coverage[state] = {}
        if county not in coverage[state]:
            coverage[state][county] = {}
        coverage[state][county][day] = [number,descr]
    return coverage

def write_file(filename,coverage):
    file = open(filename,'w')
    statelist = list(coverage.keys())
    statelist.sort()
    for state in statelist:
        countylist = list(coverage[state].keys())
        countylist.sort()
        for county in countylist:
            datelist = list(coverage[state][county].keys())
            datelist.sort()
            for day in datelist:
                file.write(coverage[state][county][day][1] + ' {' + str(day) + ':' + state + ':' + county + ':' + str(coverage[state][county][day][0]) + '}\n')
    file.close()

def interpolate(coverage):
    counties = []
    for state in coverage:
        for county in coverage[state]:
            counties.append([state,county])
    for item in counties:
        state = item[0]
        county = item[1]
        daylist = list(coverage[state][county].keys())
        daylist.sort()
        first = daylist[0]
        last  = daylist[-1]
        prevday = -1
        for dayno in range(first,last):
            if dayno in daylist:
                prevday = dayno
            if dayno not in daylist:
                nextday = dayno
                while nextday not in daylist:
                    nextday += 1
                if coverage[state][county][prevday][0] == coverage[state][county][nextday][0]:
                    coverage[state][county][dayno] = [coverage[state][county][prevday][0],'(presumed)']
                else:
                    startno = coverage[state][county][prevday][0]
                    endno   = coverage[state][county][nextday][0]
                    increment = (endno - startno) / (nextday - prevday)
                    newval = int(increment+startno + 0.5)
                    print('Need',state,county,dayno,startno,'--',newval,'--',endno)
                    coverage[state][county][prevday+1] = [newval,'(interpolated)']
                    #if scale(coverage[state][county][prevday][0]) != scale(coverage[state][county][nextday][0]):
                        #print('Need',state,county,dayno,coverage[state][county][prevday][0],'->',coverage[state][county][nextday][0])

    return coverage

coverage = read_file(filename)
coverage = interpolate(coverage)
completeds = {}
ongoings   = {}
max_duration = 0
max_state = 0
for state in coverage:
    for county in coverage[state]:
        daylist = list(coverage[state][county].keys())
        daylist.sort()
        first = daylist[0]
        last  = daylist[-1]
        magnitude = 0
        duration = 0
        for day in daylist:
            newmag = scale(coverage[state][county][day][0])
            if newmag != magnitude:
                if magnitude != 0:
                    while magnitude < newmag:
                        if magnitude not in completeds:
                            completeds[magnitude] = {}
                            if magnitude > max_state:
                                max_state = magnitude
                        if duration not in completeds[magnitude]:
                            completeds[magnitude][duration] = 0
                        completeds[magnitude][duration] += 1
                        if duration > max_duration:
                            max_duration = duration
                        magnitude += 1
                        duration = 0
                duration = 1
                magnitude = newmag
            else:
                duration += 1
        if magnitude != 0:
            if magnitude not in ongoings:
                ongoings[magnitude] = {}
                if magnitude > max_state:
                    max_state = magnitude
            if duration not in ongoings[magnitude]:
                ongoings[magnitude][duration] = 0
            ongoings[magnitude][duration] += 1
            if duration > max_duration:
                max_duration = duration

distribution = {}
occur_types = {}
for stateno in range(1,max_state+1):
    max_duration = 0
    if stateno not in completeds:
        completeds[stateno] = {}
    if stateno not in ongoings:
        ongoings[stateno] = {}
    for value in completeds[stateno]:
        if value > max_duration:
            max_duration = value
    for value in ongoings[stateno]:
        if value > max_duration:
            max_duration = value
    for durationval in range(max_duration+1):
        if durationval not in completeds[stateno]:
            completeds[stateno][durationval] = 0
        if durationval not in ongoings[stateno]:
            ongoings[stateno][durationval] = 0
    finished = []
    openend = []
    finish_count = 0
    ongoing_count = 0
    for dayno in range(max_duration+1):
        finished.append(completeds[stateno][dayno])
        openend.append(ongoings[stateno][dayno])
        finish_count += completeds[stateno][dayno]
        ongoing_count += ongoings[stateno][dayno]
    occur_types[stateno] = [finish_count,ongoing_count]
    distribution[stateno] = max_likelihood_distro(finished,openend)

print(distribution)

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
