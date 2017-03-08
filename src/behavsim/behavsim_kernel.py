import numpy as np
import os
import sys
import sub.app as app
from collections import OrderedDict
import multiprocessing
import matplotlib.pyplot as plt

# Initialize and run behavsim simulation for the different appliances.
def initialize_param(params):
	
	# Unpack the simulation parameters defined by the user
	# params=(days,smart_washers)
	(days,smart_washers)=params
	
	# Number of minutes in one day.
	mins = 1440
	
	# Directory of the default appliance configurations.
	#directory="default_config/" #Directory for all behavsim applications
	directory="src/behavsim/default_config_autoquar/"
	
	# Aggregated power initialization.
	active_power=np.zeros(mins*days)
	
	# Loop over all configuration files.
	for fn in os.listdir(directory):
		if fn.endswith(".csv"):
			
			# Opens configuration file.
			fid = open(os.path.join(directory, fn),'r')

			# Gets next line, removes ending \n and defines the key values.
			line = next(fid)
			line = line.strip()
			key = line.split(",")

			# Gets next line, removes ending \n and defines the mu values.
			line = next(fid)
			line = line.strip()
			mu = line.split(",")
            
			# Gets next line, removes ending \n and defines the sigma values.
			line = next(fid)
			line = line.strip()
			sigma = line.split(",")
			
			# Builds the ordered dictionary for the current appliance.
			param = OrderedDict([('Number of Days',[days,'-'])]+[dictionary_entry(key[i],mu[i],sigma[i]) for i in range(0,len(key))])
			
			# Change start and end times of the washing machine if we simulate smart washers
			if smart_washers==True and param['Name of the Simulation'][0]=='washing_machine':
				param['Earliest Start [hour]'][0]=10.0
				param['Latest Start [hour]'][0]=14.0
				
			# Run behavsim for the current appliance and aggregate the active power
			# If the appliance is not the boiler.
			appliance=param['Name of the Simulation'][0]
			if appliance !='boiler':
				results_app=eval("app.%s(param)" % appliance)
				active_power+=results_app
			else:
				hot_water_consumption=eval("app.%s(param)" % appliance)
				
	return active_power, hot_water_consumption
	
# Builds the dictionnary entry.
def dictionary_entry(key,mu,sigma):

	if sigma == "-":
		if key == "Name of the Simulation":
			return (key,[mu,sigma])
		elif key == "Keeps Water Warm?":
			return (key,[mu,sigma])
		elif key == "Induction?":
			return (key,[mu,sigma])
		elif key == "Number of People":
			return (key,[int(mu),sigma])
		else:
			return (key,[float(mu),sigma])
	else:
		return (key,[float(mu),float(sigma)])

# Runs the behavsim smulation parallelized over houses
def run_behavsim(houses,days,smart_washers):
	
	# Determines number of available cpus in the machine
	cpu_nb = multiprocessing.cpu_count()
	
	# Pool of working processes
	pool = multiprocessing.Pool(cpu_nb)
    
    # Run in parallel the simulations for the different houses
	results = np.array(pool.map(initialize_param,[(days,smart_washers) for i in range(0,houses)]))
	
	# Row indices for time and column indices for houses
	active_power=results[:,0].transpose()
	hot_water=results[:,1].transpose()
	
	del results 
	
	return active_power,hot_water
	
# Defines the main function.
def main():
	
	# Initialize the number of houses in the simulation.
	houses=int(sys.argv[1])
	
	# Initialize the number of days in the simulation.
	days=int(sys.argv[2])
	
	# Determine whether washers are smart or not
	smart_washers=True if sys.argv[3]=='True' else False
	
	# Run behavsim simulation
	a,h=run_behavsim(houses, days, smart_washers)
	
	plot_behavsim(a,h)
	
# Plot behavsim results
def plot_behavsim(active_power,hot_water):
	
	f, ax=plt.subplots(2,sharex=True)
	
	ax[0].plot(active_power.sum(axis=1), label="Total Active Power")
	ax[1].plot(hot_water.sum(axis=1), label="Total Hot Water")
	labels=[n for n in range(0,len(active_power)/1440)]
	ticks=[n*1440 for n in range(0,len(active_power)/1440)]
	ax[0].set_xlabel(labels)
	ax[0].xaxis.set_ticks(ticks)
	ax[1].set_xlabel(labels)
	ax[1].xaxis.set_ticks(ticks)
	plt.legend()
	plt.show()
	
# Executes the following only if behavsim-test.py is directly executed.
if __name__ == "__main__":
    
	# Calls main function.
	main()
