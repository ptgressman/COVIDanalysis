import urllib.request, urllib.error, urllib.parse
from datetime import datetime
import os, re

url = 'https://www.livescience.com/coronavirus-updates-united-states.html'
datafile = 'collected.txt'

currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year

filename = str(currentYear*10000 + currentMonth * 100 + currentDay) + '.html'

monthtotal = [0,31,29,31,30,31,30,31,31]
daynumber  = 0
for index in range(currentMonth):
    daynumber += monthtotal[index]
daynumber += currentDay

if os.path.exists(filename):
    file = open(filename,'r')
    url_content = file.read()
    file.close
else:
    response = urllib.request.urlopen(url)
    webbytes = response.read()
    url_content = webbytes.decode('utf-8')
    file = open(filename,'w')
    file.write(url_content)
    file.close()


url_content = re.sub(r'\n','',url_content)
url_content = re.sub(r'&nbsp;','',url_content)

header_simple = r"(<h2[^>]*>\s*[\w ]*?\s*</h2>)"
header_string = r"<h2[^>]*>\s*(?P<state>[\w ]*?)\s*</h2>"

resultslist = ''
statename = ''
result = re.split(header_simple,url_content)
for item in result:
    newstate = re.search(header_string,item)
    if newstate is not None:
        statename = newstate.group('state')
    else:
        countylist = re.search(r'<ul>.*?</ul>',item)
        if countylist is not None:
            counties_string = countylist.group(0)
            countyinfo = re.compile(r'<li>\s*(?P<county>[\w ]*?):\s*(?P<number>\d*)')
            for subitem in re.finditer(countyinfo,counties_string):
                countyname = subitem.group('county')
                countynumber = subitem.group('number')
                countyname = re.sub(' (C|c)ounty','',countyname)
                countyname = re.sub('^\s*','',countyname)
                countyname = re.sub('\s*$','',countyname)
                resultslist += filename + ' {' + str(daynumber) + ':' + statename + ':' + countyname + ':' + countynumber + '}\n'

file = open(datafile,'r')
oldresults = file.read()
file.close()
file = open(datafile,'w')
file.write(resultslist)
file.write(oldresults)
file.close()
