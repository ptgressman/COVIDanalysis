
import os,ast,traceback,re


all_objects = os.listdir()

all_objects.sort()
all_reports = {}
locations = []
observations = []
previous_total = 0
for item in all_objects:
    if item.startswith('states20'):
        print(item,os.path.getctime(item))
        try:
            reports = {}
            file_contents = open(item,'r').read()
            file_contents = re.sub('false','False',file_contents)
            file_contents = re.sub('true','True',file_contents)
            file_contents = re.sub('null','None',file_contents)
            json_object = ast.literal_eval(file_contents)
            total = 0
            for record in json_object['data']:
                if 'Jurisdiction' in record and 'Cases Reported' in record and type(record['Cases Reported']) == int:
                    location = record['Jurisdiction']
                    cases    = record['Cases Reported']
                    reports[location] = cases
                    total += cases
                    if location not in locations:
                        locations.append(location)
            reports['TOTAL'] = total
            if total != previous_total:
                all_reports[item] = reports
                observations.append(item)
                previous_total = total
        except:
            traceback.print_exc()
            jston_object = {}

locations.sort()
observations.sort()

csvtxt = 'source,'

locations.insert(0,'TOTAL')

for place in locations:
    csvtxt += place
    if place != locations[-1]:
        csvtxt += ','
    else:
        csvtxt += '\n'
for line in observations:
    csvtxt += line + ','
    for place in locations:
        if place in all_reports[line]:
            csvtxt += str(all_reports[line][place])
        if place != locations[-1]:
            csvtxt += ','
        else:
            csvtxt += '\n'

csvtxt = csvtxt[0:len(csvtxt)-1]

file = open('summary.csv','w')
file.write(csvtxt)
