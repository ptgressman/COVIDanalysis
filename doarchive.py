archive_todo = ['configCDC.txt','configCDC2.txt','configCDC3.txt','configCDC4.txt','configLiveSci.txt','configNYT.txt']
archive_root = '' # Don't put the final slash; I'll do that myself

import ast
import urldailyarchive
import sys

if len(sys.argv) > 1:
    archive_root = sys.argv[1]

for item in archive_todo:
    try:
        filename = item
        if archive_root != '':
            filename = archive_root + '/' + filename
        filedat = open(filename,'r').read()
        paramdict = ast.literal_eval(filedat)
        if paramdict['archive'][-1] != '/':
            paramdict['archive'] = paramdict['archive'] + '/'
        if archive_root != '':
            paramdict['archive'] = archive_root + '/' + paramdict['archive']
    except:
        paramdict = {'url' : None}
        print('ERROR: Failed read of ' + item + '.')
    try:
        if paramdict['url'] is not None:
            urldailyarchive.get_html(paramdict['url'],paramdict['archive'])
    except:
        print('ERROR: Failed archive of ' + item + ' ' + paramdict['url'])
