import random as rd
import numpy as np
import rd_var
import time

# Defines the hifi function.
def hifi(param):
	
	# Defines the number of minutes in a day
	mins = 1440

	# Initializes the active power vector.
	active_power = np.zeros(mins*param["Number of Days"][0])
	
	# Repeats the following for each day.
	for j in range(int(round(param["Number of Days"][0]))):
		
		# Continues only if the day is a week day.
		if j % 7 != 5 and j % 7 != 6:
			
			# Computes a breakfast use if prob is OK.
			if 100*rd.random() <= param["Morning Prob [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Morning Time [hour]"][0]*60,
											param["Morning Time [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Morning Duration [min]"][0],
										param["Morning Duration [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				
			# Computes a lunch use if prob is OK.
			if 100*rd.random() <= param["Afternoon Prob [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Afternoon Time [hour]"][0]*60,
											param["Afternoon Time [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Afternoon Duration [min]"][0],
										param["Afternoon Duration [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				
			# Computes a dinner use if prob is OK.
			if 100*rd.random() <= param["Evening Prob [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Evening Time [hour]"][0]*60,
											param["Evening Time [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Evening Duration [min]"][0],
										param["Evening Duration [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
					
		# Continues only if the day is a weekend day.
		if j % 7 == 5 or j % 7 == 6:
			
			# Computes a breakfast use if prob is OK.
			if 100*rd.random() <= param["Morning Prob (WE) [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Morning Time (WE) [hour]"][0]*60,
											param["Morning Time (WE) [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Morning Duration (WE) [min]"][0],
										param["Morning Duration (WE) [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power

			# Computes a lunch use if prob is OK.
			if 100*rd.random() <= param["Afternoon Prob (WE) [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Afternoon Time (WE) [hour]"][0]*60,
											param["Afternoon Time (WE) [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Afternoon Duration (WE) [min]"][0],
										param["Afternoon Duration (WE) [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power

			# Computes a dinner use if prob is OK.
			if 100*rd.random() <= param["Evening Prob (WE) [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Evening Time (WE) [hour]"][0]*60,
											param["Evening Time (WE) [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Evening Duration (WE) [min]"][0],
										param["Evening Duration (WE) [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
	
	return active_power
 
