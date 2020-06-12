import re,os

def convert_string(thestring):
    result = thestring
    if re.search(r'^-?\d+(,\d\d\d)*(\.\d*)?$',thestring):
        simpler = re.sub(',','',thestring)
        simpler = re.sub('\s','',simpler)
        if re.search(r'\.',thestring):
            result = float(simpler)
        else:
            result = int(simpler)
    return result

def read_tables(**kwargs):
    if 'file' in kwargs:
        file = kwargs['file']
        with open(file,'r') as fileobj:
            filestr = fileobj.read()
    elif 'source' in kwargs:
        filestr = kwargs['source']
    elif 'directory' in kwargs:
        all_items = {}
        for object in sorted(os.listdir(kwargs['directory'])):
            if re.search('html',object):
                kwargs['file'] = os.path.join(kwargs['directory'],object)
                result = read_tables(**kwargs)
                if len(result) > 0:
                    all_items[object] = result
        return all_items


    table_body = re.compile(r'<\s*?tbody[^>]*>(?P<body>(.|\n)*?)<\s*?/tbody\s*?>')
    table_row = re.compile(r'<\s*?tr[^>]*>(?P<row>(.|\n)*?)<\s*?/tr\s*?>')
    table_cell = re.compile(r'<\s*?t[hd][^>]*>(?P<cell>(.|\n)*?)<\s*?/t[hd]\s*?>')
    tag = re.compile(r'<[^>]*>|^\s*|\s*\Z')
    all_tables = []
    for found_table in re.finditer(table_body,filestr):
        table_string = found_table.group('body')
        valid = True
        if 'regexp' in kwargs:
            if type(kwargs['regexp']) == list:
                for item in kwargs['regexp']:
                    if not re.search(item,table_string):
                        valid = False
            else:
                if not re.search(kwargs['regexp'],table_string):
                    valid = False
        if valid:
            this_table = []
            for found_row in re.finditer(table_row,table_string):
                row_string = found_row.group('row')
                this_row = []
                for found_cell in re.finditer(table_cell,row_string):
                    cell_string = found_cell.group('cell')
                    stripped_cell_string = re.sub(tag,'',cell_string)
                    this_row.append(convert_string(stripped_cell_string))
                this_table.append(this_row)
            this_table.append(this_row)
            all_tables.append(this_table)
    return all_tables



def collect_table_data(county_dictionary,**kwargs):
    county_list = []
    for key in county_dictionary:
        county_list += county_dictionary[key]

    all_tables = read_tables(**kwargs,regexp=county_list)
    found = {}
    for county in county_list:
        found[county] = {}
        for table_set in all_tables:
            found[county][table_set] = []
            for table in all_tables[table_set]:
                for row in table:
                    if row[0] == county:
                        savedrow = []
                        for index in range(len(row)):
                            if index in kwargs['save_columns']:
                                savedrow.append(row[index])
                        found[county][table_set].append(tuple(savedrow))
            if len(found[county][table_set]) == 1:
                found[county][table_set] = found[county][table_set][0]
    result = {}
    for county in found:
        for level in county_dictionary:
            for sublevel in range(0,level+1):
                if county in county_dictionary[sublevel]:
                    for filekey in found[county]:
                        if filekey not in result:
                            result[filekey] = {}
                        if type(found[county][filekey]) == tuple:
                            if level not in result[filekey]:
                                result[filekey][level] = found[county][filekey]
                            else:
                                newtuple = []
                                for index in range(len(kwargs['save_columns'])):
                                    if index < len(result[filekey][level]):
                                        start = result[filekey][level][index]
                                    else:
                                        start = 0
                                    if index < len(found[county][filekey]):
                                        start += found[county][filekey][index]
                                    newtuple.append(start)
                                result[filekey][level] = tuple(newtuple)
    return result


county_dictionary = {
0 : ['Delaware'],
1 : ['Chester','Montgomery','Philadelphia'],
2 : ['Bucks','Berks','Lancaster','Lehigh','Northampton']
}

print(collect_table_data(county_dictionary,directory='./archiveOTHER',file_matches='wikiPA.*html',save_columns=[1,2]))
