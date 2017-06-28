import sys
import numpy as np
import matplotlib.pyplot as plt
from Tree_network.Load_tree import Load_tree_data
from Tree_network.Generate_tree import Line_load, Plot_tree
import pylab
from matplotlib import rc
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)


# On click event plot the bus voltage
def click(event, coord, v_data, P_data, descendants_ids):
	
	ax1, ax2, ax3 = event.canvas.figure.get_axes()
	n = event.canvas.figure.number
	P = P_data[n]
	v = v_data[n]
	if event.dblclick:
		xnode = coord[0]
		ynode = coord[1]
		tb = pylab.get_current_fig_manager().toolbar
		if event.button==1 and tb.mode == '':
			x, y = event.xdata, event.ydata
			if event.inaxes == ax1:
				node_id = np.nanargmin((xnode-x)**2+(ynode-y)**2)
				ax1.scatter(xnode[node_id],ynode[node_id],s=60, c='r', edgecolor="k", marker="s",lw=0.5)
				ax2.plot(v[:,node_id],"o-",label = "Bus "+str(node_id))
				ax2.set_ylim(0.8,1.05)
				
				# Computation of the line load
				line_load, mean, std = Line_load(descendants_ids,P,node_id)
				# Conversion of the line load to [kW]
				ax3.plot(line_load*1e-03, "-",label = "Bus "+str(node_id)) 
				ax2.legend()
				ax3.legend()
				
				plt.show()
	

# On key event plot the bus voltage
def onkey(event):
	
	ax1, ax2, ax3 = event.canvas.figure.get_axes()
	to_remove = len(ax1.collections)

	if event.key == 'c' and ax1.collections>1:
		positions = ax2.get_xticks()
		labels = ax2.get_xticklabels()
		for n in range(1,to_remove):
			ax1.collections.pop(-1)
		ax2.cla()
		ax3.cla()
		ax2.set_xticks(positions)
		ax3.set_xticks(positions)
		ax2.set_xticklabels(labels)
		ax3.set_xticklabels(labels)
		ax2.xaxis.grid()
		ax3.xaxis.grid()
		plt.show()


def plot_voltages(V_T, V_C, V_C_B, P_T, P_C, P_C_B):
	
	Voltages = [V_T, V_C, V_C_B]
	Voltages = [V_T, V_C, V_C_B]
	P_data = [P_T, P_C, P_C_B]
	title = ["Thermostat", "Control", "Control + Batt"]

	# Load tree
	num_busses = len(V_T[0])
	tree_dir = "Visualization_Scripts/Tree_network"
	fn = tree_dir+"/Tree_N="+str(num_busses)
	adj, num_of_children, levels, descendants, descendants_ids = Load_tree_data(num_busses,fn)
		
	for n, V in enumerate(Voltages):

		# Static plot 
		fig = plt.figure()
		fig.number = n
		
		ax1 = plt.subplot2grid((3, 1), (0, 0))
		ax2 = plt.subplot2grid((3, 1), (1, 0))
		ax3 = plt.subplot2grid((3, 1), (2, 0), sharex=ax2)
		
		coord = Plot_tree(fig, ax1, num_busses, adj, levels, num_of_children)
				
		ax2.set_xlim(0,len(P_data[n]))
		ax2.set_ylim(0.8,1.05)
		ax2.set_ylabel(r"$V$ [p.u.]", fontsize=25)
		ax3.set_ylabel(r"$P_{\rm el}$"+" "+r"$[{\rm kW}]$", fontsize=30)			
		ax3.set_xlabel(r"Day", fontsize=25)

		ax2.tick_params(axis = 'both', which = 'major',pad=10, labelsize=20)
		ax3.tick_params(axis = 'both', which = 'major',pad=10, labelsize=20)
		positions = [1440*m for m in range(0,len(P_data[n])/1440)]
		labels = [m for m in range(0,len(P_data[n])/1440)]
		ax2.set_xticks(positions)
		ax3.set_xticks(positions)
		ax2.set_xticklabels(labels)
		ax3.set_xticklabels(labels)
		
		ax2.xaxis.grid()
		ax3.xaxis.grid()
		fig.subplots_adjust(right=0.98, left=0.07,top=0.95,bottom=0.08,wspace=0.11)
		
		# Dynamic plot
		fig.canvas.mpl_connect('button_press_event',lambda event: click(event, coord, Voltages, P_data, descendants_ids))
		fig.canvas.mpl_connect('key_press_event', lambda event: onkey(event))
		fig.suptitle(title[n], fontsize=25)
		mng = plt.get_current_fig_manager()
		mng.resize(*mng.window.maxsize())
		plt.ion()
	plt.show()


