# Census Bureau Population Data: https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-total.html
# Census County Adjacency Table: https://www2.census.gov/geo/docs/reference/county_adjacency.txt
import re
import textmanip

nyc = ['New York','Kings','Queens','Richmond','Bronx'] # New York City

csv1 = 'us-counties.csv'
csv2 = 'co-est2019-alldata.csv'
csv3 = 'all-geocodes-v2017.csv'

raw1 = open(csv1,'r').read()
raw2 = open(csv2,'r',encoding='cp1250').read()
raw3 = open(csv3,'r').read()

CSV1 = textmanip.csv_parse(raw1)
CSV2 = textmanip.csv_parse(raw2)
CSV3 = textmanip.csv_parse(raw3)

def fips_int_to_str(fipsint):
    code = str(fipsint)
    if len(code) < 5:
        code = '0' * (5 - len(code)) + code
    return code

state_code_to_name = {}
state_name_to_code = {}
state_county_info = {}   # Keys are string FIPS state names; each is a dictionary name -> code
fips_id = {}
for index,line in enumerate(CSV3):
    if index > 0:
        if line[0] == '040':
            code = line[1]
            state = line[6]
            state_code_to_name[code] = state
            state_name_to_code[state] = code
            state_county_info[state] = {}
        elif line[0] == '050':
            state = state_code_to_name[line[1]]
            code = line[2]
            name = line[6]
            state_county_info[state][name] = {'fips' : code}
            fips_id[line[1] + code] = {'name' : name + ', ' + state, 'state' : state, 'county' : name, 'adjacent' : []}



countylist1 = {}
countylist2 = {}

for index,item in enumerate(CSV1):
    county = [item[2],item[1]] # State, County, fips
    if tuple(county) not in countylist1 and county[1] != 'Unknown' and index > 0:
        countylist1[tuple(county)] = item[3]

def process_name(rawname):
    remove = [' County',' Parish', ' Municipality'] #,' Census Area',' Municipality']
    for item in remove:
        rawname = re.sub(item,'',rawname)
    substitute = [['Dońa Ana','Doña Ana']]
    for pair in substitute:
        rawname = re.sub(pair[0],pair[1],rawname)
    return rawname

for index,item in enumerate(CSV2):
    state = item[5]
    county = item[6]
    county = re.sub('Dońa Ana','Doña Ana',county)
    if item[0] == '050':
        state_county_info[state][county]['pop2019'] = int(item[18])
        fips_id[state_name_to_code[state] + state_county_info[state][county]['fips']] = {
        'name' : county + ', ' + state,
        'state' : state, 'county' : county, 'pop2019' : int(item[18]), 'dpop2019' : int(item[28]), 'adjacent' : []}

    county = [item[5],process_name(item[6])]
    if tuple(county) not in countylist2 and index > 0 and item[0] != '040':
        countylist2[tuple(county)] = int(item[18])


for index,item in enumerate(CSV1):
    if index > 0 and item[3] != '':
        code = fips_int_to_str(int(item[3]))
        #print(fips_id[code])


common_counties = []
one_only = []
for item in countylist1:
    if item in countylist2:
        common_counties.append(item)
        del countylist2[item]
    else:
        one_only.append(item)

raw4 = open('county_adjacency.txt',encoding='cp1250').read()

working_on = None
pattern = re.compile(r'(.*?)"(.*?)".*?(\d\d\d\d\d)')
for result in re.finditer(pattern,raw4):
    if result.group(1) == '':
        working_on = result.group(3)
        if working_on not in fips_id:
            fips_id[working_on] = { 'name' : result.group(2)}
        fips_id[working_on]['adjacent'] = []
    elif working_on is not None:
        if result.group(3) not in fips_id[working_on]['adjacent'] and result.group(3) != working_on:
            fips_id[working_on]['adjacent'].append(result.group(3))

# Verify adjacency:
for item in fips_id:
    for subitem in fips_id[item]['adjacent']:
        if item not in fips_id[subitem]['adjacent']:
            print(item,subitem)


csv5 = 'DEC_10_SF1_GCTPH1.US05PR_with_ann.csv'
raw5 = open(csv5,'r',encoding='cp1250').read()
CSV5 = textmanip.csv_parse(raw5)

for index,item in enumerate(CSV5):
    if index > 3:
        fips = item[4]
        area = item[9]
        land = item[11]
        if len(fips) == 5:
            fips_id[fips]['area_land'] = float(land)
            fips_id[fips]['area_total'] = float(area)

open('fipsdata.py','w').write(str(fips_id))
