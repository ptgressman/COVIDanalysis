import random,math
import matplotlib
import matplotlib.pyplot as plt

class CustomDistribution(object):
    def __init__(self):
        self.probabilities = []
        self.points = []
        self.search_tree = {}
        self.indexed = False
        self.intensity = 1.0
        self.poisson_size = 0
        self.poisson_calls = 0
    def average(self):
        if self.poisson_calls == 0:
            return 0
        else:
            return self.poisson_size/self.poisson_calls
    def add(self,item,probability):
        self.indexed = False
        self.probabilities.append(probability)
        self.points.append(item)
    def startup(self,mystart = 0.0,myprob=None,mypoints=None):
        total = mystart
        toplevel = False
        if myprob is None:
            myprob = self.probabilities
            mypoints = self.points
            toplevel = True
            print('INFO : Indexing Probability Distribution for Fast Access')
        if len(myprob) < 3:
            result = {'cutoff' : [], 'result' : []}
            for index,value in enumerate(myprob):
                total += value
                result['cutoff'].append(total)
                result['result'].append(mypoints[index])
            return result
        middle_cutoff = int(len(myprob)/2)  # First half is 0...Middle_Index-1 inclusive
        total = mystart
        for index in range(middle_cutoff):
            total += myprob[index]
        result = {'cutoff' : [], 'branch' : []}
        result['cutoff'].append(total)
        result['branch'].append(self.startup(mystart,myprob[0:middle_cutoff],mypoints[0:middle_cutoff]))
        result['branch'].append(self.startup(total,myprob[middle_cutoff:len(myprob)],mypoints[middle_cutoff:len(myprob)]))
        total = result['branch'][-1]['cutoff'][-1]
        result['cutoff'].append(total)
        if toplevel:
            self.search_tree = result
            self.indexed = True
            print('INFO : Done.')
        return result
    def __getitem__(self,realindex):
        mytree = self.search_tree
        if realindex > mytree['cutoff'][-1]:
            return None
        while True:
            arm = 0
            while realindex > mytree['cutoff'][arm]:
                arm += 1
            if 'branch' not in mytree:
                return mytree['result'][arm]
            else:
                mytree = mytree['branch'][arm]
    def random(self):
        if not self.indexed:
            self.startup()
        mymax = self.search_tree['cutoff'][-1]
        where = random.random()* mymax
        return self[where]
    def poisson(self,modintensity = None):
        if modintensity is not None:
            intensity = modintensity
        else:
            intensity = self.intensity
        if intensity <= 3.0:
            p_for_multiplicity = random.random()
            p_now = math.exp(-intensity)
            p_cumulative = p_now
            how_many = 0
            while p_for_multiplicity > p_cumulative:
                how_many += 1
                p_now *= intensity / how_many
                p_cumulative += p_now
            result = {}
            for draws in range(how_many):
                neighbor = self.random()
                if neighbor not in result:
                    result[neighbor] = 0
                result[neighbor] += 1
        else:
            divisor = int(intensity)
            result = {}
            for subdraws in range(divisor):
                subresult = self.poisson(intensity/divisor)
                for neighbor in subresult:
                    if neighbor not in result:
                        result[neighbor] = 0
                    result[neighbor] += subresult[neighbor]
        self.poisson_size += len(result)
        self.poisson_calls += 1
        return result
    def powerlaw(self,size,power,intensity):
        self.probabilities = []
        self.points = []
        self.intensity = intensity
        self.poisson_size = 0
        self.poisson_calls = 0
        start = -int((size-1)/2)
        for index1 in range(start,size+start):
            for index2 in range(start,size+start):
                if index1 != 0 or index2 != 0:
                    p = 0.0
                    for subindex1 in range(-1,2):
                        for subindex2 in range(-1,2):
                            p += 1/((index1+size*subindex1)**2+(index2+size*subindex2)**2)**(power/2)
                    self.add((index1,index2),p)
        self.startup()
        return self


class TorusArray(object):
    def __init__(self,size):
        self.size = size
        self.data = []
        for index in range(size):
            self.data.append([])
            for subindex in range(size):
                self.data[index].append(None)
        self.power = 3.5
        self.intensity = 3.0
        self.low_distribution = CustomDistribution()
        self.high_distribution = self.low_distribution
#        self.high_distribution = CustomDistribution().powerlaw(size,self.power,self.intensity)
#        self.low_distribution = CustomDistribution().powerlaw(size,5.0,2.314)
        self.profile = [0.0,0.0,0.05,0.1,0.15,0.23,0.18,0.14,0.075,0.05,0.025]
    def show(self):
        fig, ax = plt.subplots()
        im = ax.imshow(self.data)
        plt.show()
    def __getitem__(self,key):
        index0 = ((key[0] % self.size) + self.size) % self.size
        index1 = ((key[1] % self.size) + self.size) % self.size
        return self.data[index0][index1]
    def __setitem__(self,key,value):
        index0 = ((key[0] % self.size) + self.size) % self.size
        index1 = ((key[1] % self.size) + self.size) % self.size
        self.data[index0][index1] = value
    def set_all(self,value):
        for index0 in range(self.size):
            for index1 in range(self.size):
                self.data[index0][index1] = value
    def run(self,switchat = -1):
        profile = self.profile
        self.set_all(0)
        infected = [(int(self.size/2),int(self.size/2))]
        statistics = [1]
        self[0,0] = 1
        count = 0
        recent_infections = [infected]
        recent_total = 1
        total = 1
        distribution = self.high_distribution
        while recent_total > 0:
            new_infected = []
            if count == switchat:
                distribution = self.low_distribution
            for index,infected in enumerate(recent_infections):
                if index < len(profile) and profile[index] > 0.0:
                    for person in infected:
                        unlucky_neighbors = distribution.poisson()
                        for delta_neighbor in unlucky_neighbors:
                            neighbor = (person[0]+delta_neighbor[0],person[1]+delta_neighbor[1])
                            if self[neighbor] == 0 and (1 - profile[index])**unlucky_neighbors[delta_neighbor] <= random.random():
                                self[neighbor] = count+1 + 1000
                                new_infected.append(neighbor)
            newest = len(new_infected)
            statistics.append(newest)
            total += newest
            count += 1
            recent_infections.insert(0,new_infected)
            if len(recent_infections) > len(profile):
                del recent_infections[-1]
            recent_total = 0
            for index,infected in enumerate(recent_infections):
                if index < len(profile):
                    recent_total += len(infected)
            if count % 14 == 1:
                print('%4i % 7i % 7i' % (count,newest,total))
        #self.show()
        return statistics
    def monte_carlo(self,number,mobility=0.4,intensity=3.0):
        grand_totals = []
        for run_no in range(number):
            self.mobility = mobility
            self.intensity = intensity
            result = self.run()
            for index,value in enumerate(result):
                if index >= len(grand_totals):
                    grand_totals.append(0)
                grand_totals[index] += value
            print('Total %7i | Peak @ %3i %7i' % (sum(result),result.index(max(result)),max(result)))
        for index in range(len(grand_totals)):
            grand_totals[index] = grand_totals[index] / number
        return grand_totals


distribution = CustomDistribution()
cuba = TorusArray(1000)
cuba.high_distribution = distribution
outcomes = []
for parameterno in range(500):
    if parameterno % 2 == 0:
        power = random.random() * 4.0
        intensity = random.random() * 6.0
        distribution.powerlaw(1000,power,intensity)
    print('Power: %f Intensity %f' % (power,intensity))
    result = cuba.run()
    effectiveR0 = distribution.average()
    outcomes.append({'power' : power, 'intensity' : intensity, 'R0' : effectiveR0, 'result' : result})
    with open('sampleruns.py','w') as file:
        file.write(str(outcomes))
        file.close()



cuba = TorusArray(1000)
result = cuba.monte_carlo(1)
print(cuba.high_distribution.average(),cuba.low_distribution.average())
cuba.show()
string = ''
for item in result:
    string += str(item) + ',' + str(math.log(1+item)) + "\n"
open('mc.csv','w').write(string[0:len(string)-1])
