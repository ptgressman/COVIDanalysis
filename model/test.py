
s0 = 0.9999
i0 = 0.0001
delta = 0.14
R0 = 3
factor = 0.14


sa = s0
sb = s0
ia = i0
ib = i0
old_dia = 0
old_dib = 0
reported = False
hreport = False
string = ''
for loop in range(300):
    string += '%i,%f,%f,%f,%f\n' % (loop,ia,sa,ib,sb)
    dsa = - R0 * sa * ia * delta
    dsb = - sb * (1 - (1-ib)**(R0/factor)) * factor * delta
    dia = -dsa - delta * ia
    dib = -dsb - delta * ib
    sa = sa + dsa
    ia = ia + dia
    sb = sb + dsb
    ib = ib + dib
    if not hreport and (dia <= 0 or dib <= 0):
        print(loop,'%10.8f %10.8f | %10.8f %10.8f' % (ia,sa,ib,sb))
        if dia <= 0 and dib <= 0:
            hreport = True
    old_dia = dia
    old_dib = dib
    if not reported and ib < 1e-9 and ia < 1e-9:
        print(loop,'%10.8f %10.8f | %10.8f %10.8f' % (ia,sa,ib,sb))
        reported = True

open('test.csv','w').write(string[0:len(string)-1])
