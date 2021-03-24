import ast,re,math

file = open('./archiveEUCDC/20200702-1.json').read()

gathered = []
file = re.sub('null','None',file)
offset = {'day' : 1, 'month' : 100, 'year' : 10000}
pattern = re.compile(r'{[^{}]*}')
for result in re.finditer(pattern,file):
    dict_string = result.group(0)
    dict_obj = ast.literal_eval(dict_string)
    number = 0
    for field in ['day','month','year']:
        dict_obj[field] = int(dict_obj[field])
        number += offset[field] * dict_obj[field]
    dict_obj['datecode'] = number
    if dict_obj['datecode'] == 20200426:
        dict_obj['cases'] = 29000
    if dict_obj['countryterritoryCode'] == 'USA' and dict_obj['datecode'] >= 20200301:
        gathered.append([dict_obj['datecode'],dict_obj['cases']])

gathered.sort()

print(gathered)

data = []
for item in gathered:
    if item[1] > 35000:
        print(item[0],item[1])
    data.append(item[1])

print(data)

weeks = int(len(data)/7)

with open('downsample.csv','w') as file:
    for index in range(weeks):
        bundle = str(index) + ','
        for day in range(7):
            bundle += str(data[index*7+day]) + ','
        file.write(bundle + '\n')

for period in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]:
    residual = 0
    for index in range(len(data)):
        if index + period < len(data):
            residual += abs(data[index]-data[index+period])/period
    print(period,residual)
