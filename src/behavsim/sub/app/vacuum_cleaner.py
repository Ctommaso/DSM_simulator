import random as rd
import numpy as np
import rd_var

# Defines the vacuum_cleaner function.
def vacuum_cleaner(param):
	
	# Defines the number of minutes in a day
	mins = 1440

	# Initializes the active power vector.
	active_power = np.zeros(mins*param["Number of Days"][0])
		
	# Repeats the following for each day.
	for j in range(int(round(param["Number of Days"][0]))):
		
		# Continues only if prob is OK.
		if 100*rd.random() <= param["Probability [%]"][0]:
		
			# Computes the cycle.
			l1 = mins*j+rd_var.uni(param["Earliest Start [hour]"][0]*60,
									   param["Latest Start [hour]"][0]*60-param["Earliest Start [hour]"][0]*60,
									   True)
			l2 = l1+rd_var.norm(param["Duration [min]"][0], param["Duration [min]"][1], True)
			power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
			active_power[l1:l2] += power
	
	return active_power
