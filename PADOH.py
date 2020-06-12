import subprocess,re,os,ast
import urllib.request, urllib.error, urllib.parse

pa_health_url = 'https://www.health.pa.gov/topics/disease/coronavirus/Pages/Cases.aspx'
pa_base_url = 'https://www.health.pa.gov'
local_dir = './archivePADOH/'
processed_records = './archivePADOH/summary.py'
overwrite = False
def gsTextExtract(filename):
    process = subprocess.run(['gs','-dBATCH','-dNOPAUSE','-sDEVICE=txtwrite','-o','-',filename],capture_output=True)
    stdout = process.stdout.decode('utf-8')
    return stdout
def get_report_date(filename,format):
    datefmt = re.compile(format)
    result = re.search(datefmt,filename)
    stdfmt = '%4i-%02i-%02i' % (int(result.group('Y')),int(result.group('M')),int(result.group('D')))
    return stdfmt
def extractCountyCases(localfilename):
    allresults = []
    text = gsTextExtract(localfilename)
    linepattern = re.compile(r'(\w+)\s*(\w\w)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)')
    for result in re.finditer(linepattern,text):
        capture = []
        for index in [1,3,6]:
            piece = result.group(index)
            if index > 2:
                piece = int(piece)
            capture.append(piece)
        allresults.append(capture)
    return allresults
def extractDeathCount(localfilename):
    all_results = []
    text = gsTextExtract(localfilename)
    linepattern = re.compile(r'([A-Za-z]+)\s+([,\d]+)\s+[,\d]+')
    for result in re.finditer(linepattern,text):
        capture = []
        capture.append(result.group(1))
        piece = int(re.sub(',','',result.group(2)))
        capture.append(piece)
        all_results.append(capture)
    return all_results

def getPADOH():
    scraped = {}
    datestamp = {}
    response = urllib.request.urlopen(pa_health_url)
    webContent = response.read().decode('utf-8')
    linkpattern = re.compile(r'<a href="([^"]+pdf)"')
    for result in re.finditer(linkpattern,webContent):
        foundpdfurl = pa_base_url + result.group(1)
        filename = result.group(1)
        filename = re.sub(r'%20',' ',filename)
        filename = re.sub(r'^.*/', '',filename)
        localfilename = local_dir + filename
        extractor = None
        if re.search('County Case',filename):
            extractor = extractCountyCases
            keyword = 'case'
            dfmt = r'(?P<M>\d+)-(?P<D>\d+)-(?P<Y>\d\d\d\d)'
        if re.search('Death by County',filename):
            extractor = extractDeathCount
            keyword = 'death'
            dfmt = r'(?P<Y>\d\d\d\d)-(?P<M>\d+)-(?P<D>\d+)'
        if extractor is not None:
            if not os.path.exists(localfilename):
                response = urllib.request.urlopen(foundpdfurl).read()
                file = open(localfilename,'wb').write(response)
            try:
                scraped_data = extractor(localfilename)
                scrapedict = {}
                datestamp[keyword] = get_report_date(localfilename,dfmt)
                for item in scraped_data:
                    scrapedict[item[0]] = item[1:len(item)]
                scraped[keyword] = scrapedict
            except:
                print('Extraction Failed',localfilename)
    final = {}
    for key in scraped['death']:
        deathresult = scraped['death'][key]
        caseresult = scraped['case'][key.upper()]
        final[key] = caseresult + deathresult
    datestamp['records'] = final

    try:
        file = open(processed_records,'r')
        filetxt = file.read()
        file.close()
        hydrated = ast.literal_eval(filetxt)
    except:
        if not overwrite:
            raise
        else:
            hydrated = []
    duplicate = False
    for item in hydrated:
        if item['case'] == datestamp['case'] and item['death'] == datestamp['death']:
            duplicate = True
            break
    if not duplicate:
        hydrated.append(datestamp)
    file = open(processed_records,'w')
    file.write(str(hydrated))
    file.close()

    return datestamp

if __name__ == '__main__':
    getPADOH()
