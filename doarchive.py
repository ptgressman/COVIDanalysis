archive_todo = 'archiveconfig.py'
archive_root = '' # Don't put the final slash; I'll do that myself

import ast
import urldailyarchive
import sys,traceback,re

def check_nyt(urltxt,paramdict):
    #https://static01.nyt.com/newsgraphics/2020/01/21/china-coronavirus/e3cfc76272e8c29a1a3d08188df4bdd96c57e263/build/js/chunks/model-lite.js
    if re.search(r'www\.nytimes\.com',paramdict['url']) is None:
        return None
    foundit = re.search('window.NYTG.ASSETS = "(.*?)"',urltxt)
    if foundit:
        newurl = foundit.group(1) + 'build/js/chunks/model-lite.js'
        record = {}
        record['url'] = newurl
        record['archive'] = 'archiveNYT/model'
        record['checktimes'] = paramdict['checktimes']
        record['extension'] = '.js'
        return record
    else:
        return None

def check_who(urltxt,paramdict):
    if re.search(r'www\.who\.int/emergencies',paramdict['url']) is None:
        return None
    foundit = re.search(r'[-\w/]*\d*-sitrep-\d*-covid-19.pdf',urltxt)
    if foundit:
        record = {}
        record['url'] = 'https://www.who.int' + foundit.group(0)
        record['archive'] = 'archiveWHO/sitrep'
        record['checktimes'] = paramdict['checktimes']
        record['extension'] = '.pdf'
        record['binary'] = True
        return record
    else:
        return None

if len(sys.argv) > 1:
    archive_root = sys.argv[1]

try:
    filename = archive_todo
    if archive_root != '':
        filename = archive_root + '/' + filename
    filedat = open(filename,'r').read()
    tasklist = ast.literal_eval(filedat)
except:
    tasklist = []
    print('ERROR: Failed read of ' + filename + '.')

index = 0
while index < len(tasklist):
    paramdict = tasklist[index]
    index += 1
    if archive_root != '':
        paramdict['root'] = archive_root
    try:
        result_data = urldailyarchive.get_asset(paramdict)
        try:
            dynamic = check_nyt(result_data,paramdict)
        except:
            dynamic = None
        if dynamic is not None:
            tasklist.append(dynamic)
        try:
            dynamic = check_who(result_data,paramdict)
        except:
            dynamic = None
        if dynamic is not None:
            tasklist.append(dynamic)
        print('='*80)
        print('SUCCESS:',paramdict)
    except:
        print('='*80)
        print('ERROR: Failed archive of',paramdict)
        print('-'*80)
        traceback.print_exc()
