import re

filename = 'collected.txt'

read_pattern = re.compile(r'(?P<description>.*?)\s*{(?P<day>\d*):(?P<state>(\w| )*):(?P<county>(\w| )*):(?P<number>\d*)}')

with open(filename,'r') as file:
    rawtxt = file.read()
    file.close()

records = []
for item in re.finditer(read_pattern,rawtxt):
    descr = item.group('description')
    day   = int(item.group('day'))
    state = item.group('state')
    county = item.group('county')
    number = int(item.group('number'))
    records.append([descr,day,state,county,number])

print(records)
