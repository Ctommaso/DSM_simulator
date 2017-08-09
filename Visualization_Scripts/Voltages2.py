import sys
import numpy as np
import matplotlib.pyplot as plt
from Load_tree import Load_tree_data
from Generate_tree import Line_load, Plot_tree
from mpl_toolkits.axes_grid.inset_locator import inset_axes
import pylab
from matplotlib import rc
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)


# On click event plot the bus voltage
def click(event, coord, v_data, P_data, descendants_ids):
	
	ax1, ax2, ax1ins = event.canvas.figure.get_axes()
	n = event.canvas.figure.number

	if event.dblclick:
		xnode = coord[0]
		ynode = coord[1]
		tb = pylab.get_current_fig_manager().toolbar
		if event.button==1 and tb.mode == '':
			x, y = event.xdata, event.ydata
			if event.inaxes == ax1ins:
				node_id = np.nanargmin((xnode-x)**2+(ynode-y)**2)
				l1 = ax1.plot(v_data[0][:,node_id],"--",linewidth=2.,label = "Bus "+str(node_id))
				ax1.plot(v_data[2][:,node_id],"-",linewidth=2.,c = l1[0].get_color(), label = "Bus "+str(node_id))
				
				ax1.set_ylim(0.8,1.05)
				ax1ins.scatter(xnode[node_id],ynode[node_id], c=l1[0].get_color(), s=60, marker="s",lw=0.5)
				
				# Computation of the line load
				line_load, mean, std = Line_load(descendants_ids,P_data[0],node_id)
				# Conversion of the line load to [kW]
				ax2.plot(line_load*1e-03, "--",linewidth=2.,c = l1[0].get_color(),label = "Bus "+str(node_id)) 

				# Computation of the line load
				line_load, mean, std = Line_load(descendants_ids,P_data[2],node_id)
				# Conversion of the line load to [kW]
				ax2.plot(line_load*1e-03, "-",linewidth=2.,c = l1[0].get_color(),label = "Bus "+str(node_id)) 

				ax1.legend()
				ax2.legend()
								
				plt.show()
	

# On key event plot the bus voltage
def onkey(event):
	
	ax1, ax2, ax1ins = event.canvas.figure.get_axes()
	to_remove = len(ax1ins.collections)

	if event.key == 'c' and ax1ins.collections>1:
		positions = ax1.get_xticks()
		labels = ax1.get_xticklabels()
		for n in range(1,to_remove):
			ax1ins.collections.pop(-1)
		ax1.cla()
		ax2.cla()
		ax1.set_xticks(positions)
		ax2.set_xticks(positions)
		ax1.set_xticklabels(labels)
		ax2.set_xticklabels(labels)
		ax1.set_ylabel(r"$V$ [p.u.]", fontsize=25)
		ax2.set_ylabel(r"$P_{\rm el}$"+" "+r"$[{\rm kW}]$", fontsize=30)			
		ax2.set_xlabel(r"Day", fontsize=25)
		ax1.xaxis.grid()
		ax2.xaxis.grid()
		plt.show()


def plot_voltages(V_T, V_C, V_C_B, P_T, P_C, P_C_B):
	
	Voltages = [V_T, V_C, V_C_B]
	Voltages = [V_T, V_C, V_C_B]
	P_data = [P_T, P_C, P_C_B]
	title = ["Thermostat", "Control", "Control + Batt"]

	# Load tree
	num_busses = len(V_T[0])
	tree_dir = "Data/Distribution_network_data/Tree_N="+str(num_busses)
	adj, num_of_children, levels, descendants, descendants_ids = Load_tree_data(num_busses,tree_dir)
		
	# Static plot 
	fig , (ax1, ax2) = plt.subplots(2, sharex = True)
		
	ax1ins = inset_axes(ax1,width="30%", height="30%",loc=4)

	coord = Plot_tree(fig, ax1ins, num_busses, adj, levels, num_of_children)
				
	ax1.set_xlim(0,len(P_data[0]))
	ax1.set_ylim(0.8,1.05)
	ax1.set_ylabel(r"$V$ [p.u.]", fontsize=25)
	ax2.set_ylabel(r"$P_{\rm el}$"+" "+r"$[{\rm kW}]$", fontsize=30)			
	ax2.set_xlabel(r"Day", fontsize=25)

	ax1.tick_params(axis = 'both', which = 'major',pad=10, labelsize=20)
	ax2.tick_params(axis = 'both', which = 'major',pad=10, labelsize=20)
	positions = [1440*m for m in range(0,len(P_data[0])/1440)]
	labels = [m for m in range(0,len(P_data[0])/1440)]
	ax1.set_xticks(positions)
	ax2.set_xticks(positions)
	ax1.set_xticklabels(labels)
	ax2.set_xticklabels(labels)
		
	ax1.xaxis.grid()
	ax2.xaxis.grid()
	fig.subplots_adjust(right=0.98, left=0.08,top=0.95,bottom=0.08,wspace=0.11)
		
	# Dynamic plot
	fig.canvas.mpl_connect('button_press_event',lambda event: click(event, coord, Voltages, P_data, descendants_ids))
	fig.canvas.mpl_connect('key_press_event', lambda event: onkey(event))
	
	mng = plt.get_current_fig_manager()
	mng.resize(*mng.window.maxsize())
	plt.ion()
	plt.show()

