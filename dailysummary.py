import ast,re,os,datetime
import matplotlib.pyplot as plt
import datamollify

write_to = 'dailymessage.html'

todaydate = datetime.date.today().strftime("%Y-%m-%d")
yesterday = datetime.date.today() - datetime.timedelta(days=1)
yesterdaydate = yesterday.strftime("%Y-%m-%d")
print('Ignoring Data for',todaydate)

def deaccumulate(datalist):
    result = []
    for index in range(len(datalist)):
        if index == 0:
            result.append(datalist[0])
        else:
            result.append(datalist[index] - datalist[index-1])
    return result

nyt_year_file = '../covid-19-data/us-counties-{year}.csv'
nyt_live = '../covid-19-data/live/us-counties.csv'
max_radius = 6 # Can go up to 12
smooth_scale = 7 # days

#filedata = open('./census/fipsdata.py','r').read()
#codes = ast.literal_eval(filedata)

# Sample data
# Delco FIPS = 42045
# codes['42045'] = {'name': 'Delaware County, Pennsylvania', 'state': 'Pennsylvania', 'county': 'Delaware County', 'pop2019': 566747, 'dpop2019': 1516, 'adjacent': ['10003', '34015', '42029', '42091', '42101'], 'area_land': 183.84, 'area_total': 190.6}

#counties = {}
#counties['42045'] = {'dist' : 0, 'pop' : codes['42045']['pop2019']}
# for radius in range(1,max_radius+1):
#     newcohort = {}
#     for fipscode in counties:
#         if counties[fipscode]['dist'] == radius - 1:
#             for neighborfips in codes[fipscode]['adjacent']:
#                 if neighborfips not in counties and neighborfips not in newcohort:
#                     newcohort[neighborfips] = {'dist' : radius, 'pop' : codes[neighborfips]['pop2019']}
#     for fips in newcohort:
#         counties[fips] = newcohort[fips]

counties = {'42045': {'dist': 0, 'pop': 566747}, '10003': {'dist': 1, 'pop': 558753}, '34015': {'dist': 1, 'pop': 291636}, '42029': {'dist': 1, 'pop': 524989}, '42091': {'dist': 1, 'pop': 830915}, '42101': {'dist': 1, 'pop': 1584064}, '10001': {'dist': 2, 'pop': 180786}, '24015': {'dist': 2, 'pop': 102855}, '24029': {'dist': 2, 'pop': 19422}, '34033': {'dist': 2, 'pop': 62385}, '34001': {'dist': 2, 'pop': 263670}, '34007': {'dist': 2, 'pop': 506471}, '34011': {'dist': 2, 'pop': 149527}, '42011': {'dist': 2, 'pop': 421164}, '42071': {'dist': 2, 'pop': 545724}, '42017': {'dist': 2, 'pop': 628270}, '42077': {'dist': 2, 'pop': 369318}, '34005': {'dist': 2, 'pop': 445349}, '10005': {'dist': 3, 'pop': 234225}, '24011': {'dist': 3, 'pop': 33406}, '24035': {'dist': 3, 'pop': 50381}, '34009': {'dist': 3, 'pop': 92039}, '24025': {'dist': 3, 'pop': 255441}, '24003': {'dist': 3, 'pop': 579234}, '24005': {'dist': 3, 'pop': 827370}, '34029': {'dist': 3, 'pop': 607186}, '42075': {'dist': 3, 'pop': 141793}, '42107': {'dist': 3, 'pop': 141359}, '42043': {'dist': 3, 'pop': 278299}, '42133': {'dist': 3, 'pop': 449058}, '34019': {'dist': 3, 'pop': 124371}, '34021': {'dist': 3, 'pop': 367430}, '34041': {'dist': 3, 'pop': 105267}, '42095': {'dist': 3, 'pop': 305285}, '42025': {'dist': 3, 'pop': 64182}, '34025': {'dist': 3, 'pop': 618795}, '24019': {'dist': 4, 'pop': 31929}, '24045': {'dist': 4, 'pop': 103609}, '24047': {'dist': 4, 'pop': 52276}, '24041': {'dist': 4, 'pop': 37181}, '24009': {'dist': 4, 'pop': 92525}, '24027': {'dist': 4, 'pop': 325690}, '24033': {'dist': 4, 'pop': 909327}, '24510': {'dist': 4, 'pop': 593490}, '24013': {'dist': 4, 'pop': 168447}, '42037': {'dist': 4, 'pop': 64964}, '42079': {'dist': 4, 'pop': 317417}, '42097': {'dist': 4, 'pop': 90843}, '42041': {'dist': 4, 'pop': 253370}, '42067': {'dist': 4, 'pop': 24763}, '42099': {'dist': 4, 'pop': 46272}, '42001': {'dist': 4, 'pop': 103009}, '34027': {'dist': 4, 'pop': 491845}, '34035': {'dist': 4, 'pop': 328934}, '34023': {'dist': 4, 'pop': 825062}, '34037': {'dist': 4, 'pop': 140488}, '42089': {'dist': 4, 'pop': 170271}, '36081': {'dist': 4, 'pop': 2253858}, '36085': {'dist': 4, 'pop': 476143}, '24037': {'dist': 5, 'pop': 113510}, '24039': {'dist': 5, 'pop': 25616}, '51001': {'dist': 5, 'pop': 32316}, '24017': {'dist': 5, 'pop': 163257}, '24021': {'dist': 5, 'pop': 259547}, '24031': {'dist': 5, 'pop': 1050688}, '11001': {'dist': 5, 'pop': 705749}, '51059': {'dist': 5, 'pop': 1147532}, '51510': {'dist': 5, 'pop': 159428}, '42081': {'dist': 5, 'pop': 113299}, '42093': {'dist': 5, 'pop': 18230}, '42113': {'dist': 5, 'pop': 6066}, '42069': {'dist': 5, 'pop': 209674}, '42131': {'dist': 5, 'pop': 26794}, '42109': {'dist': 5, 'pop': 40372}, '42119': {'dist': 5, 'pop': 44923}, '42055': {'dist': 5, 'pop': 155027}, '42061': {'dist': 5, 'pop': 45144}, '42087': {'dist': 5, 'pop': 46138}, '34013': {'dist': 5, 'pop': 798975}, '34031': {'dist': 5, 'pop': 501826}, '34039': {'dist': 5, 'pop': 556341}, '36071': {'dist': 5, 'pop': 384940}, '42103': {'dist': 5, 'pop': 55809}, '42127': {'dist': 5, 'pop': 51361}, '36005': {'dist': 5, 'pop': 1418207}, '36047': {'dist': 5, 'pop': 2559903}, '36059': {'dist': 5, 'pop': 1356924}, '36061': {'dist': 5, 'pop': 1628706}, '34017': {'dist': 5, 'pop': 672391}, '51133': {'dist': 6, 'pop': 12095}, '51193': {'dist': 6, 'pop': 18015}, '51103': {'dist': 6, 'pop': 10603}, '51115': {'dist': 6, 'pop': 8834}, '51119': {'dist': 6, 'pop': 10582}, '51131': {'dist': 6, 'pop': 11710}, '51099': {'dist': 6, 'pop': 26836}, '51153': {'dist': 6, 'pop': 470335}, '51179': {'dist': 6, 'pop': 152882}, '24043': {'dist': 6, 'pop': 151049}, '51107': {'dist': 6, 'pop': 413538}, '51013': {'dist': 6, 'pop': 236842}, '51600': {'dist': 6, 'pop': 24019}, '51610': {'dist': 6, 'pop': 14617}, '42015': {'dist': 6, 'pop': 60323}, '42035': {'dist': 6, 'pop': 38632}, '42105': {'dist': 6, 'pop': 16526}, '42117': {'dist': 6, 'pop': 40591}, '42115': {'dist': 6, 'pop': 40328}, '42027': {'dist': 6, 'pop': 162385}, '42057': {'dist': 6, 'pop': 14530}, '42009': {'dist': 6, 'pop': 47888}, '42013': {'dist': 6, 'pop': 121829}, '34003': {'dist': 6, 'pop': 932202}, '36087': {'dist': 6, 'pop': 325789}, '36027': {'dist': 6, 'pop': 294218}, '36079': {'dist': 6, 'pop': 98320}, '36105': {'dist': 6, 'pop': 75432}, '36111': {'dist': 6, 'pop': 177573}, '36007': {'dist': 6, 'pop': 190488}, '36025': {'dist': 6, 'pop': 44135}, '36119': {'dist': 6, 'pop': 967506}, '09001': {'dist': 6, 'pop': 943332}, '36103': {'dist': 6, 'pop': 1476601}}


csvqueue = []
year = 2020
while os.path.exists(nyt_year_file.format(year=year)):
    csvqueue.append(nyt_year_file.format(year=year))
    year += 1
if os.path.exists(nyt_live):
    csvqueue.append(nyt_live)

dates = {}
for csvfile in csvqueue:
    mycsv_rows = open(csvfile,'r').readlines()
    for row in mycsv_rows:
        cols = re.split(r',|\n',row)
        if cols[0] != 'date':
            dates[cols[0]] = True
            if cols[3] in counties:
                if 'data' not in counties[cols[3]]:
                    counties[cols[3]]['data'] = {}
                counties[cols[3]]['data'][cols[0]] = int(cols[4])

dates = list(dates.keys())
dates.sort()
if dates[-1] == todaydate:
    del dates[-1]

for county in counties:
    if 'data' in counties[county]:
        datalist = []
        for date in dates:
            if date in counties[county]['data']:
                datalist.append(counties[county]['data'][date])
            elif len(datalist) == 0:
                datalist.append(0)
            else:
                datalist.append(datalist[-1])
        #datalist = deaccumulate(datalist)
        #datalist = datamollify.smoothit(datalist,smooth_scale)
        counties[county]['data'] = datalist

all_data = {}
population = {}
rate_today = {}

for radius in range(max_radius+1):
    all_data[radius] = [0] * len(dates)

for county in counties:
    if 'data' in counties[county]:
        radius = counties[county]['dist']
        for cumlrad in range(radius,max_radius+1):
            if cumlrad not in population:
                population[cumlrad] = 0
            population[cumlrad] += counties[county]['pop']
            for index,value in enumerate(counties[county]['data']):
                all_data[cumlrad][index] += value

numplots = max_radius + 1

fig, ax = plt.subplots(numplots,1,figsize=(15,20))
tickno = []
tickl = []
datespan = int(len(dates)/119)*7

for index in range(len(dates)):
    if (index - len(dates)+1) % datespan == 0:
        tickno.append(index-1)
        tickl.append(dates[index][5:10])
for index in range(numplots):
    plt.subplot(ax[index])
    plt.xticks(tickno,tickl)
    plt.margins(x=0)
    ax[index].grid(axis='y',linestyle=':')
    minlist,maxlist = datamollify.minmax(all_data[index],8)
    deriv = datamollify.differentiate(minlist,maxlist)
    rate_today[index] = int(deriv[-1]+0.5)
    ax[index].plot(range(len(dates)),deaccumulate(all_data[index]))
    ax[index].plot(range(len(dates)),deriv)
    ax[index].set_ylim(bottom=0,top=1.1*max(deriv))
#plt.yscale('log')
fig.savefig('plotnearby.png',bbox_inches='tight')

htmlmessage = 'Delaware County COVID-19 Monitor<br>\n'
htmlmessage += 'as of ' + dates[-1] + '<br>\n'
htmlmessage += '<table border="1" cellspacing="5" cellpadding="3">\n'

for index in range(max_radius+1):
    htmlmessage += '<tr>\n'
    packet = [index,rate_today[index],population[index],int(1000000*rate_today[index]/population[index])/10]
    for item in packet:
        htmlmessage += '<td>' + str(item) + '</td>\n'
    htmlmessage += '</tr>\n'
htmlmessage += '</table>'

open(write_to,'w').write(htmlmessage)
