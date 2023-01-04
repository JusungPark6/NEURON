from neuron import h, gui
from neuron.units import mV, ms, µm
import numpy as np
h.CVode().cache_efficient(1)

h.load_file("stdrun.hoc")
h.finitialize(-85 * mV)
h.continuerun(200 * ms)

def taper_diam(sec,zero_bound,one_bound):
    dx = 1./sec.nseg
    for (seg, x) in zip(sec, np.arange(dx/2, 1, dx)):
        seg.diam=(one_bound-zero_bound)*x+zero_bound

base = "BOTH_85"
v_init = -85
AMPAmax = 0.0005
NMDAmax = 0.001
dt = 0.01
steps_per_ms = 100
tstop = 200

soma = h.Section(name="soma")
dend = h.Section(name="dend")
axon = h.Section(name="axon")
iseg = [h.Section(name='iseg[%d]' % i) for i in range(40)]
spine_head = [h.Section(name='spine_head[%d]' % i) for i in range(1000)]
spine_neck = [h.Section(name='spine_neck[%d]' % i) for i in range(1000)]

soma.L = 20
soma.nseg = 3
soma.connect(iseg[0], 0, 0)
soma.diam = 10

dend.L = 1000
dend.nseg = 1001
taper_diam(dend,5,1)
dend.connect(soma(1), 0)
for seg in dend:
    print(seg.diam)


axon.nseg = 201
axon.L = 2000
axon.diam = 0.5

h.celsius = 37
Ri = 100
Cm = 1.0
Rm = 15000


for i in range(0, 40):
    iseg[i].nseg = 1
    iseg[i].diam = 2 - (1.5 * (i / 40))
    iseg[i].L = 1
    if i < 39:
        iseg[i].connect(iseg[i + 1], 0, 1)
    if i == 39:
        iseg[i].connect(axon, 0, 1)

h.distance(sec=soma)

for i in range(0, 1000):
    g = (i+1)/1000
    spine_neck[i].connect(dend, g)
    spine_head[i].connect(spine_neck[i], 1)
    spine_neck[i].nseg = 1
    spine_neck[i].L = 1
    spine_neck[i].diam = 0.0504573
    spine_head[i].nseg = 1
    spine_head[i].L = 0.5
    spine_head[i].diam = 0.5

for sec in h.allsec():
    sec.insert('pas')
    sec.g_pas = 1/Rm
    sec.cm = Cm
    sec.Ra = Ri
    sec.e_pas = v_init

somavec = h.Vector()
dendvec = h.Vector()
Acondvec = h.Vector()
Ncondvec = h.Vector()

savsoma = h.File()
savdend = h.File()
savAcond = h.File()
savNcond = h.File()

somamatrix = h.Matrix(2000,101)
dendmatrix = h.Matrix(2000,101)
Acondmatrix = h.Matrix(2000,101)
Ncondmatrix = h.Matrix(2000,101)

fName = h.ref("")
h.sprint(fName, "Soma_%s.dat", base)
savsoma.wopen(fName)
h.sprint(fName, "Dend_%s.dat", base)
savdend.wopen(fName)
h.sprint(fName, "AMPAcond_%s.dat", base)
savAcond.wopen(fName)
h.sprint(fName, "NMDAcond_%s.dat", base)
savNcond.wopen(fName)

AMPA = [h.Section(name='AMPA[%d]' % i) for i in range(100)]
NMDA = [h.Section(name='NMDA[%d]' % i) for i in range(100)]
for i in range(0,100):
    if i==0:
        q=1
    else:
        q=((i*10)-1)

    # h(r'''''''''spine_head[q]   AMPA = new syn_g(1)
    # spine_head[q]   NMDA = new nmda(1)
    # AMPA.onset = 2
    # AMPA.gmax = AMPAmax
    # NMDA.onset = 2
    # NMDA.gmax = NMDAmax''''''''')
    AMPA[i].connect(spine_head[q])
    NMDA[i].connect(spine_head[q])
    # spine_head[q]   AMPA = new syn_g(1)
    # spine_head[q]   NMDA = new nmda(1)
    # AMPA.onset = 2
    # AMPA.gmax = AMPAmax
    # NMDA.onset = 2
    # NMDA.gmax = NMDAmax
    p = q / 999

    # somavec = somavec.record(soma(0.5)._ref_v)
    # dendvec = dendvec.record(dend(p)._ref_v)
    somavec.record(soma(0.5)._ref_v, 0.1)
    dendvec.record(dend(p)._ref_v, 0.1)
    h('Acondvec.record(&AMPA.g, 0.1)')
    h('Ncondvec.record(&NMDA.g, 0.1)')
    # Acondvec.record(AMPA[i],v)
    # Ncondvec.record(NMDA[i], 0.1)

    t = h.Vector().record(h._ref_t)
    h.finitialize(-85 * mV)

    while t<tstop-dt:
        h.fadvance()

    somamatrix.setcol(i, somavec)
    dendmatrix.setcol(i, dendvec)
    Acondmatrix.setcol(i, Acondvec)
    Ncondmatrix.setcol(i, Ncondvec)

    print(i)



somamatrix.fprint(savsoma, " %g")
dendmatrix.fprint(savdend, " %g")
Acondmatrix.fprint(savAcond, " %g")
Ncondmatrix.fprint(savNcond, " %g")

savsoma.close()
savdend.close()
savAcond.close()
savNcond.close()
