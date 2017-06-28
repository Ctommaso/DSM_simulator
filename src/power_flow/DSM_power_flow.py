from Load_data import *
from NR_solver import *
import os
import numpy as np
import multiprocessing
import copy
import pandas as pd

# Run load flow
def run_power_flow(args):
	
	# Unpack arguments: graph, list of active powers
	g, S = args
	
	# Do not modify the original graph
	g = copy.deepcopy(g)

	# Set nodal power consumptions
	for n, b in enumerate(g.busses):
		b.load = S[n]
	
	#run load flow
	theta, v = NR_solver(g,1e-8,20)
	return v
	

def DSM_power_flow(graph_fn, p_T, p_C, p_C_B):

	# Load graph
	busses, lines, S_BASE = load_MATPOWER(graph_fn)
	g = Electrical_network(busses, lines, S_BASE)
	num_busses = len(g.busses)
	
	P_data = [p_T, p_C, p_C_B]
	Pflow_name = ["thermostat", "control", "control + batt"]
	V = []
	for n, p_data in enumerate(P_data):
		print "running power flow", Pflow_name[n]
		
		# Power factor for reactive power conversion: cos(phi)=0.97
		power_factor = 0.25
		s_data = p_data + 1j*p_data*0.25

		# Get number of available processors
		cpu_nb = multiprocessing.cpu_count()
		pool = multiprocessing.Pool(cpu_nb)
		
		# Parameters for the parallel load flow
		param = [(g, s_data[t,:]) for t in range(0,len(p_data))]
	
		start = time.time()
		# Parallel load flow (nb: map returns ordered output)
		V.append(np.array(pool.map(run_power_flow, param)))
		pool.close()
		pool.join()
		end = time.time()
		print "elapsed_time ", end-start
	
	V_T, V_C, V_C_B = V
	
	return V_T, V_C, V_C_B


def prepare_load_flow_data(num_nodes, start_day, num_days, R40, Domestic_appliances,
                           pv_efficiency, pv_surf, city, simulate_boilers, *standalone):

	### GATHER DATA ###
	num_days=num_days-1
	
	res_fn_smart_B = "Results_"+city+"/Res_HP_Control_B.dat"
	res_fn_smart = "Results_"+city+"/Res_HP_Control.dat"
	res_fn = "Results_"+city+"/Res_HP_Thermostat.dat"
	
	res_smart_B = pd.read_csv(res_fn_smart_B,delim_whitespace=True,header=None,index_col=False)
	res_smart_B = res_smart_B.values
	res_smart = pd.read_csv(res_fn_smart,delim_whitespace=True,header=None,index_col=False)
	res_smart = res_smart.values
	res_thermostat = pd.read_csv(res_fn,delim_whitespace=True,header=None,index_col=False)
	res_thermostat = res_thermostat.values
	
	if simulate_boilers==True:
		res_boilers_smart = pd.read_csv("Results_"+city+"/Res_Boiler_Control.dat",delim_whitespace=True,header=None,index_col=False)
		res_boilers_smart = (res_boilers_smart.values)[0:24*60*num_days,num_nodes+1:2*num_nodes+1]
		res_boilers=pd.read_csv("Results_"+city+"/Res_Boiler_Thermostat.dat",delim_whitespace=True,header=None,index_col=False)
		res_boilers = (res_boilers.values)[0:24*60*num_days,num_nodes+1:2*num_nodes+1]
	
	time=res_smart[:,0]
	power_hp_smart_B=res_smart_B[:,1:num_nodes+1]
	power_hp_smart=res_smart[:,1:num_nodes+1]
	power_hp_thermostat=res_thermostat[:,1:num_nodes+1]

	R40=R40[0:24*60*num_days]
	power_pv=R40*pv_efficiency*pv_surf
	power_pv=np.tile(power_pv,(num_nodes,1))
	power_pv=np.transpose(power_pv)
	
	Domestic_appliances=Domestic_appliances[0:24*60*num_days,:]

	if simulate_boilers==True:
		Load_T=(power_hp_thermostat + res_boilers + Domestic_appliances - power_pv)#[W] load thermostat
		Load_C=(power_hp_smart + res_boilers_smart + Domestic_appliances - power_pv)#[W] load control
		Load_C_B=(power_hp_smart_B + res_boilers_smart + Domestic_appliances - power_pv)#[W] load control + batteries
	else:
		Load_T=(power_hp_thermostat+Domestic_appliances-power_pv)#[W] load thermostat
		Load_C=(power_hp_smart+Domestic_appliances-power_pv)#[W] load control
		Load_C_B=(power_hp_smart_B + Domestic_appliances - power_pv)#[W] load control + batteries
	
	# Add slack column
	Load_T = np.concatenate((np.zeros((len(Load_T),1)), Load_T), axis = 1)
	Load_C = np.concatenate((np.zeros((len(Load_C),1)), Load_C), axis = 1)
	Load_C_B = np.concatenate((np.zeros((len(Load_C_B),1)), Load_C_B), axis = 1)
	
	return Load_T, Load_C, Load_C_B


def prepare_load_flow_network(num_nodes, Adj):

	fn = "case"+str(num_nodes)+".txt"
	edges = [[Adj[i,0]+1, Adj[i,1]+1] for i in range(0,len(Adj),2)]

	file = open(fn,"w") 
	 
	file.write("%%-----  Power Flow Data  -----%%\n") 
	file.write("%% system VA base\n") 
	file.write("mpc.baseMVA = 1000 %[W], BaseV = 220[V], BaseR = V0^2/P0 = 48.4 [Ohm];\n") 

	file.write("\n")

	file.write("%% bus data\n") 
	file.write("%	bus_i	type	Pd	Qd	Gs	Bs	area	Vm	Va	baseKV	zone	Vmax	Vmin\n") 
	file.write("mpc.bus = [\n") 
	for n in range(1, num_nodes+1):
		bus_type = '3' if n == 1 else '1'
		file.write("	"+str(n) + "	" + bus_type +"	0	0	0	0	1	1.0	0	0	1	1.06	0.94;\n")
	file.write("];\n")

	file.write("\n")

	file.write("%% generator data\n") 
	file.write("%	bus	Pg	Qg	Qmax	Qmin	Vg	mBase	status	Pmax	Pmin	Pc1	Pc2	Qc1min	Qc1max	Qc2min	Qc2max	ramp_agc	ramp_10	ramp_30	ramp_q	apf\n") 
	file.write("mpc.gen = [\n") 
	file.write("	1	0	0	0	0	1.0	0	1	0	0	0	0	0	0	0	0	0	0	0	0	0;\n") 
	file.write("];\n") 

	file.write("\n")

	# Per unit values of r and x (these are somehow arbitrary)
	r, x = 1e-04, 1e-04

	file.write("%% branch data\n") 
	file.write("%	fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status	angmin	angmax\n") 
	file.write("mpc.branch = [\n") 
	for e in edges:
		file.write("	"+str(e[0]) +"	"+ str(e[1]) +"	"+ str(r)+ "	"+str(x)+"	0	0	0	0	0	0	1	-360	360;\n")
	file.write("];\n") 

	file.close()
