import urllib.request, urllib.error, urllib.parse
from datetime import datetime
import os, re

def get_asset(paramdict):
    url = paramdict['url']
    if 'extension' in paramdict:
        ext = paramdict['extension']
    else:
        ext = '.html'
    currentDay = datetime.now().day
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    currentHour = datetime.now().hour

    currentPeriod = int(currentHour/6)
    if 'checktimes' in paramdict and currentPeriod not in paramdict['checktimes']:
        return None
    where_to_save = ''
    if 'archive' in paramdict:
        where_to_save = paramdict['archive']
    if 'root' in paramdict and paramdict['root'] != '':
        where_to_save = paramdict['root'] + '/' + where_to_save

    filename = where_to_save + str(currentYear*10000 + currentMonth * 100 + currentDay) + '-' + str(currentPeriod) +  ext

    monthtotal = [0,31,29,31,30,31,30,31,31,30,31,30,31]
    daynumber  = 0
    for index in range(currentMonth):
        daynumber += monthtotal[index]
        daynumber += currentDay

    if os.path.exists(filename):
        if 'binary' not in paramdict or paramdict['binary'] == False:
            file = open(filename,'r')
            url_content = file.read()
            file.close()
        else:
            url_content = ''
    else:
        print('REQUE',url)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        myreq = urllib.request.Request(url=url,headers=headers)
        response = urllib.request.urlopen(myreq)
        print('OPENED',url)
        webbytes = response.read()
        print(len(webbytes))
        if 'binary' not in paramdict or paramdict['binary'] == False:
            url_content = webbytes.decode('utf-8')
            writestr = 'w'
        else:
            url_content = webbytes
            writestr = 'wb'
        print('RETRV',url)
        file = open(filename,writestr)
        file.write(url_content)
        file.close()
    return url_content


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
