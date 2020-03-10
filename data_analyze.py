from sympy import *
import textmanip
import re

CSVlocation = "../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
CSVout = "smoothed.csv"

locations = [['Mainland China'],['Delaware County','PA','US'],['PA','US'],[]]


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
        result = smooth_it(shortlist,0.1,2e-5,1)
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


data = all_smoothed(CSV)
big_labels = aggregate_labels(CSV)
