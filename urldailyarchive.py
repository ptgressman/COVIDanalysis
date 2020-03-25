import urllib.request, urllib.error, urllib.parse
from datetime import datetime
import os, re

def get_html(url,where_to_save):
    currentDay = datetime.now().day
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    currentHour = datetime.now().hour

    currentPeriod = int(currentHour/6)

    filename = where_to_save + str(currentYear*10000 + currentMonth * 100 + currentDay) + '-' + str(currentPeriod) +  '.html'

    monthtotal = [0,31,29,31,30,31,30,31,31,30,31,30,31]
    daynumber  = 0
    for index in range(currentMonth):
        daynumber += monthtotal[index]
        daynumber += currentDay

    if os.path.exists(filename):
        file = open(filename,'r')
        url_content = file.read()
        file.close()
    else:
        response = urllib.request.urlopen(url)
        webbytes = response.read()
        url_content = webbytes.decode('utf-8')
        file = open(filename,'w')
        file.write(url_content)
        file.close()
    return url_content
