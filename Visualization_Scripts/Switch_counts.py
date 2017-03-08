import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib import rc

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

def plot_switch_counts(city,*standalone):
	
	# Load data
	fn_smart_B = "Results_"+city+"/Switch_counts_Control_B.dat"
	fn_smart = "Results_"+city+"/Switch_counts_Control.dat"
	fn_thermostat = "Results_"+city+"/Switch_counts_Thermostat.dat"
	
	res_smart_B=np.loadtxt(fn_smart_B)
	res_smart_B=res_smart_B.astype(float)
	res_smart=np.loadtxt(fn_smart)
	res_smart=res_smart.astype(float)
	res_thermostat = np.loadtxt(fn_thermostat)
	res_thermostat=res_thermostat.astype(float)
	
	# Switching statistics
	print "THERMOSTAT:"
	print "Highest number of ON switchings", np.amax(res_thermostat)
	print "Average number of ON switchings =", np.mean(res_thermostat)
	print "Standard deviation=", np.std(res_thermostat)
	print "SMART:"
	print "Highest number of ON switchings", np.amax(res_smart)
	print "Average number of ON switchings =", np.mean(res_smart)
	print "Standard deviation=", np.std(res_smart)
	"""
	print "SMART + BATTERIES:"
	print "Highest number of ON switchings", np.amax(res_smart_B)
	print "Average number of ON switchings =", np.mean(res_smart_B)
	print "Standard deviation=", np.std(res_smart_B)
	"""
	# Computes the increase factor in the number of switching between control and thermostat
	increase=res_smart/res_thermostat
	"""
	increase_B=res_smart_B/res_thermostat
	"""
	
	# Plotting part
	fig, ax1=plt.subplots(1)
	fig.set_size_inches(18, 7, forward=True)
	fig.subplots_adjust(right=0.95, left=0.10,top=0.95,bottom=0.18)
	ax1.set_xlabel(r"Thermostat Switching", fontsize=40)
	ax1.set_ylabel(r"Increase factor", fontsize=40)
	ax1.tick_params(axis='both', which='major', labelsize=40)
	
	for i in range(0,len(increase)):
		plt.annotate(str(i), (res_thermostat[i],increase[i]))
	plt.plot(res_thermostat,increase,'ro',mec='r', label="Control")
	"""
	for i in range(0,len(increase_B)):
		plt.annotate(str(i), (res_thermostat[i],increase_B[i]))
	plt.plot(res_thermostat,increase_B,'bx',label="Control + Battery")
	"""
	plt.savefig("Results_"+city+"/Switching.pdf",format='pdf',dvi=700)
	ax1.legend()

	if not standalone:
		plt.ion()
	plt.show()
	
def main():
	
	standalone=True
	city=sys.argv[1]
	plot_switch_counts(city,standalone)

if __name__ == '__main__':
    main()
