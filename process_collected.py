import re

filename = 'collected.txt'

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
                    if scale(coverage[state][county][prevday][0]) != scale(coverage[state][county][nextday][0]):
                        print('Need',state,county,dayno,coverage[state][county][prevday][0],'->',coverage[state][county][nextday][0])
    return coverage

coverage = read_file(filename)
coverage = interpolate(coverage)
write_file('test.txt',coverage)
