
def compute_shift(modified,shift,myliststruct):
    total = 0
    mylist = myliststruct[1]
    mins = myliststruct[0]
    maxs = myliststruct[2]
    for index in range(len(mylist)):
        total += min(max(modified[index]+shift,mins[index]),maxs[index]) - mylist[index]
    return total
def corrected_shift(modified,myliststruct,thresh):
    running = True
    shift = 0
    step = 0.1 / len(myliststruct[1])
    while running:
        offby = compute_shift(modified,shift,myliststruct)
        error = max(offby,-offby)
        if error < thresh:
            running = False
        else:
            shift -= step * offby
    return shift

def regularize(myliststruct,threshold=1e-12):
    # Find smoothest function which has the same integral
    # And differs by at most a fixed percentage at each point
    # 1/2 * \sum_{i=0}^{N-2} (x_i - 2 x_{i+1} + x_{i+2})^2
    mylist = myliststruct[1]
    mins = myliststruct[0]
    maxs = myliststruct[2]
    step = 0.05
    ostep = 1
    initial_sum = sum(mylist)
    running = True
    current = {}
    for index in range(len(mylist)):
        current[index] = mylist[index]
    unconstrained = len(mylist)
    count = 0
    magfactor = 1 # max(mylist)
    while running:
        count += 1
        increments = {}
        for index in range(len(mylist)):
            incr = 0
            if index + 2 < len(mylist):
                incr += current[index] - 2 * current[index+1] + current[index+2]
            if index -1 >= 0 and index + 1 < len(mylist):
                incr += -2 * (current[index-1] - 2 * current[index] + current[index+1])
            if index -2 >= 0:
                incr += current[index-2] - 2 * current[index-1] + current[index]
            increments[index] = incr
        next = {}
        presumed = {}
        for index in range(len(mylist)):
            presumed[index] = current[index] - step * increments[index]
        lagrange = corrected_shift(presumed,myliststruct,threshold * 0.01 * magfactor)
        change = 0
        total = 0
        # We add a constant shift so that the sum is preserved...
        for index in range(len(mylist)):
            presumed_value = presumed[index] + lagrange
            next[index] = min(max(presumed_value,mins[index]),maxs[index])
            total += next[index]
            change = max(max(change,next[index]-current[index]),current[index]-next[index])
        if change < threshold * magfactor:
            running = False
        current = next
        if count % 100 == 0:
            print('Regularize Iteration',change,total-sum(mylist))
    result = []
    for index in range(len(mylist)):
        result.append(current[index])
    return result

def pointwindow(mylist,pointno,pct_diff=0):
    mins = []
    maxs = []
    for index in range(len(mylist)):
        earliest = max(index-pointno+1,0)
        mins.append(min(mylist[earliest:index+1])*(1-pct_diff))
        maxs.append(max(mylist[earliest:index+1])*(1+pct_diff))
        #print(mins[-1],mylist[index],maxs[-1])
    return [mins,mylist,maxs]

if __name__ == '__main__':
    structure = pointwindow([1,2,3,4,6,6,7,8,9,10],2,0.1)
    print(regularize(structure))
