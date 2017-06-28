import matplotlib.pyplot as plt
import pylab
import Generate_tree as Tree
from Load_tree import Load_tree_data
from src.power_flow.DSM_power_flow import *
import numpy as np
import pandas as pd
import os
import sys

### PLOTS THE LOAD ON A GIVEN BRANCH DEPENDING ON WHERE WE CLICK
def click(event,X,Y,Descendants_ids,Load_T,Load_C,Load_C_B,start_day,num_days,time,pv_surf):
	tb = pylab.get_current_fig_manager().toolbar
	if event.dblclick and event.button==1 and event.inaxes and tb.mode == '':
		x,y = event.xdata,event.ydata
		node = np.nanargmin((X-x)**2+(Y-y)**2)
		plt.plot(X[node],Y[node],'rs')
		plt.draw()
		
		load_C_B,Mean_C_B,Std_C_B=Tree.Line_load(Descendants_ids,Load_C_B,node)
		load_C,Mean_C,Std_C=Tree.Line_load(Descendants_ids,Load_C,node)
		load_T,Mean_T,Std_T=Tree.Line_load(Descendants_ids,Load_T,node)
	
		fig, ax = plt.subplots(2, sharex=True)
		fig.subplots_adjust(right=0.93, left=0.07,top=0.95,bottom=0.08,hspace=0.15)
		ax[0].plot(time,load_T,label = "Thermostat Node="+str(node),linewidth=1.5,c="g")
		ax[0].plot(time,load_C,label = "Control Node="+str(node),linewidth=1.5,c="r")
		ax[0].plot(time,load_C_B,label = "Control + Battery Node="+str(node),linewidth=1.5,c="b")
		ax[1].plot([start_day*24+12+n*24 for n in range(0,num_days)],Mean_T,'-og',label="Daily Mean Thermostat Node="+str(node),linewidth=2)
		ax[1].plot([start_day*24+12+n*24 for n in range(0,num_days)],Mean_C,'-or',label="Daily Mean Control Node="+str(node),linewidth=2)
		ax[1].plot([start_day*24+12+n*24 for n in range(0,num_days)],Mean_C_B,'-ob',label="Daily Mean Control + Battery Node="+str(node),linewidth=2)
		p1=ax[1].fill_between([start_day*24+12+n*24 for n in range(0,num_days)],Mean_T-Std_T,Mean_T+Std_T,alpha=0.3,facecolor="g")
		p2=ax[1].fill_between([start_day*24+12+n*24 for n in range(0,num_days)],Mean_C-Std_C,Mean_C+Std_C,alpha=0.3,facecolor="r")
		p3=ax[1].fill_between([start_day*24+12+n*24 for n in range(0,num_days)],Mean_C_B-Std_C_B,Mean_C_B+Std_C_B,alpha=0.3,facecolor="b")
		
		positions=[n*24 for n in range(start_day,start_day+num_days+1)]
		if num_days>20:
			labels=[n if n%5==0 else "" for n in range(start_day,start_day+num_days+1)]	
		else:
			labels=[n for n in range(start_day,start_day+num_days+1)]
		
		ax[0].set_title("Node "+str(node)+", "+str(len(Descendants_ids[node]))+" descendants, PV surf "+str(pv_surf)+"$[m^2]$",fontsize=30)
		for a in ax:
			a.legend()
			a.set_ylabel(r"$P_{\rm el}$"+" "+r"$[{\rm kW}]$", fontsize=30)
			a.tick_params(axis='both', which='major', labelsize=22)
			a.set_xlabel(r"Day", fontsize=25)
			a.set_xticks(positions)
			a.set_xticklabels(labels)
			a.xaxis.grid()
		ax[0].set_ylim(min(0,np.amin(load_T),np.amin(load_C)),max(np.amax(load_T),np.amax(load_C)))
		ax[0].set_xlim(start_day*24,24*(start_day+num_days))
	#plt.ion()
	plt.show()

	
def plot_line_load(num_nodes,start_day,num_days,R40,Domestic_appliances,pv_efficiency,pv_surf,city,simulate_boilers,*standalone):

	### GATHER DATA ###
	num_days=num_days-1
	
	res_fn_smart_B="Results_"+city+"/Res_HP_Control_B.dat"
	res_fn_smart="Results_"+city+"/Res_HP_Control.dat"
	res_fn="Results_"+city+"/Res_HP_Thermostat.dat"
	
	res_smart_B = pd.read_csv(res_fn_smart_B,delim_whitespace=True,header=None,index_col=False)
	res_smart_B = res_smart_B.values
	res_smart = pd.read_csv(res_fn_smart,delim_whitespace=True,header=None,index_col=False)
	res_smart = res_smart.values
	res_thermostat = pd.read_csv(res_fn,delim_whitespace=True,header=None,index_col=False)
	res_thermostat = res_thermostat.values
	
	if simulate_boilers==True:
		res_boilers_smart=pd.read_csv("Results_"+city+"/Res_Boiler_Control.dat",delim_whitespace=True,header=None,index_col=False)
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
		Load_T=(power_hp_thermostat + res_boilers + Domestic_appliances - power_pv)*1e-03 #[kW] load thermostat
		Load_C=(power_hp_smart + res_boilers_smart + Domestic_appliances - power_pv)*1e-03 #[kW] load control
		Load_C_B=(power_hp_smart_B + res_boilers_smart + Domestic_appliances - power_pv)*1e-03 #[kW] load control + batteries
	else:
		Load_T=(power_hp_thermostat+Domestic_appliances-power_pv)*1e-03 #[kW] load thermostat
		Load_C=(power_hp_smart+Domestic_appliances-power_pv)*1e-03 #[kW] load control
		Load_C_B=(power_hp_smart_B + Domestic_appliances - power_pv)*1e-03 #[kW] load control + batteries
		
	### PLOTTING THE NETWORK ###
	# Add one additional slack node to plot the network...
	num_nodes += 1
	# Append row of zeros for the slack bus additional node!
	Load_T = np.concatenate((np.zeros((24*60*num_days,1)), Load_T),axis=1)
	Load_C = np.concatenate((np.zeros((24*60*num_days,1)), Load_C),axis=1)
	Load_C_B = np.concatenate((np.zeros((24*60*num_days,1)), Load_C_B),axis=1)
	
	initial_dir = os.getcwd()
	tree_dir = "Data/Distribution_network_data/"
	fn = tree_dir+"Tree_N="+str(num_nodes)
	if os.path.exists(fn):
		print "TREE ALREADY EXISTS -- I AM USING AN OLD ONE"
		Adj,Num_of_children,Levels,Descendants,Descendants_ids = Load_tree_data(num_nodes,fn)
	else: 
		os.chdir(tree_dir)
		print "TREE DOES NOT EXIST -- I AM CREATING ONE"
		Adj, Levels, Num_of_children = Tree.generate_tree(num_nodes)
		Descendants, Descendants_ids = Tree.Tree_statistics(num_nodes,Adj,Levels,Num_of_children)
		Tree.Save_tree(num_nodes,Adj,Levels,Num_of_children,Descendants,Descendants_ids,"Tree_N="+str(num_nodes))
		prepare_load_flow_network(num_nodes, Adj)
		os.chdir(initial_dir)
	
	fig = plt.figure()
	ax = fig.add_subplot(111)
	[X,Y] = Tree.Plot_tree(fig, ax,num_nodes, Adj, Levels, Num_of_children)
	fig.canvas.mpl_connect('button_press_event', lambda event: click(event, X, Y, Descendants_ids, Load_T, Load_C, Load_C_B,start_day,num_days,time,pv_surf))

	if not standalone:
		plt.ion()
	plt.show()


def main():
	
	city=sys.argv[1]
	dir_name='Results_'+city+'/'
	f = open(dir_name+'Input_Heat_Pump.txt', 'r')
	data = f.readlines()
	f.close()
	num_houses =int(data[0])
	starting_day =int(data[1])
	num_days =int(data[2])
	pv_surf = float(data[11])
	pv_efficiency = float(data[12])
	R40=np.loadtxt(dir_name+'R40.dat')
	Domestic_appliances=np.loadtxt(dir_name+"House_aggregate.dat")

	if os.path.exists(dir_name+'Input_Boilers.txt'):
		simulate_boilers=True
	else:
		simulate_boilers=False
	standalone=True
	plot_line_load(num_houses,starting_day,num_days,R40,Domestic_appliances,pv_efficiency,pv_surf,city,simulate_boilers,standalone)

if __name__ == '__main__':
	main()


