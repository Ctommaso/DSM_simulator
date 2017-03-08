import random as rd
import numpy as np
import rd_var

# Defines the microwave function.
def microwave(param):
	
	# Defines the number of minutes in a day
	mins = 1440
	
	# Initializes the active power vector.
	active_power = np.zeros(mins*param["Number of Days"][0])
	
	# Repeats the following for each day.
	for j in range(int(round(param["Number of Days"][0]))):
		
		# Continues only if the day is a week day.
		if j % 7 != 5 and j % 7 != 6:
			
			# Computes a breakfast use if prob is OK.
			if 100*rd.random() <= param["Breakfast Prob [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Breakfast Time [hour]"][0]*60,
											param["Breakfast Time [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Breakfast Duration [min]"][0],
										param["Breakfast Duration [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				
			# Computes a lunch use if prob is OK.
			if 100*rd.random() <= param["Lunch Prob [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Lunch Time [hour]"][0]*60,
											param["Lunch Time [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Lunch Duration [min]"][0],
										param["Lunch Duration [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				
			# Computes a dinner use if prob is OK.
			if 100*rd.random() <= param["Dinner Prob [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Dinner Time [hour]"][0]*60,
											param["Dinner Time [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Dinner Duration [min]"][0],
										param["Dinner Duration [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				
		# Continues only if the day is a weekend day.
		if j % 7 == 5 or j % 7 == 6:
			
			# Computes a breakfast use if prob is OK.
			if 100*rd.random() <= param["Breakfast Prob (WE) [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Breakfast Time (WE) [hour]"][0]*60,
											param["Breakfast Time (WE) [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Breakfast Duration (WE) [min]"][0],
										param["Breakfast Duration (WE) [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power

			# Computes a lunch use if prob is OK.
			if 100*rd.random() <= param["Lunch Prob (WE) [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Lunch Time (WE) [hour]"][0]*60,
											param["Lunch Time (WE) [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Lunch Duration (WE) [min]"][0],
										param["Lunch Duration (WE) [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power

			# Computes a dinner use if prob is OK.
			if 100*rd.random() <= param["Dinner Prob (WE) [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Dinner Time (WE) [hour]"][0]*60,
											param["Dinner Time (WE) [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Dinner Duration (WE) [min]"][0],
										param["Dinner Duration (WE) [min]"][1],
										True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
	
	return active_power
