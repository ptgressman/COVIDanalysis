# int (x+d) e^{t x} x = 0..r
# [e^{tr} (td + tr - 1) + (-td + 1)] t^{-2}

# (x+d) (e^{tx}-1) t^{-1} |_0^r - (e^{tx} - tx - 1) t^{-2} |_0^r
# (r+d) r (rt)^{-1} (e^{tr} - 1) - r^2 (rt)^{-2} (e^{tr} - tr - 1)


def exp(t,k=0): # only valid for k = 0,1,2
    if k == 0:
        if t < 0:
            return 1.0/exp(-t)
        if t >= 2:
            tempval = exp(t * 0.5)
            return tempval * tempval
        if t >= 1:
            return exp(t-1) * 2.718281828459045235
    if t > 1 or t < -1:
        if k == 1:
            return (exp(t,0) - 1.0)/t
        if k == 2:
            return (exp(t,0) - 1.0 - t)/(t*t)
    count = 0
    term = 1.0
    while count < k:
        count += 1
        term /= count
    total = term
    while term > 1e-23 or term < -1e-23:
        count += 1
        term = term * t / count
        total += term
    return total

def special_integral(startval,rate,timelength):
    dummy = rate*timelength
    return ((startval + timelength) * exp(dummy,1) - timelength * exp(dummy,2))*timelength

def special_sum(startval,rate,timesteps):
    factor = exp(rate,0)
    collected = factor
    total = 0
    for index in range(timesteps):
        total += (index+1+startval) * collected
        collected *= factor
    return total
def generate_sequence(startval,rate,timesteps):
    factor = exp(rate,0)
    collected = factor
    result = []
    for index in range(timesteps):
        result.append((index+1+startval) * collected)
        collected *= factor
    return result

def findrate(startval,integral,timelength):
    guessrate_low = 0
    check = special_sum(startval,guessrate_low,timelength)
    while check > integral:
        guessrate_low -= 1
        guessrate_low *= 2
        check = special_sum(startval,guessrate_low,timelength)
        if guessrate_low < -100:
            return [0] * timelength
    guessrate_high = 0
    check = special_sum(startval,guessrate_high,timelength)
    while check <= integral:
        guessrate_high += 1
        guessrate_high *= 2
        check = special_sum(startval,guessrate_high,timelength)
    for iteration in range(40):
        guessrate_mid = (guessrate_low+guessrate_high)*0.5
        check = special_sum(startval,guessrate_mid,timelength)
        if check < integral:
            guessrate_low = guessrate_mid
        else:
            guessrate_high = guessrate_mid
    return generate_sequence(startval,guessrate_mid,timelength)

def smoothit(dataseries,chunksize):
    mismatch = len(dataseries) % chunksize
    newseries = []
    if mismatch > 0:
        mismatch = chunksize - mismatch
        newseries = [0] * mismatch
    # mismatch = how many datapoints need to be added to make a multiple
    newseries = newseries + dataseries
    windows = int(len(newseries)/chunksize)
    chunks = [[]]
    for index in range(len(newseries)):
        if len(chunks[-1]) == chunksize:
            chunks.append([])
        chunks[-1].append(newseries[index])
    smoothed = []
    startval = 0
    for chunk in chunks:
        total = sum(chunk)
        result = findrate(startval,total,chunksize)
        startval = result[-1]
        for value in result:
            smoothed.append(int(value + 0.5))
    return smoothed[mismatch:len(smoothed)]

def nextstep(position,step,listsize):
    if step < 0:
        nextstep = -step
    else:
        nextstep = -(step + 1)
    if position + nextstep >= 0 and position + nextstep < listsize:
        return nextstep
    if nextstep < 0:
        nextstep = -nextstep
    else:
        nextstep = -(nextstep + 1)
    if position + nextstep >= 0 and position + nextstep < listsize:
        return nextstep
    return None

def oldnextstep(position,step,listsize):
    step = step -1
    if position + step < 0:
        return None
    return step

def slope_inside(lowerbound,upperbound,atindex):
    if atindex == 0:
        return 0
    min_slope = lowerbound[atindex] - upperbound[atindex-1]
    max_slope = upperbound[atindex] - lowerbound[atindex-1]
    step = -1
    while True:
        step = nextstep(atindex,step,len(lowerbound))
        if step is None:
            return 0.5 * (max_slope + min_slope)
        newmin = (lowerbound[atindex+step] - upperbound[atindex])/step
        newmax = (upperbound[atindex+step] - lowerbound[atindex])/step
        if step < 0:
            temp = newmin
            newmin = newmax
            newmax = temp
        if newmin > max_slope or newmax < min_slope:
            return 0.5 * (max_slope + min_slope)
        else:
            min_slope = max(min_slope,newmin)
            max_slope = min(max_slope,newmax)

def minmax(dataseries,timescale):
    length = len(dataseries)
    minlist = [0] * length
    maxlist = [0] * length
    for index in range(length):
        minlist[index] = dataseries[index]
        maxlist[index] = dataseries[index]
    for index in range(length):
        for lookahead in range(1,timescale):
            if index + lookahead < length:
                first = dataseries[index]
                last = dataseries[index+lookahead]
                for midpoint in range(1,lookahead):
                    average = (first * (lookahead - midpoint) + last * midpoint)/lookahead
                    minlist[index+midpoint] = min(minlist[index+midpoint],average)
                    maxlist[index+midpoint] = max(maxlist[index+midpoint],average)
    return [minlist,maxlist]

def differentiate(lowerdata,upperdata):
    result = []
    localmin = []
    localmax = []
    for index in range(len(lowerdata)):
        if index == 0:
            result.append(0)
        else:
            localmin.append(lowerdata[index])
            localmax.append(upperdata[index])
            result.append(slope_inside(lowerdata,upperdata,index))
    return result
