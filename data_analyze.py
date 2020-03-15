from math import *
import textmanip
import re

CSVlocation = "../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
CSVout = "smoothed.csv"

locations = [['Mainland China'],['Delaware County','PA','US'],['PA','US'],[]]

remove = 2

def locator_to_label(locator):
    if len(locator) == 0:
        return 'Worldwide'
    result = ''
    for index, item in enumerate(locator):
        result += item
        if index != len(locator)-1:
            result += ', '
    return result

def label_to_locator(label):
    if label == 'Worldwide':
        return []
    return re.split(', ',label)

def is_subregion_of(smallloc,largeloc):
    if (len(smallloc) < len(largeloc)):
        return False
    if len(largeloc) == 0:
        return True
    for index in range(len(largeloc)):
        if (largeloc[-1-index] != smallloc[-1-index]):
            return False
    return True

def grab_label(CSVline):
    if CSVline[0] == '':
        return CSVline[1]
    else:
        return CSVline[0] + ', ' + CSVline[1]
def grab_locator(CSVline):
    return label_to_locator(grab_label(CSVline))


def all_labels(CSV):
    all_labels = ['Worldwide']
    for index,line in enumerate(CSV):
        if index > 0:
            locator = grab_locator(line)
            while len(locator) > 0:
                label = locator_to_label(locator)
                if label not in all_labels:
                    all_labels.append(label)
                del locator[0]
    return all_labels

def aggregate_labels(CSV):
    all_labels = []
    #all_labels = ['Worldwide']
    for index,line in enumerate(CSV):
        if index > 0:
            locator = grab_locator(line)
            while len(locator) > 0:
                label = locator_to_label(locator)
                if label not in all_labels and len(locator) == 1:
                    if label != 'Others':
                        all_labels.append(label)
                del locator[0]
    return all_labels

def all_smoothed(CSV):
    labellist = all_labels(CSV)
    data = {}
    data['date'] = date_list(CSV)
    for label in labellist:
        locator = label_to_locator(label)
        print('Computing',label)
        result = get_smoothed_cumulative(locator,CSV)
        data[label] = result
    return data

def date_list(CSV):
    datalist = []
    line = CSV[0]
    for index in range(len(line)-4):
        datalist.append(line[index+4])
    return datalist

def get_cumulative(locator,CSVdat):
    datalist = []

    for line in CSVdat:
        if len(datalist) == 0:
            for index in range(len(line)-4):
                datalist.append(0)
        valid = False
        if is_subregion_of(grab_locator(line),locator):
            valid = True
        if valid:
            for index,data in enumerate(line):
                data = textmanip.atof(data)
                if (index >= 4) and (type(data) != str):
                    datalist[index-4] += data
                    if (index == len(line)-1):
                        print(grab_locator(line),data,datalist[index-4])
    if locator == ['US']:
        print(datalist)
        quit()
    return datalist

def get_smoothed_cumulative(locator,CSVdat):
    datalist = get_cumulative(locator,CSVdat)
    started = 0
    shortlist = []
    for index in range(len(datalist)):
        if (datalist[index] >= 1) and (started == 0):
            started = index
        if (started > 0 and datalist[index] >= 1):
            shortlist.append(ln(datalist[index]))
        if (datalist[index] < 1) and (started > 0):
            started = 0
            shortlist = []
    if len(shortlist) > 3:
        result = smooth_it(shortlist,0.1,2e-3,1)
        for index in range(len(result)):
            datalist[started+index] = exp(result[index])
    return datalist



def smooth_it(datalist,global_margin,change_by,deriv_sign = 0,logarithmic=False):
    stepfact = 0.04
    count_limit = 5000
    datadict = {}
    for index,item in enumerate(datalist):
        datadict[index] = item
    size = len(datalist)
    datadict[-1] = datadict[0]
    datadict[size] = datadict[size-1]
    running = True
    count = 0
    while running:
        update = {}
        # Boundary conditions: Endpoint values fixed, linear extrapolation for slope
        datadict[-1] = 2* datadict[0] - datadict[1]
        datadict[size] = 2 * datadict[size-1] - datadict[size-2]
        update[0] = datadict[0]
        update[size-1] = datadict[size-1]
        for delta_ind in range(1,size-1):
            margin = global_margin
            if (logarithmic):
                margin = margin * datalist[delta_ind]
            update[delta_ind] = datadict[delta_ind] + stepfact * (-6 * datadict[delta_ind] + 4 * (datadict[delta_ind+1] + datadict[delta_ind-1]) - (datadict[delta_ind+2] + datadict[delta_ind-2]))
            if (update[delta_ind] > margin + datalist[delta_ind]):
                update[delta_ind] = margin + datalist[delta_ind]
            elif (update[delta_ind] < -margin + datalist[delta_ind]):
                update[delta_ind] = -margin + datalist[delta_ind]
            if (update[delta_ind] < update[delta_ind-1]) and (deriv_sign > 0):
                update[delta_ind] = update[delta_ind-1]
            elif (update[delta_ind] > update[delta_ind-1]) and (deriv_sign < 0):
                update[delta_ind] = update[delta_ind-1]
            if (update[delta_ind] > datadict[delta_ind+1]) and (deriv_sign > 0):
                update[delta_ind] = datadict[delta_ind+1]
            elif (update[delta_ind] < datadict[delta_ind+1]) and (deriv_sign < 0):
                update[delta_ind] = datadict[delta_ind+1]
        count += 1
        change = 0
        for delta_ind in range(size):
            diff = datadict[delta_ind] - update[delta_ind]
            diff = max(diff,-diff)
            change = max(diff,change)
            datadict[delta_ind] = update[delta_ind]
        if (count >= count_limit) or (change < change_by):
            running = False

    newlist = []
    for delta_ind in range(size):
        newlist.append(datadict[delta_ind])
    return newlist

with open(CSVlocation,"r") as file:
    rawdata = file.read()
    file.close()

CSV = textmanip.csv_parse(rawdata)
print(len(CSV))
for index in range(len(CSV)):
    for clip in range(-remove,0):
        del CSV[index][clip]
atrow = 1
running = True
while running:
    nonzero = False
    for index in range(4,len(CSV[atrow])):
        if int(CSV[atrow][index]) > 0:
            nonzero = True
    if nonzero:
        atrow += 1
    else:
        del CSV[atrow]
    if atrow == len(CSV):
        running = False
print(len(CSV))
my_aggregate_data = {}

# USA

USstateslist = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut',
'Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas',
'Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota',
'Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey',
'New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon',
'Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas',
'Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming','District of Columbia','District of Columbia']
USstatesabbr = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL',
'IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH',
'NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA',
'WA','WV','WI','WY','DC','D.C.']

found_states = []
state_indices = {}
other_indices = []
parent_index = []
for_import = []
for index,item in enumerate(CSV):
    if item[0] in USstateslist:
        if item[0] in found_states:
            print('ERROR : Apparent Duplicate',item[0])
        found_states.append(item[0])
        print('ADDING: Found record for',item[0])
        state_indices[item[0]] = index
for index,item in enumerate(CSV):
    if item[1] == 'US':
        if item[0] not in USstateslist:
            re_abbrev = re.search(r', ([A-Z]\.?[A-Z]\.?)',item[0])
            if re_abbrev is not None:
                abbrev = re_abbrev.group(1)
                if abbrev in USstatesabbr:
                    statename = USstateslist[USstatesabbr.index(abbrev)]
                    prefixsearch = re.search(r'([^,]*),',item[0])
                    if prefixsearch is not None:
                        prefixname = prefixsearch.group(1)
                        prefixname = re.sub(' County','',prefixname)
                        for_import.append([index,statename,prefixname])
                    if statename not in found_states:
                        print('ADDING: Found record for',item[0])
                        other_indices.append(index)
                        parent_index.append(-1)
                    else:
                        print('SUBREC: Record for',item[0])
                        other_indices.append(index)
                        parent_index.append(state_indices[statename])
                else:
                    print('ERROR : Not sure about',item[0])
                    other_indices.append(index)
                    parent_index.append(-1)
            else:
                print('ADDING: Found record for',item[0])
                other_indices.append(index)
                parent_index.append(-1)


# export_report = ''
# for item in for_import:
#     for index in range(len(CSV[item[0]])):
#         if index > 3:
#             cellval = int(CSV[item[0]][index])
#             if cellval > 0:
#                 outstr = '{' + str(index-4+22) + ':' + item[1] + ':' + item[2] + ':' + str(cellval) + '}'
#                 export_report += 'JHU 03-09-20 ' + outstr + '\n'
# file = open('jhu_export.txt','w')
# file.write(export_report)
# file.close()

my_aggregate_data['US'] = []
my_aggregate_smoothlog = {}
for index in range(len(CSV[0])):
    if (index > 3):
        total = 0
        for state in state_indices:
            total += int(CSV[state_indices[state]][index])
        for whichone,lineno in enumerate(other_indices):
            if parent_index[whichone] < 0 or int(CSV[parent_index[whichone]][index]) == 0:
                total += int(CSV[lineno][index])
        my_aggregate_data['US'].append(total)

nation_dict = {}
for index,item in enumerate(CSV):
    if item[1] != 'US' and index > 0:
        if item[1] not in nation_dict:
            nation_dict[item[1]] = []
        nation_dict[item[1]].append(index)

for name in nation_dict.keys():
    my_aggregate_data[name] = []
    for index in range(len(CSV[0])):
        if (index > 3):
            total = 0
            for line in nation_dict[name]:
                total += int(CSV[line][index])
            my_aggregate_data[name].append(total)

for name in my_aggregate_data:
    started = False
    start_index = 0
    for index in range(len(my_aggregate_data[name])):
        if not started and my_aggregate_data[name][index] > 0:
            start_index = index
            started = True
        elif started and my_aggregate_data[name][index] == 0:
            started = False
    shortlist = []
    if started:
        for index in range(start_index,len(my_aggregate_data[name])):
            shortlist.append(log(my_aggregate_data[name][index]))
        if len(shortlist) > 3:
            print('Smoothing',name)
            result = smooth_it(shortlist,0.1,1e-12,1)
        else:
            result = shortlist
        my_aggregate_smoothlog[name] = []
        for index in range(start_index):
            my_aggregate_smoothlog[name].append(-999999)
        for index in range(len(result)):
            my_aggregate_smoothlog[name].append(result[index])

my_aggregate_smoothlog['date'] = date_list(CSV)
my_aggregate_data['date'] = date_list(CSV)

#data = all_smoothed(CSV)
#big_labels = aggregate_labels(CSV)
