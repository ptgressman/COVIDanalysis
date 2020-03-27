import math,ast,sys


def best_uniform_line(valuelist):
    oscillation = None
    for index1 in range(len(valuelist)):
        for index2 in range(index1+2,len(valuelist)):
            slope = (valuelist[index2] - valuelist[index1]) / (index2 - index1)
            minitp = None
            maxitp = None
            for index3 in range(len(valuelist)):
                itp = valuelist[index3] - slope * index3
                if minitp is None or itp < minitp:
                    minitp = itp
                if maxitp is None or itp > maxitp:
                    maxitp = itp
            osc = maxitp - minitp
            if oscillation is None or osc < oscillation:
                found_slope = slope
                found_itp   = (maxitp + minitp) * 0.5
                oscillation = osc
    return [slope,itp,oscillation]

print(best_uniform_line([1,2,4,8,16,32,64]))
quit()


def dot_product(list1,list2,dim):
    result = 0.0
    for index in range(dim):
        result += list1[index]*list2[index]
    return result
def scalar_mult(list1,scalar):
    result = []
    for number in list1:
        result.append(number*scalar)
    return result
def linear_combo(list1,list2,scalar1,scalar2):
    result = []
    for index in range(len(list1)):
        result.append(scalar1*list1[index]+scalar2*list2[index])
    return result

def extrapolate(list,degree,number,factor):
    longlength = len(list)+number
    vectors = []
    resultvec = [0.0] * longlength
    for index in range(degree+1):
        myvec = []
        for subind in range(longlength):
            if index == 0:
                myvec.append(1.0)
            else:
                myvec.append(subind ** index)
        for prev_vec in vectors:
            dotp = dot_product(prev_vec,myvec,len(list))
            myvec = linear_combo(myvec,prev_vec,1.0,-dotp)
        norm = math.sqrt(dot_product(myvec,myvec,len(list)))
        myvec = scalar_mult(myvec,1/norm)
        vectors.append(myvec)
        dotp = dot_product(list,myvec,len(list))
        if index > 1:
            dotp = dotp * (factor ** (index-1))
        resultvec = linear_combo(resultvec,myvec,1.0,dotp)
    return resultvec

def smooth_it(datalist,global_margin,change_by):
    deriv_sign = 0
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

def delta_smooth(listobj):
    if len(listobj) < 2:
        return listobj
    deltas = [[listobj[0]]]
    for index in range(1,len(listobj)):
        mydelta = listobj[index] - listobj[index-1]
        if len(deltas) == 0:
            deltas.append([mydelta])
        else:
            previous = deltas[-1][-1]
            matches = False
            if previous == 0 and mydelta == 0:
                matches = True
            if previous > 0 and mydelta > 0:
                matches = True
            if previous < 0 and mydelta < 0:
                matches = True
            if matches:
                deltas[-1].append(mydelta)
            else:
                deltas.append([mydelta])
    smoothed_deltas = []
    for batch in deltas:
        if batch[0] == 0:
            smoothed_deltas += batch
        else:
            rawlog = []
            sign = 1
            if batch[0] < 0:
                sign = -1
            for item in batch:
                rawlog.append(math.log(abs(item)))
            result = smooth_it(rawlog,0.1,1e-12)
            for item in result:
                smoothed_deltas.append(sign*math.exp(item))
    final_result = []
    cumulative = 0
    for item in smoothed_deltas:
        cumulative += item
        final_result.append(cumulative)
    return final_result

def smooth_all(dict_obj):
    result = {}
    for item in dict_obj['<rows>']:
        out = delta_smooth(dict_obj[item])
        factor = dict_obj[item][-1]
        if out[-1] != 0:
            factor = factor / out[-1]
        else:
            factor = 1.0
        newout = []
        for number in out:
            newout.append(number * factor)
        result[item] = newout
    result['<rows>'] = dict_obj['<rows>']
    result['<columns>'] = dict_obj['<columns>']
    return result

def extrapolate_all(dict_obj,usethismany,extrapthismany,factor):
    result = {}
    for name in dict_obj['<rows>']:
        numberlist = dict_obj[name]
        should_extrap = True
        lndeltas = []
        for index in range(usethismany):
            delta = numberlist[index-usethismany] - numberlist[index-usethismany-1]
            if delta <= 0:
                should_extrap = False
            else:
                lndeltas.append(math.log(delta))
        if should_extrap:
            extended = extrapolate(lndeltas,2,extrapthismany,factor)  # Quadratic at most
            for index in range(extrapthismany):
                increment = math.exp(extended[usethismany+index])
                numberlist.append(numberlist[-1] + increment)
        result[name] = numberlist
    result['<rows>'] = dict_obj['<rows>']
    result['<columns>'] = dict_obj['<columns>']
    return result

def strip(datadict):
    lastone = len(datadict['<columns>'])-1
    del datadict['<columns>'][lastone]
    for name in datadict['<rows>']:
        del datadict[name][lastone]
    return datadict

if __name__ == '__main__':
    try:
        clip = 0
        if len(sys.argv) > 1:
            clip = int(sys.argv[1])
    except:
        clip = 0

    raw_in = ast.literal_eval(open('archiveNYT/recent.py','r').read())
    forward = 7
    for index in range(clip):
        raw_in = strip(raw_in)
    result = smooth_all(raw_in)
    result = extrapolate_all(result,7,forward,0.75)

    predictions = []
    for placename in result['<rows>']:
        predlist = result[placename]
        if len(predlist) > len(raw_in[placename]):
            predictions.append([-predlist[-1-forward],placename])
    predictions.sort()
    resultstring = ' ' * 16 + raw_in['<columns>'][-1] + '\n'
    for index,item in enumerate(predictions):
        if index < 10:
            mystring = item[1] + ' ' * 17
            resultstring += mystring[0:17] + ' '
            for number in range(forward+1):
                resultstring += '% 8i' % int(result[item[1]][-forward-1+number]+0.4) + ' '
            resultstring += '\n'
    print(resultstring)
