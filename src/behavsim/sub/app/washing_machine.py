import random as rd
import numpy as np
import rd_var

# Defines the washing_machine function.
def washing_machine(param):
	
	# Defines the number of minutes in a day
	mins = 1440
		
	# Initializes the active power vector.
	active_power = np.zeros(mins*param["Number of Days"][0])
	
	# Repeats the following for each day.
	for j in range(int(round(param["Number of Days"][0]))):
		
		# Defines the default number of cycles (0)
		cycles = 0
		
		# Computes the number of cycles if prob is OK.
		if 100*rd.random() <= param["Probability [%]"][0]:
			cycles = rd_var.norm(param["Number of Cycles"][0], param["Number of Cycles"][1], True, trunc_neg=0)
		
		# Continnues only if the number of cycles is not 0.
		if cycles != 0:
			
			# Computes the time window of each cycle.
			win = int(round(60*(param["Latest Start [hour]"][0]-param["Earliest Start [hour]"][0])/cycles))
			
			# Initialises the end of last cycle.
			l2 = int(mins*j+60*param["Earliest Start [hour]"][0])
			
			# Repeats the following for each cycle.
			for k in range(cycles):
				
				# Computes the number of heating cycles.						
				heat = rd_var.norm(param["Number of Heatings"][0],
									   param["Number of Heatings"][1],
									   True,
									   trunc_neg=-1)
				
				# Computes the beginning of the cycle.
				l1 = int(l2+rd_var.uni(0, win, True))
				
				# Repeats the following for each heating cycle.
				for l in range(heat):
					
					# Computes the parameters of the short washing.
					l2 = l1+rd_var.norm(param["Inter Heating Delay [min]"][0],
											param["Inter Heating Delay [min]"][1],
											True)
					power = rd_var.norm(param["Washing Power [W]"][0], param["Washing Power [W]"][1], False)
					active_power[l1:l2] += power
					l1 = l2
					
					# Computes the parameters of the heating.
					l2 = l1+rd_var.norm(param["Heating Duration [min]"][0],
											param["Heating Duration [min]"][1],
											True)
					power = rd_var.norm(param["Heating Power [W]"][0], param["Heating Power [W]"][1], False)
					active_power[l1:l2] += power
					l1 = l2
				
				# Computes the parameters of the washing.
				l2 = l1+rd_var.norm(param["Washing Duration [min]"][0],
										param["Washing Duration [min]"][1],
										True)
				power = rd_var.norm(param["Washing Power [W]"][0], param["Washing Power [W]"][1], False)
				active_power[l1:l2] += power
				l1 = l2
					
				# Computes the parameters of the spinning.
				l2 = l1+rd_var.norm(param["Spinning Duration [min]"][0],
										param["Spinning Duration [min]"][1],
										True)
				power = rd_var.norm(param["Spinning Power [W]"][0], param["Spinning Power [W]"][1], False)
				active_power[l1:l2] += power
				l1 = l2

	return active_power
