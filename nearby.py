import ast,re
import matplotlib.pyplot as plt
import regularize


outtxt = True
filedata = open('./census/fipsdata.py','r').read()
nyt_file = '../covid-19-data/us-counties.csv'
nyt_live = '../covid-19-data/live/us-counties.csv'
codes = ast.literal_eval(filedata)

county_neighborhoods = {0 : ['42045']}
neighborhood_totals = {0 : {}}
max_radius = 6 # Can go up to 12
capture_days = 28
rewind=0

def list_difference(mylist):
    result = []
    for index in range(len(mylist)-1):
        result.append(mylist[index] - mylist[index+1])
    return result

def _mass_motion(mylist):
    thislist = []
    shifts = 0
    for value in mylist:
        if len(thislist) == 0:
            thislist = [value]
        else:
            comeafter = len(thislist)-1
            while value < thislist[comeafter]:
                comeafter -= 1
                shifts += thislist[comeafter] - value
                if comeafter < 0:
                    break
            putat = comeafter + 1
            if putat < len(thislist):
                thislist.insert(putat,value)
            else:
                thislist.append(value)
    return shifts
def mass_motion(mylist,population):
    numerator = _mass_motion(mylist)
    slist = []
    for value in mylist:
        slist.append(value)
    slist.sort(reverse=True)
    denominator = (_mass_motion(slist) + population/1000)
    return numerator/denominator
def min_grade(gradelist):
    conversions = {'GREEN' : 0, 'YELLOW' : 1, 'RED' : 2}
    backscore = {0 : 'GREEN', 1 : 'YELLOW', 2 : 'RED'}
    scores = []
    for item in gradelist:
        scores.append(conversions[item])
    return backscore[max(scores)]
def final_grade(gradelist):
    conversions = {'GREEN' : 0, 'YELLOW' : 1, 'RED' : 2}
    backscore = {0 : 'GREEN', 1 : 'YELLOW', 2 : 'RED'}
    scores = []
    for item in gradelist:
        scores.append(conversions[item])
    scores.sort()
    midpoint = int(len(gradelist)/2)
    middle = backscore[scores[midpoint]]
    next = backscore[scores[midpoint+1]]
    return middle


def grade(series):
    grades = []
    justifications = []
    # Cases in last week 0.04% to 0.1% of population
    level = (sum(series['cases'][0:7]) - max(series['cases'][0:7])) / series['population'] * 10000
    if level <= 3:
        grades.append('GREEN')
    elif level <= 5:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = 'per capita new cases 7 days, excluding worst day = %6.3f * 10^{-4}' % (level)
    justifications.append(jtext)

    level = (sum(series['cases'][0:7])) / series['population'] * 10000
    if level <= 3.5:
        grades.append('GREEN')
    elif level <= 5:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = 'per capita new cases 7 days = %6.3f * 10^{-4}' % (level)
    justifications.append(jtext)


    # [Days increased,Days decreased] It should not be going up very often
    ticks = [0,0]
    previous = 0
    for value in series['cases']:
        if value >= previous:
            ticks[1] += 1
        else:
            ticks[0] += 1
        previous = value
    if ticks[1] >= ticks[0]:
        grades.append('GREEN')
    elif ticks[1] >= 0.75*ticks[0]:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = 'over %i days: %i day-to-day decreases and %i increases' % (len(series['cases']),ticks[1],ticks[0])
    justifications.append(jtext)

    # How much movement to make it decreasing?
    score = mass_motion(series['cases'],series['population'])
    if score <= 0.15:
        grades.append('GREEN')
    elif score <= 0.3:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = 'Closeness to nondecreasing (0-1) =  %5.3f' % (score)
    justifications.append(jtext)

    # How much change compared to last week?
    vs_lastweek = series['cases'][0] + series['cases'][1] - series['cases'][7] - series['cases'][8]
    vs_lastweek = vs_lastweek / series['population'] * 10000
    if vs_lastweek <= -0.01:
        grades.append('GREEN')
    elif vs_lastweek <= 0.5:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = 'Last two days per capita change over last week = %6.3f * 10^{-4}' % (vs_lastweek)
    justifications.append(jtext)

    # Should be closer to the minimum in week-over-week data
    upper = series['cases'][0]
    lower = series['cases'][0]
    at_spot = 7
    while at_spot < len(series['cases']):
        upper = max(upper,series['cases'][at_spot])
        lower = min(lower,series['cases'][at_spot])
        at_spot += 7
    upper += 10
    fraction = (series['cases'][0]-lower)/(upper-lower)
    if fraction <= 0.25:
        grades.append('GREEN')
    elif fraction <= 0.45:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = 'Closeness to minimum (week over week) = %5.3f' % (fraction)
    justifications.append(jtext)

    # Should be much closer to the minum over the last few days than the maximum
    upper = max(series['cases']) + 10
    lower = min(min(series['cases'][3:len(series['cases'])]),max(series['cases'][0:3]))
    fraction = (max(series['cases'][0:3])-lower)/(upper-lower)
    if fraction <= 0.25:
        grades.append('GREEN')
    elif fraction <= 0.45:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = 'Max of last 3 days, closeness to minimum = %5.3f' % (fraction)
    justifications.append(jtext)

    baseline = []
    for index in range(len(series['cases'])):
        baseline.insert(0,series['cases'][index])
    smoothrev = regularize.regularize(regularize.pointwindow(baseline,4,0.05),1e-4 * max(baseline))
    smooth = []
    for index in range(len(smoothrev)):
        smooth.insert(0,smoothrev[index])

    level = sum(smooth[0:7]) / series['population'] * 10000
    if level <= 3:
        grades.append('GREEN')
    elif level <= 5:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = 'per capita new cases 7 days (regularized) = %6.3f * 10^{-4}' % (level)
    justifications.append(jtext)

    level = (14*smooth[0] - sum(smooth[0:7])) / series['population'] * 10000
    if level <= 3:
        grades.append('GREEN')
    elif level <= 5:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = 'per capita new cases 7 days (regularized 3.5 day forecast) = %6.3f * 10^{-4}' % (level)
    justifications.append(jtext)

    fraction = (smooth[0] - min(smooth)) / (max(smooth)-min(smooth))
    if fraction <= 0.25:
        grades.append('GREEN')
    elif fraction <= 0.45:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = '(regularized) closeness to minimum = %5.3f' % (fraction)
    justifications.append(jtext)
    ticks = [0,0]
    previous = 0
    for value in smooth:
        if value >= previous:
            ticks[1] += 1
        else:
            ticks[0] += 1
        previous = value
    if ticks[1] >= 1.5*ticks[0]:
        grades.append('GREEN')
    elif ticks[1] >= 0.9*ticks[0]:
        grades.append('YELLOW')
    else:
        grades.append('RED')
    jtext = '(regularized) over %i days: %i day-to-day decreases and %i increases' % (len(smooth),ticks[1],ticks[0])
    justifications.append(jtext)

    series['grades'] = grades
    series['justifications'] = justifications
    series['final_grade'] = final_grade(grades)
    return series['final_grade']

def multiday_grade(series):
    starting_cases = series['cases']
    starting_deaths = series['deaths']

    final_grades = []
    daysback = [13,12,11,10,9,8,7,6,5,4,3,2,1,0]
    for offset in daysback:
        series['cases'] = []
        series['deaths'] = []
        for index in range(len(starting_cases)):
            if index >= offset:
                series['cases'].append(starting_cases[index])
                series['deaths'].append(starting_deaths[index])
        result = grade(series)
        final_grades.insert(0,result)
    middle = final_grade(final_grades)
    take_worst = [final_grades[0],middle]
    if 'RED' in final_grades[0:6]:
        take_worst.append('YELLOW')
    minimum = min_grade(take_worst)
    if minimum == 'YELLOW':
        count_greens = 0
        for index in range(3):
            if final_grades[index] == 'GREEN':
                count_greens += 1
        if count_greens >= 2:
            minimum = min_grade(['GREEN',final_grades[0]])
    return minimum

for radius in range(1,max_radius+1):
    neighborhood_totals[radius] = {}
    county_neighborhoods[radius] = []
    for code in county_neighborhoods[radius-1]:
        if code not in county_neighborhoods[radius]:
            county_neighborhoods[radius].append(code)
        for code2 in codes[code]['adjacent']:
            if code2 not in county_neighborhoods[radius]:
                county_neighborhoods[radius].append(code2)

population = {}
for radius in county_neighborhoods:
    population[radius] = 0
    for county in county_neighborhoods[radius]:
        population[radius] += codes[county]['pop2019']

mycsv_rows = open(nyt_file,'r').readlines()
mycsv_rows += open(nyt_live,'r').readlines()
already_used = {}
import datetime
todaydate = datetime.date.today().strftime("%Y-%m-%d")
yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterdaydate = yesterday.strftime("%Y-%m-%d")
print('Ignoring Data for',todaydate)
for row in mycsv_rows:
    cols = re.split(',',row)
    if len(cols) <= 3:
        raise('I thought it would be longer')
    if cols[3] in county_neighborhoods[max_radius]:
        tag = (cols[0],cols[1],cols[2],cols[3])
        if cols[0] == todaydate:
            cols[0] = yesterdaydate
            tag = (cols[0],cols[1],cols[2],cols[3])
        if tag not in already_used:
            for radius in range(max_radius+1):
                if cols[3] in county_neighborhoods[radius]:
                    if cols[0] not in neighborhood_totals[radius]:
                        neighborhood_totals[radius][cols[0]] = [0,0]
                    neighborhood_totals[radius][cols[0]][0] += int(cols[4])
                    neighborhood_totals[radius][cols[0]][1] += int(cols[5])

        already_used[tag] = True

gathered_data = {}
all_data = {}
for radius in neighborhood_totals:
    cases = []
    deaths = []
    last_day = ''
    all_dates = []
    for date in sorted(neighborhood_totals[radius]):
        cases.append(neighborhood_totals[radius][date][0])
        deaths.append(neighborhood_totals[radius][date][1])
        last_day = date
        if date not in all_dates:
            all_dates.append(date)
    all_data[radius] = {'cases' : cases, 'deaths' : deaths}
    cases = cases[len(cases)-capture_days-rewind:len(cases)-rewind]
    deaths = deaths[len(deaths)-capture_days-rewind:len(deaths)-rewind]
    cases.reverse()
    deaths.reverse()
    cases = list_difference(cases)
    deaths = list_difference(deaths)


    gathered_data[radius] = {'cases' : cases, 'deaths' : deaths, 'as_of' : last_day, 'population' : population[radius]}


message = '-' * 25 + '\n'
message += '| COVID-19 Local Status |\n|   As Of: ' + gathered_data[0]['as_of'] + '   |\n'

for key in gathered_data:
    line = '|%1i: ' % (key)
    line += (multiday_grade(gathered_data[key]) + ' ' * 4)[0:6]
    line += '%5i %8i' % (gathered_data[key]['cases'][0],gathered_data[key]['population'])
    message += line + '|\n'
message += '-' * 25 + '\n'
for index in range(len(gathered_data[0]['grades'])):
    message += (gathered_data[0]['grades'][index] + ' ' * 4)[0:6] + ' ' + gathered_data[0]['justifications'][index] + '\n'

if outtxt:
    try:
        filestr = open('local_status.txt','r').read()
        message += '\n'
        message += '=' * 40 + '\n'
        message += filestr
    except:
        message += '\n'
        message += '=' * 40
    open('local_status.txt','w').write(message)

print(message)


def convolution(rawcumulative,which):
    massdistro = {}
    massdistro[0] = [-1,-2,-1,0,0,0,0,0,0,1,2,1]
    massdistro[1] = [-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1]
    massdistro[2] = [7,-1,-1,-1,-1,-1,-1,-15,1,1,1,1,1,1,8]
    massdistro[3] = [-1,1]
    massdistro = massdistro[which]
    normalization = 0
    for index in range(len(massdistro)):
        normalization += index * massdistro[index]
    width = len(massdistro)
    result = []
    for index in range(len(rawcumulative)+1):
        locsum = 0
        for subind in range(width):
            if index-width+subind < 0:
                value = rawcumulative[0]
            else:
                value = rawcumulative[index-width+subind]
                locsum += massdistro[subind] * value / normalization
        result.append(locsum)
    return result
numplots = 6
avg = 5
fig, ax = plt.subplots(numplots,1,figsize=(15,20))
tickno = []
tickl = []
for index in range(len(all_dates)):
    if (index - len(all_dates)+1) % 28 == 0:
        tickno.append(index-1)
        tickl.append(all_dates[index][5:10])
for index in range(numplots):
    plt.subplot(ax[index])
    plt.xticks(tickno,tickl)
    ax[index].grid(axis='y',linestyle=':')
    for choice in [3]:
        diffs = convolution(all_data[index]['cases'],choice)
        ax[index].plot(range(len(diffs)),diffs)
        newguys = regularize.regularize(regularize.pointwindow(diffs,4,0.05),1e-4 * max(diffs))
        ax[index].plot(range(len(newguys)),newguys)
        ax[index].set_ylim(bottom=0,top=1.1*max(newguys))
#plt.yscale('log')
fig.savefig('plotnearby.png',bbox_inches='tight')
