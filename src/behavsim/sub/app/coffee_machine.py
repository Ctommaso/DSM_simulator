import random as rd
import numpy as np
import rd_var

# Defines the coffee_machine function.
def coffee_machine(param):
	
	# Defines the number of minutes in a day
	mins = 1440
	
	# Initializes the active power vector.
	active_power = np.zeros(mins*param["Number of Days"][0])
		
	# Repeats the following for each day.
	for j in range(int(round(param["Number of Days"][0]))):
			
		earliest = 0
		latest = 0
		
		# Continues only if the day is a week day.
		if j % 7 != 5 and j % 7 != 6:

			# Computes a breakfast use if prob is OK.
			if 100*rd.random() <= param["Breakfast Prob [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Breakfast Time [hour]"][0]*60,
											param["Breakfast Time [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Duration [min]"][0], param["Duration [min]"][1], True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				if earliest == 0:
					earliest = l2
				if l1 > latest:
					latest = l1
					
			# Computes a lunch use if prob is OK.
			if 100*rd.random() <= param["Lunch Prob [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Lunch Time [hour]"][0]*60,
											param["Lunch Time [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Duration [min]"][0], param["Duration [min]"][1], True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				if earliest == 0:
					earliest = l2
				if l1 > latest:
					latest = l1
				
			# Computes a dinner use if prob is OK.
			if 100*rd.random() <= param["Dinner Prob [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Dinner Time [hour]"][0]*60,
											param["Dinner Time [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Duration [min]"][0], param["Duration [min]"][1], True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				if earliest == 0:
					earliest = l2
				if l1 > latest:
					latest = l1
					
		# Continues only if the day is a weekend day.
		if j % 7 == 5 or j % 7 == 6:
			
			# Computes a breakfast use if prob is OK.
			if 100*rd.random() <= param["Breakfast Prob (WE) [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Breakfast Time (WE) [hour]"][0]*60,
											param["Breakfast Time (WE) [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Duration [min]"][0], param["Duration [min]"][1], True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				if earliest == 0:
					earliest = l2
				if l1 > latest:
					latest = l1

			# Computes a lunch use if prob is OK.
			if 100*rd.random() <= param["Lunch Prob (WE) [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Lunch Time (WE) [hour]"][0]*60,
											param["Lunch Time (WE) [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Duration [min]"][0], param["Duration [min]"][1], True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				if earliest == 0:
					earliest = l2
				if l1 > latest:
					latest = l1

			# Computes a dinner use if prob is OK.
			if 100*rd.random() <= param["Dinner Prob (WE) [%]"][0]:
				l1 = mins*j+rd_var.norm(param["Dinner Time (WE) [hour]"][0]*60,
											param["Dinner Time (WE) [hour]"][1]*60,
											True)
				l2 = l1+rd_var.norm(param["Duration [min]"][0], param["Duration [min]"][1], True)
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				active_power[l1:l2] += power
				if earliest == 0:
					earliest = l2
				if l1 > latest:
					latest = l1
						
		# Computes the periodic heatings if the water is kept warm.
		if param["Keeps Water Warm?"][0] == "Yes":
			l1 = mins*j
			l2 = mins*(j+1)
			daily_ac = active_power[l1:l2]
			nz_daily_ac = np.nonzero(daily_ac)
			nz_daily_ac = nz_daily_ac[0]
			index_on = []
			index_off = []
			for k in range(1, len(nz_daily_ac)):
				if nz_daily_ac[k]-nz_daily_ac[k-1] > 1:
					index_on.append(mins*j+nz_daily_ac[k])
					index_off.append(mins*j+nz_daily_ac[k-1])
			for k in range(len(index_on)):
				power = rd_var.norm(param["Power [W]"][0], param["Power [W]"][1], False)
				dt = rd_var.norm(param["Inter Heating Time [min]"][0],
									 param["Inter Heating Time [min]"][1],
									 True)
				active_power[index_off[k]+dt:index_on[k]:dt] = power
 
	return active_power
