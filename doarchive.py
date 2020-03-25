archive_todo = 'archiveconfig.py'
archive_root = '' # Don't put the final slash; I'll do that myself

import ast
import urldailyarchive
import sys,traceback

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

for paramdict in tasklist:
    if archive_root != '':
        paramdict['root'] = archive_root
    try:
        urldailyarchive.get_asset(paramdict)
        print('='*80)
        print('SUCCESS:',paramdict)
    except:
        print('='*80)
        print('ERROR: Failed archive of',paramdict)
        print('-'*80)
        traceback.print_exc()
