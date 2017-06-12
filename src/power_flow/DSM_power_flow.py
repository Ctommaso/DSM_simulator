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
	network_dir = "Data/Distribution_network_data" 
	busses, lines, S_BASE = load_MATPOWER(os.path.join(network_dir, graph_fn))
	g = Electrical_network(busses, lines, S_BASE)
	num_busses = len(g.busses)
	
	P_data = [p_T, p_C, p_C_B]
	V = []
	for p_data in P_data:
		print "MAMMA MIA"
		
		# Power factor for reactive power conversion: cos(phi)=0.97
		power_factor = 0.25
		s_data = p_data + 1j*p_data*0.25

		# Get number of available processors
		cpu_nb = multiprocessing.cpu_count()
		pool = multiprocessing.Pool(cpu_nb)
		
		# Parameters for the parallel load flow
		param = [(g, s_data[t,:]) for t in range(0,len(p_data),15)]
	
		start = time.time()
		# Parallel load flow (nb: map returns ordered output)
		V.append(np.array(pool.map(run_power_flow, param)))
		pool.close()
		pool.join()
		end = time.time()
		print "elapsed_time ", end-start
	
	V_T, V_C, V_C_B = V
	
	return V_T, V_C, V_C_B


def prepare_load_flow_data(num_nodes,start_day,num_days,R40,Domestic_appliances,pv_efficiency,pv_surf,city,simulate_boilers,*standalone):

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
	
def main():
	
	city = sys.argv[1]
	dir_name = 'Results_'+city+'/'
	f = open(dir_name+'Input_Heat_Pump.txt', 'r')
	data = f.readlines()
	f.close()
	num_houses = int(data[0])
	starting_day = int(data[1])
	num_days = int(data[2])
	pv_surf = float(data[11])
	pv_efficiency = float(data[12])
	R40 = np.loadtxt(os.path_join(dir_name,'R40.dat'))
	Domestic_appliances = np.loadtxt(os.path_join(dir_name,"House_aggregate.dat"))

	if os.path.exists(dir_name+'Input_Boilers.txt'):
		simulate_boilers = True
	else:
		simulate_boilers = False
	standalone = True
	
	Load_T, Load_C, Load_C_B = prepare_load_flow_data(num_houses,starting_day,num_days,
	                                                  R40,Domestic_appliances,pv_efficiency,pv_surf,
	                                                  city,simulate_boilers,standalone)
	V_T, V_C, V_C_B = DSM_power_flow(Load_T, Load_C, Load_C_B)
	
	V = [V_T, V_C, V_C_B]
	Load = [Load_T, Load_C, Load_C_B]
	for n, v in enumerate(V): 
		print "ciao"
		#Plot_voltages(v,Load[n])
	
# Main
def main():
	
	
	# Plotting part
	# Load tree
	fn = "../Visualization_Scripts/Tree_network/Tree_N="+str(num_busses)
	adj, num_of_children, levels, descendants, descendants_ids = Load_tree_data(num_busses,fn)
	
	# Static plot 
	fig = plt.figure()
	fig.subplots_adjust(right=0.99, left=0.07,top=0.95,bottom=0.08,wspace=0.11)
	
	ax1 = plt.subplot2grid((3, 1), (0, 0))
	ax2 = plt.subplot2grid((3, 1), (1, 0))
	ax3 = plt.subplot2grid((3, 1), (2, 0), sharex=ax2)
	
	coord = plot_tree(ax1, num_busses, adj, levels, num_of_children)
	
	ax2.set_xlim(0,len(P_data))
	ax2.set_ylim(0.8,1.05)
	ax2.set_ylabel(r"$V$ [p.u.]", fontsize=25)
	ax3.set_ylabel(r"$P_{\rm el}$"+" "+r"$[{\rm kW}]$", fontsize=30)			
	ax3.set_xlabel(r"Day", fontsize=25)

	ax2.tick_params(axis='both', which='major',pad=10, labelsize=20)
	ax3.tick_params(axis='both', which='major',pad=10, labelsize=20)
	positions = [1440*n for n in range(0,len(P_data)/1440)]
	labels = [n for n in range(1,len(P_data)/1440+1)]
	ax2.set_xticks(positions)
	ax3.set_xticks(positions)
	ax2.set_xticklabels(labels)
	ax3.set_xticklabels(labels)
	
	ax2.xaxis.grid()
	ax3.xaxis.grid()
	
	# Dynamic plot
	fig.canvas.mpl_connect('button_press_event',lambda event: click(event, ax1, ax2, ax3, coord, V, P_data, descendants_ids))
	fig.canvas.mpl_connect('key_press_event', lambda event: onkey(event, ax1, ax2, ax3))
	fig.suptitle("Thermostat", fontsize=25)
	mng = plt.get_current_fig_manager()
	mng.resize(*mng.window.maxsize())
	plt.show()
	
if __name__ == '__main__':
	main()
