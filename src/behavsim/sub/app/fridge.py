import random as rd
import numpy as np
import rd_var
import math

# Defines the fridge function.
def fridge(param):
	
	# Defines the number of minutes in a day.
	mins = 1440
	
	# Initializes the active power vector.
	active_power = np.zeros(mins*param["Number of Days"][0])
	
	# Computes the parameters of the first period.
	on = rd_var.norm(param["Compressor On [min]"][0], param["Compressor On [min]"][1], True)
	off = rd_var.norm(param["Compressor Off [min]"][0], param["Compressor Off [min]"][1], True)
	power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
	peak_power = rd_var.norm(param["Power [W]"][0]/2.0, param["Power [W]"][0]/2.0, False, trunc_neg=-1,
								 trunc_pos=1)
	
	# Computes the first period.
	tmp_power = np.zeros(on+off)
	tmp_power[0:on] = power
	for j in range(on):
		tmp_power[j] += peak_power*math.exp(-j)
		
	# Select initial point.
	start = rd_var.uni(0, on+off, True)
	tmp_power = tmp_power[start:]
	
	# Adds the initial period.
	l1 = 0
	l2 = len(tmp_power)
	active_power[l1:l2] += tmp_power
	
	# Repeats the following until the end of the time vector.
	skip = False
	while l2 < mins*param["Number of Days"][0]:
		
		# Computes the parameters of the period.
		on = rd_var.norm(param["Compressor On [min]"][0], param["Compressor On [min]"][1], True)
		off = rd_var.norm(param["Compressor Off [min]"][0], param["Compressor Off [min]"][1], True)
		power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
		peak_power = rd_var.norm(param["Power [W]"][0]/2.0, param["Power [W]"][0]/2.0, False, trunc_neg=-1,
									 trunc_pos=1)
		if skip:
			on += on
			skip = False
		 
		# Computes and adds the period.
		tmp_power = np.zeros(on+off)
		tmp_power[0:on] = power
		for j in range(on):
			tmp_power[j] += peak_power*math.exp(-j)
		l1 = l2
		l2 = min(l1+len(tmp_power), mins*param["Number of Days"][0])
		if 100*rd.random() <= param["Cycle Probability [%]"][0]:
			active_power[l1:l2] += tmp_power[:l2-l1]
		else:
			skip = True

	return active_power
