import ast,re,traceback,os
from datetime import datetime

outfile = 'recent.py'

variable_names = ['countries_raw', 'us_counties', 'ts']

all_objects = os.listdir()
file = ''
ctime = 0
options = []
for item in all_objects:
    myctime = os.path.getctime(item)
    if item.startswith('model'):
        options.append(item)
    if item.startswith('model') and myctime > ctime:
        file = item
        ctime = myctime
options.sort(reverse=True)
file = options[0]

text = open(file,'r').read()

data = {}
forbidden = ['http','https']
attributes = []
pattern = re.compile(r'\s([a-zA-Z0-9_]*):')
for result in re.finditer(pattern,text):
    if result.group(1) not in attributes and result.group(1) not in forbidden:
        attributes.append(result.group(1))
for item in attributes:
    text = re.sub(r'\s'+ item + ':', ' "' + item + '":',text)

for item in variable_names:
    try:
        subtext = re.search(r'var '+ item + ' = ((.|\n)*?)];',text).group(1) + ']'
        result = ast.literal_eval(subtext)
        print(item,len(result))
        data[item] = result
    except:
        print("ERROR: Couldn't parse",item)
        traceback.print_exc()


time_series = {}
id_to_name = {}
days = []
locales = []
for item in data['countries_raw']:
    id_to_name[item['adm0_a3']] = item['nyt_name']

for item in data['ts']:
    name = id_to_name[item['adm0_a3']]
    datadict = {}
    for subitem in item['data']:
        date = subitem['date']
        confirmed = subitem['confirmed']
        recovered = subitem['recovered']
        deaths    = subitem['deaths']
        datadict[date] = confirmed
        if date not in days:
            days.append(date)
        if name not in locales:
            locales.append(name)
    time_series[name] = datadict

days.sort()
locales.sort()

datapack = {}
used_locales = []
for place in locales:
    list = []
    should_post = False
    for item in days:
        if item != days[-1]:
            if item in time_series[place]:
                list.append(time_series[place][item])
                should_post = True
            else:
                list.append(0)
    if should_post:
        datapack[place] = list
        used_locales.append(place)
datapack['<rows>'] = used_locales
datapack['<columns>'] = days[0:len(days)-1]

with open(outfile,'w') as file:
    file.write(str(datapack))
    file.close()

print('SUCCESS!')
