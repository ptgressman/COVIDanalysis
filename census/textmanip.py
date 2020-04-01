import re

def charstring(input):
    valid_chars = '1awx3drv5gyn7ji9lp'
    size = len(valid_chars)
    number = input + 1000 * input + 1000000
    result = ''
    while number > 0:
        result += valid_chars[number % size]
        number = int ((number-(number % size))/size)
    return result

def csv_parse(mystring):
    csvgrid = []
    tokens = []
    instring = False
    quote_streak_length = 0
    token = ''
    for index in range(len(mystring)):
        thischar = mystring[index]
        if thischar == '\"':
            quote_streak_length += 1
        if instring:
            if quote_streak_length % 2 == 0 and (index == len(mystring)-1 or mystring[index+1] != '\"'):
                quote_streak_length = 0
                instring = False
            elif thischar == '\"':
                if index > 0 and mystring[thischar-1] == '\"':
                    token += '\"'
            else:
                if thischar.isprintable() or thischar == '\t' or thischar == '\n':
                    token += thischar
        elif thischar == '\"':
            instring = True
            quote_streak_length = 1
            token = ''
        elif thischar == ',':
            tokens.append(token)
            token = ''
        elif thischar == '\n':
            tokens.append(token)
            csvgrid.append(tokens)
            token = ''
            tokens = []
        elif thischar.isprintable() or thischar == '\t' or thischar == '\n':
            token += thischar
    if len(token) != 0:
        tokens.append(token)
    if len(tokens) > 0:
        csvgrid.append(tokens)
    for rind in range(len(csvgrid)):
        for cind in range(len(csvgrid[rind])):
            csvgrid[rind][cind] = re.sub(r'^\s*','',csvgrid[rind][cind])
            csvgrid[rind][cind] = re.sub(r'\s*$','',csvgrid[rind][cind])
    return csvgrid

def csvescape(thisobj):
    thisstring = str(thisobj)
    shouldquote = False
    if re.search('\n|,|"',thisstring):
        shouldquote = True
    result = re.sub(r'"',r'""',thisstring)
    if shouldquote:
        result = '"' + result + '"'
    return result

def to_csv(grid):
    result = ''
    for index,row in enumerate(grid):
        for colindex,cell in enumerate(row):
            result += csvescape(cell)
            if colindex != len(row) - 1:
                result += ','
        if index != len(grid) - 1:
            result += '\n'
    return result

def is_numerical(stringitem):
    stringitem = re.sub(r'^\s*','',stringitem)
    stringitem = re.sub(r'\s*$','',stringitem)

    try:
        value = float(stringitem)
        return True
    except:
        if stringitem[-1] == '%' and len(stringitem) > 1:
            return is_numerical(stringitem[0:len(stringitem)-1])
    return False

## SORTING: From https://stackoverflow.com/questions/5967500

def atof(text):
    try:
        retval = float(text)
    except ValueError:
        retval = text
    return retval

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    float regex comes from https://stackoverflow.com/a/12643073/190597
    '''
    return [ atof(c) for c in re.split(r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)', text) ]

alist=[
    "something1",
    "something2",
    "something1.0",
    "something1.25",
    "something1.105"]
