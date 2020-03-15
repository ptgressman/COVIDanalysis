from math import *
scenarios = [[0.05,1.0],[0.25,1.0],[0.5,1.0],[0.75,1.0]]
limit = 500.0
dt = 0.001
for scenario in scenarios:
    deathrate = scenario[0]
    infectrate = scenario[1]
    population = 1.0
    virus = exp(-15)
    time = -15
    count = 0.0
    infected = 0.0
    infect_time = 0.0
    while time < limit:
        newpop = population - dt * infectrate * population * virus * (1.0 - deathrate)
        newinf = dt * infectrate * population * virus * (1.0 - deathrate)
        newvir = virus + dt * (population * virus - deathrate * virus)
        population = newpop
        virus = newvir
        infected += newinf
        infect_time += newinf * (time + 0.5 * dt)
        time += dt * (1.0 - deathrate)
        count += 1
        #if count % 100 == 0 and time < 1.0:
            #print(time,virus * exp(-time+10),population)
    print(deathrate,infectrate,infected,infect_time/(infected))
quit()
class TorusGrid(object):
    def __init__(self,sizex,sizey,const=0.0):
        self.data = []
        for i in range(sizex):
            self.data.append([])
            for j in range(sizey):
                self.data[i].append(const)
        self.sizex = sizex
        self.sizey = sizey
    def get(self,i,j):
        truex = (i % sizex)
        truey = (j % sizey)
        if truex < 0:
            truex += sizex
        if truey < 0:
            truey += sizey
        return self.data[truex][truey]
    def set(self,i,j,value):
        truex = (i % sizex)
        truey = (j % sizey)
        if truex < 0:
            truex += sizex
        if truey < 0:
            truey += sizey
        self.data[truex][truey] = value
    def clone(self,othergrid):
        for i in range(self.sizex):
            for j in range(self.sizey):
                self.data[i][j] = othergrid.data[i][j]
    def laplacian(self,i,j):
        return -4 * self.get(i,j) + self.get(i+1,j) + self.get(i-1,j) + self.get(i,j+1) + self.get(i,j-1)
    def sum(self):
        value = 0.0
        for i in range(self.sizex):
            for j in range(self.sizey):
                value += self.data[i][j]
        return value


sizex = 40
sizey = 40
dt = 0.01
limit = 150.001



population = TorusGrid(sizex,sizey,1.0)
virus      = TorusGrid(sizex,sizey,0.0)
virus.set(0,0,1.0)
totalpop = population.sum()
viruspop = virus.sum()

temppop = TorusGrid(sizex,sizey)
tempvir = TorusGrid(sizex,sizey)
time = 0.0
count = 0
report = ''
for scenario in scenarios:
    deathrate = scenario[0]
    infectrate = scenario[1]
    population.__init__(sizex,sizey,1.0)
    virus.__init__(sizex,sizey,0.0)
    virus.set(0,0,1.0)
    totalpop = population.sum()
    viruspop = virus.sum()
    time = 0.0
    count = 0.0
    infected = 0.0
    weighted_infected = 0.0
    while time < limit and viruspop > 0.5:
        count += 1
        for i in range(sizex):
            for j in range(sizey):
                thispop = population.get(i,j)
                thisvir = virus.get(i,j)
                thisvlp = virus.laplacian(i,j)
                newvirus = thisvir + dt * (thisvlp + thispop * thisvir - deathrate * thisvir)
                newinfected = thispop * thisvir * dt * infectrate
                infected += newinfected
                weighted_infected += time * newinfected
                newpop   = thispop + dt * (-thispop * thisvir)
                tempvir.set(i,j,newvirus)
                temppop.set(i,j,newpop)
        time += dt
        population.clone(temppop)
        virus.clone(tempvir)
        if count % 500 == 0:
            viruspop = virus.sum()
            display = '%7.3f %11.5f %11.8f' % (time,viruspop,(totalpop - population.sum())/totalpop)
            print(display)
    display = '%5.2f %5.2f %11.8f\n' % (deathrate,weighted_infected/infected,(totalpop - population.sum())/totalpop)
    print(display,end='')
    report += display

print(report)
