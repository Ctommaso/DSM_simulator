import sys
sys.path.insert(0, '../../POWER_FLOW')
sys.path.insert(0, '../Visualization_Scripts')
from Load_data import *
from NR_solver import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import collections  as mc
from matplotlib.patches import Circle
import pylab
from Tree_network.Load_tree import Load_tree_data
from Tree_network.Generate_tree import Line_load
from matplotlib import rc
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)
import multiprocessing
import copy

# On click event plot the bus voltage
def click(event, ax1, ax2, ax3, coord, v, P, descendants_ids):
	
	if event.dblclick:
		xnode = coord[:,0]
		ynode = coord[:,1]
		tb = pylab.get_current_fig_manager().toolbar
		if event.button==1 and event.inaxes and tb.mode == '':
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
def onkey(event, ax1, ax2, ax3):
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


# Plot the radial network
def plot_tree(ax, num_busses, adj, levels, num_of_children):

	### PLOT NODES ###
	Y=[]
	for n in range(0,num_busses):
		for l in range(0,len(levels)):
			if n in levels[l]:
				Y.append(-l)
				
	X=np.zeros(num_busses)
	counter=1
	for n in range(0,num_busses):
		level =- Y[n]
		step = 1.0/np.exp(1.1*level)
		if num_of_children[n]>0:
			children_id=[counter + l for l in range(0,num_of_children[n])]
			for j in children_id:
				X[j] = X[n] + step*(children_id.index(j)-float((num_of_children[n])-1)/2.0)
		counter += num_of_children[n]
		if counter == num_busses:
			break

	ax.scatter(X,Y,s=20, c='k', marker="o",lw=0.1)	
	for i in range(0,num_busses):
		ax.annotate(str(i), xy=(X[i],Y[i]),fontsize=10)
	
	### PLOT LINES
	for i in range(0,len(adj),2):
		id_1,id_2 = adj[i]
		ax.plot([X[id_1],X[id_2]],[Y[id_1],Y[id_2]], lw=0.5,color="k")

	### PLOT COSMETICS
	ax.tick_params(axis='both', which='both', bottom='off', top='off', left='off', right='off', labelleft='off', labelbottom='off')
	ax.set_xlim(min(X)-0.05,max(X)+0.05)
	ax.set_ylim(min(Y)-0.25,max(Y)+0.25)
	return np.array([X,Y]).transpose()


# Run load flow
def run_load_flow(args):
	
	# Unpack arguments: copy of graph, list of active powers
	g, S = args
	
	# Do not modify the original graph
	g = copy.deepcopy(g)

	# Set nodal power consumptions
	for n, b in enumerate(g.busses):
		b.load = S[n]
	
	#run load flow
	theta, v = NR_solver(g,1e-8,20)
	return v
	
	
# Main
def main():
	
	# Load graph
	busses, lines, S_BASE = load_MATPOWER("case100.m")
	g = Electrical_network(busses, lines, S_BASE)
	num_busses = len(g.busses)
	
	fn = "Load_C"
	# Load active power timeseries
	P_data = np.load(fn+str(".npy"))
	# Added slack column
	P_data = np.concatenate((np.zeros((len(P_data),1)), P_data), axis = 1)
	# Power factor for reactive power conversion
	power_factor = 0.25
	S_data = P_data + 1j*P_data*0.25

	# Get number of available processors
	cpu_nb = multiprocessing.cpu_count()
	pool = multiprocessing.Pool(cpu_nb)
	
	# Parameters for the parallel load flow
	param = [(g, S_data[t,:]) for t in range(0,len(P_data))]
	#param = [(g, S_data[t,:]) for t in range(0,100)]
	
	start = time.time()
	# Parallel load flow (nb: map returns ordered output)
	V = np.array(pool.map(run_load_flow, param))
	pool.close()
	pool.join()
	end = time.time()
	print "elapsed_time ", end-start
	
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
	fig.suptitle("Control", fontsize=25)
	mng = plt.get_current_fig_manager()
	mng.resize(*mng.window.maxsize())
	plt.show()
	
if __name__ == '__main__':
	main()
