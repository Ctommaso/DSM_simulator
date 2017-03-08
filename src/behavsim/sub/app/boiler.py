import random as rd
import numpy as np
import rd_var

# Defines the boiler function.
def boiler(param):
	
	# Defines the number of minutes in a day
	mins = 1440
	
	# Initializes the active power vector.
	volume = np.zeros(mins*param["Number of Days"][0])
		
	# Repeats the following for each day.
	for j in range(int(round(param["Number of Days"][0]))):
		
		# Repeats the following for each person.
		for k in range(int(round(param["Number of People"][0]))):
			
			# Continues only if the day is a week day.
			if j % 7 != 5 and j % 7 != 6:
				
				# Computes a morning bath if prob is OK.
				if 100*rd.random() <= param["Bath Morning Prob [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Morning Time [hour]"][0]*60,
												param["Morning Time [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Bath Duration [min]"][0],
											param["Bath Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Bath Flow [l/min]"][0], param["Bath Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol
					
				# Computes an afternoon bath if prob is OK.
				if 100*rd.random() <= param["Bath Afternoon Prob [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Afternoon Time [hour]"][0]*60,
												param["Afternoon Time [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Bath Duration [min]"][0],
											param["Bath Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Bath Flow [l/min]"][0], param["Bath Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol
					
				# Computes an evening bath if prob is OK.
				if 100*rd.random() <= param["Bath Evening Prob [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Evening Time [hour]"][0]*60,
												param["Evening Time [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Bath Duration [min]"][0],
											param["Bath Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Bath Flow [l/min]"][0], param["Bath Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol
						
				# Computes a morning shower if prob is OK.
				if 100*rd.random() <= param["Shower Morning Prob [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Morning Time [hour]"][0]*60,
												param["Morning Time [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Shower Duration [min]"][0],
											param["Shower Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Shower Flow [l/min]"][0], param["Shower Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol
					
				# Computes an afternoon shower if prob is OK.
				if 100*rd.random() <= param["Shower Afternoon Prob [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Afternoon Time [hour]"][0]*60,
												param["Afternoon Time [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Shower Duration [min]"][0],
											param["Shower Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Shower Flow [l/min]"][0], param["Shower Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol
					
				# Computes an evening shower if prob is OK.
				if 100*rd.random() <= param["Shower Evening Prob [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Evening Time [hour]"][0]*60,
												param["Evening Time [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Shower Duration [min]"][0],
											param["Shower Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Shower Flow [l/min]"][0], param["Shower Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol
					
			# Continues only if the day is a weekend day.
			if j % 7 == 5 or j % 7 == 6:

				# Computes a morning bath if prob is OK.
				if 100*rd.random() <= param["Bath Morning Prob (WE) [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Morning Time (WE) [hour]"][0]*60,
												param["Morning Time (WE) [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Bath Duration [min]"][0],
											param["Bath Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Bath Flow [l/min]"][0], param["Bath Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol

				# Computes an afternoon bath if prob is OK.
				if 100*rd.random() <= param["Bath Afternoon Prob (WE) [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Afternoon Time (WE) [hour]"][0]*60,
												param["Afternoon Time (WE) [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Bath Duration [min]"][0],
											param["Bath Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Bath Flow [l/min]"][0], param["Bath Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol

				# Computes an evening bath if prob is OK.
				if 100*rd.random() <= param["Bath Evening Prob (WE) [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Evening Time (WE) [hour]"][0]*60,
												param["Evening Time (WE) [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Bath Duration [min]"][0],
											param["Bath Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Bath Flow [l/min]"][0], param["Bath Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol

				# Computes a morning shower if prob is OK.
				if 100*rd.random() <= param["Shower Morning Prob (WE) [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Morning Time (WE) [hour]"][0]*60,
												param["Morning Time (WE) [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Shower Duration [min]"][0],
											param["Shower Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Shower Flow [l/min]"][0], param["Shower Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol

				# Computes an afternoon shower if prob is OK.
				if 100*rd.random() <= param["Shower Afternoon Prob (WE) [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Afternoon Time (WE) [hour]"][0]*60,
												param["Afternoon Time (WE) [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Shower Duration [min]"][0],
											param["Shower Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Shower Flow [l/min]"][0], param["Shower Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol

				# Computes an evening shower if prob is OK.
				if 100*rd.random() <= param["Shower Evening Prob (WE) [%]"][0]:
					l1 = mins*j+rd_var.norm(param["Evening Time (WE) [hour]"][0]*60,
												param["Evening Time (WE) [hour]"][1]*60,
												True)
					l2 = l1+rd_var.norm(param["Shower Duration [min]"][0],
											param["Shower Duration [min]"][1],
											True)
					vol = rd_var.norm(param["Shower Flow [l/min]"][0], param["Shower Flow [l/min]"][1], False)/3
					volume[l1:l2] += vol

			# Computes the number of times the sink is used.
			sink = rd_var.norm(param["Sink Cycles"][0], param["Sink Cycles"][1], True)

			# Repeats the following for each sink utilisation.
			for l in range(sink):
					
				# Computes the sink start, end and consumption.
				l1 = mins*j+rd_var.uni(0, mins, True)
				l2 = l1+rd_var.norm(param["Sink Duration [min]"][0], param["Sink Duration [min]"][1], True)
				vol = rd_var.norm(param["Sink Flow [l/min]"][0], param["Sink Flow [l/min]"][1], False)/3
				volume[l1:l2] += vol

	return volume
