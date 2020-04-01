import githubnytcounties
import re,ast,math

data = githubnytcounties.county_timeseries

fipsdata = ast.literal_eval(open("../census/fipsdata.py").read())

nopop = []
for item in fipsdata:
    if 'pop2019' not in fipsdata[item]:
        nopop.append(item)
for item in nopop:
    del fipsdata[item]

infolist = {}
for item in fipsdata:
    starti = -1
    cases = 0
#    print(item,data[item],len(data[item]))
    popn = fipsdata[item]['pop2019']
    infolist[item] = {}
    infolist[item]['population'] = popn
    if item in data:
        for myind in range(len(data[item])):
            if data[item][myind] > 5 and starti < 0:
                starti = myind
                cases = data[item][myind]
        endc = data[item][-1]
        dayrange = len(data[item]) - starti - 1
        if endc > 2 * cases and dayrange > 5 and cases > 5:
            rate = math.exp((math.log(endc) - math.log(cases))/dayrange)
            infolist[item]['rate'] = rate
        else:
            infolist[item]['rate'] = math.exp(0.33)
        totalcases = data[item][-1]
        totalrecovered = data[item][-14]
    else:
        infolist[item]['rate'] = math.exp(0.33)
        totalcases = 0
        totalrecovered = 0
    infolist[item]['s'] = (popn-totalcases)/popn
    infolist[item]['i'] = (totalcases-totalrecovered)/popn
    infolist[item]['popfac'] = ((popn + fipsdata[item]['dpop2019'])/popn)**(1/365)

mystring = ''
for days in range(400):
    fact = 1.0
    if (int(days/28)%2) == 0:
        fact = 0.1
    for item in infolist:
        beta = fact*(infolist[item]['rate'] - 1 + 0.17)
        s = infolist[item]['s']
        i = infolist[item]['i']
        popfac = infolist[item]['popfac']
        infolist[item]['ds'] = - beta * s * i #+ (popfac - 1) * (1-s)
        infolist[item]['di'] = beta * s * i - 0.17 * i
        newcases = infolist[item]['di'] * infolist[item]['population']
        # Here's a weak link: you get a case when your neighbor has at least 24
        one = 1 / infolist[item]['population']
        if i <= one:
            for subitem in fipsdata[item]['adjacent']:
                if subitem in infolist and infolist[subitem]['i'] * infolist[subitem]['population'] > 64:
                    infolist[item]['di'] += one * 0.2
    total_s = 0
    total_i = 0
    for item in infolist:
        infolist[item]['s'] += infolist[item]['ds']
        infolist[item]['i'] += infolist[item]['di']
        total_s += infolist[item]['population'] * infolist[item]['s']
        total_i += infolist[item]['population'] * infolist[item]['i']
    mystring += str(days) + ',' + str(total_i) + ',' + str(total_s) + '\n'

open('projections.csv','w').write(mystring)
