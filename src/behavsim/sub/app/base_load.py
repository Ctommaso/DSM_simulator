import numpy as np
import rd_var

# Defines the base_load function.
def base_load(param):
	
	# Defines the number of minutes in a day
	mins = 1440
	
	# Initializes the active power vector.
	active_power = np.zeros(mins*param["Number of Days"][0])
	
	# Computes the base load.
	l2 = 0
	while l2 < len(active_power):
		l1 = l2
		l2 = l1+rd_var.norm(param["Duration [hour]"][0]*60, param["Duration [hour]"][1]*60, True)
		power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False, trunc_neg=-1, trunc_pos=1)
		active_power[l1:l2] += power
	
	return active_power
