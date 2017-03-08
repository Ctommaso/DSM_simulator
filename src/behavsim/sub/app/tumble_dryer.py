import random as rd
import numpy as np
import rd_var

# Defines the tumble_dryer function.
def tumble_dryer(param):
	
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
					
				# Computes the beginning of the cycle.
				l1 = int(l2+rd_var.uni(0, win, True))
					
				# Computes the duration of the first phase.
				l2 = l1+rd_var.norm(param["High Duration [min]"][0], param["High Duration [min]"][1], True)
					
				# Computes the parameters of the first phase.
				power = rd_var.norm(param["High Power [W]"][0], param["High Power [W]"][1], False)
				active_power[l1:l2] += power
				l1 = l2
					
				# Computes the duration of the third phase.
				l2 = l1+rd_var.norm(param["Low Duration [min]"][0], param["Low Duration [min]"][1], True)
					
				# Computes the parameters of the second phase.
				power = rd_var.norm(param["Low Power [W]"][0], param["Low Power [W]"][1], False)
				active_power[l1:l2] += power
				l1 = l2
	
	return active_power
