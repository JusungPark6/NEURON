from neuron import h, gui
from neuron.units import mV, ms, µm
h.CVode().cache_efficient(1)
h.load_file("stdrun.hoc")

# Uses the makeCell*.hoc files in parallel. Also the new ball and stick template.


# /************* Loading necessary files *********************/

h.xopen("makeSavestatesActive.hoc")
h.load_file("Threshold_Template.hoc")
# Uses 50 um range for threshold test, and 50 ms width Gaussian.
# Assumes savestates are already made and in the folder. Use 'makeSavestates.hoc' for each machine

#/************* The procs ****************/

mcVS = ""
ThName = ""
fName = ""
filename = ""
def mcVolt(voltInput, length, startS, AMPAc):
	# Inputs:
	# $1 is v_init
	# $2 is length
	# $3 is starting seed
	# $4 is AMPA conductance, normal .0005 umho

	# h('voltInput = $1')
	# h('length = $2')
	# h('startS = $3')
	# h('AMPAc = $4')

	# Makes cell with desired voltage and length
	cell = h.Cell(length,voltInput)
	v_init = voltInput

	savestate = h.SaveState()
	savestate = loadSv(length,voltInput*-1)
		# Loads the savestate to a variable 'savestate'

	# Running the test
	runTh(length,cell,startS,AMPAc)

def runTh(nSpines, cell, startS, AMPAc):
	# $1 is the number of spines (dendrite length)
	# $o2 is the cell
	# $3 is the starting seed for the trials
	# $4 is the AMPA conductance

	# h('nSpines = $1')
	# h('startS = $3')
	# h('AMPAc = $4')

	# Inputs:
	# $1: locRange is the range to be uniformly sampled in space
	# $2: gaussTime is the width of the Gaussian to be sampled for timing
	# $3: repStat is the number of repetitions for each location, to collect statistics in variation
	# $4: incrBy is the distance in microns each trial is separated by.
	# $5: branchLength is the number of spines on the tested branch.
	# $6: toggle is the kind of synapse: 0 BOTH, 1 AMPA, 2 NMDA
	# $s7: filename.
	# $8: the starting seed
	# $o9: the cell itself
	# $10: AMPA conductance, with normal .0005 umho

	# below- changed repStat from 1 to 9
	# below- changed incrBy from 20 to 10

	sprint(ThName,"Tr%dThLen%dV%dB.dat",startS,nSpines,v_init*-1)
	h.ThreshSpace(50,50,10,10,nSpines,0,ThName,startS,cell,AMPAc)
	sprint(ThName,"Tr%dThLen%dV%dA.dat",startS,nSpines,v_init*-1)
	h.ThreshSpace(50,50,10,10,nSpines,1,ThName,startS,cell,AMPAc)
	sprint(ThName,"Tr%dThLen%dV%dN.dat",startS,nSpines,v_init*-1)
	h.ThreshSpace(50,50,10,10,nSpines,2,ThName,startS,cell,AMPAc)


def init():
	# The right savestate must be loaded

	finitialize(v_init)
	h('savestate.restore(1)')
	t=0
	fcurrent()
	frecord_init()

def loadSv(length, volt):
	# Loads the right savestate
	# $1 is the dendrite length
	# $2 is the voltage*-1

	h.sprint(filename,"BLen%dstdstt%d.dat",length,volt)
	svstate = h.SaveState()
	f = h.File(filename)
	svstate.fread(f)
	return svstate

#/************************************************************/
#/**************** The actual script *************************/
#/************************************************************/

for vo_ind in range(1,8):   # RMP range (1 to 7 equates to -55 to -85 mV)
	for le_ind in range(1,6):	 # Length, from 200 to 1,000 um (1 = 200 um, 5 = 1,000 um)
		for ac_ind in range(5,6):	# AMPA conductance (in hundreds of pS)
			for tr_ind in range(0,1):	# redundant
				mcVolt(((vo_ind*5)+50)*-1,le_ind*200,tr_ind,ac_ind*.0001)

# h('''''''''for vo_ind = 1,7 {	 // RMP range (1 to 7 equates to -55 to -85 mV)
# 		for le_ind = 1,5 {	 // Length, from 200 to 1,000 um (1 = 200 um, 5 = 1,000 um)
# 			for ac_ind = 5,5 {	// AMPA conductance (in hundreds of pS)
# 				for tr_ind = 0,0 {	// redundant
# 					mcVolt(((vo_ind*5)+50)*-1,le_ind*200,tr_ind,ac_ind*.0001)
# 				}
# 			}
# 		}
# 	}''''''''')
