import sys
from adore import AdoreCollection, AdoreValues
    
ado = AdoreCollection("/home/theo/triwaco/transient_10.flo")
phit = ado.find_first('phit')
phit.read_data()
phit.write(sys.stdout)

a = AdoreValues("qrch",ado)
qrch = a.get_timeseries(58)
for t,q in qrch:
    print '%g,%g' % (t,q)
