import numpy as np
import rd_var

# Defines the lighting function.
def lighting(param):
	
	# Defines the number of minutes in a day
	mins = 1440
	
	# Initializes the active power vector.
	active_power = np.zeros(mins*param["Number of Days"][0])
		
	# Repeats the following for each day.
	for j in range(int(round(param["Number of Days"][0]))):
			
		# Continues only if the day is a week day.
		if j % 7 != 5 and j % 7 != 6:
			
			# Computes the morning bedrooms consumption.
			l1 = mins*j+rd_var.norm(param["Bedrooms Morning Time [h]"][0]*60,
										param["Bedrooms Morning Time [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Bedrooms Morning Duration [min]"][0],
									param["Bedrooms Morning Duration [min]"][1],
									True)
			power = rd_var.norm(param["Bedrooms Power [W]"][0], param["Bedrooms Power [W]"][1], False)
			active_power[l1:l2] += power
				
			# Computes the evening bedrooms consumption.
			l1 = mins*j+rd_var.norm(param["Bedrooms Evening Time [h]"][0]*60,
										param["Bedrooms Evening Time [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Bedrooms Evening Duration [min]"][0],
									param["Bedrooms Evening Duration [min]"][1],
									True)
			power = rd_var.norm(param["Bedrooms Power [W]"][0], param["Bedrooms Power [W]"][1], False)
			active_power[l1:l2] += power
				
			# Computes the morning bathrooms consumption.
			l1 = mins*j+rd_var.norm(param["Bathrooms Morning Time [h]"][0]*60,
										param["Bathrooms Morning Time [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Bathrooms Morning Duration [min]"][0],
									param["Bathrooms Morning Duration [min]"][1],
									True)
			power = rd_var.norm(param["Bathrooms Power [W]"][0], param["Bathrooms Power [W]"][1], False)
			active_power[l1:l2] += power
				
			# Computes the evening bathrooms consumption.
			l1 = mins*j+rd_var.norm(param["Bathrooms Evening Time [h]"][0]*60,
										param["Bathrooms Evening Time [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Bathrooms Evening Duration [min]"][0],
									param["Bathrooms Evening Duration [min]"][1],
									True)
			power = rd_var.norm(param["Bathrooms Power [W]"][0], param["Bathrooms Power [W]"][1], False)
			active_power[l1:l2] += power
				
			# Computes the morning kitchen consumption.
			l1 = mins*j+rd_var.norm(param["Kitchen Morning Time [h]"][0]*60,
										param["Kitchen Morning Time [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Kitchen Morning Duration [min]"][0],
									param["Kitchen Morning Duration [min]"][1],
									True)
			power = rd_var.norm(param["Kitchen Power [W]"][0], param["Kitchen Power [W]"][1], False)
			active_power[l1:l2] += power
				
			# Computes the evening kitchen consumption.
			l1 = mins*j+rd_var.norm(param["Kitchen Evening Time [h]"][0]*60,
										param["Kitchen Evening Time [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Kitchen Evening Duration [min]"][0],
									param["Kitchen Evening Duration [min]"][1],
									True)
			power = rd_var.norm(param["Kitchen Power [W]"][0], param["Kitchen Power [W]"][1], False)
			active_power[l1:l2] += power

		# Continues only if the day is a weekend day.
		if j % 7 == 5 or j % 7 == 6:

			# Computes the morning bedrooms consumption.
			l1 = mins*j+rd_var.norm(param["Bedrooms Morning Time (WE) [h]"][0]*60,
										param["Bedrooms Morning Time (WE) [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Bedrooms Morning Duration [min]"][0],
									param["Bedrooms Morning Duration [min]"][1],
									True)
			power = rd_var.norm(param["Bedrooms Power [W]"][0], param["Bedrooms Power [W]"][1], False)
			active_power[l1:l2] += power

			# Computes the evening bedrooms consumption.
			l1 = mins*j+rd_var.norm(param["Bedrooms Evening Time (WE) [h]"][0]*60,
										param["Bedrooms Evening Time (WE) [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Bedrooms Evening Duration [min]"][0],
									param["Bedrooms Evening Duration [min]"][1],
									True)
			power = rd_var.norm(param["Bedrooms Power [W]"][0], param["Bedrooms Power [W]"][1], False)
			active_power[l1:l2] += power

			# Computes the morning bathrooms consumption.
			l1 = mins*j+rd_var.norm(param["Bathrooms Morning Time (WE) [h]"][0]*60,
										param["Bathrooms Morning Time (WE) [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Bathrooms Morning Duration [min]"][0],
									param["Bathrooms Morning Duration [min]"][1],
									True)
			power = rd_var.norm(param["Bathrooms Power [W]"][0], param["Bathrooms Power [W]"][1], False)
			active_power[l1:l2] += power

			# Computes the evening bathrooms consumption.
			l1 = mins*j+rd_var.norm(param["Bathrooms Evening Time (WE) [h]"][0]*60,
										param["Bathrooms Evening Time (WE) [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Bathrooms Evening Duration [min]"][0],
									param["Bathrooms Evening Duration [min]"][1],
									True)
			power = rd_var.norm(param["Bathrooms Power [W]"][0], param["Bathrooms Power [W]"][1], False)
			active_power[l1:l2] += power

			# Computes the morning kitchen consumption.
			l1 = mins*j+rd_var.norm(param["Kitchen Morning Time (WE) [h]"][0]*60,
										param["Kitchen Morning Time (WE) [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Kitchen Morning Duration [min]"][0],
									param["Kitchen Morning Duration [min]"][1],
									True)
			power = rd_var.norm(param["Kitchen Power [W]"][0], param["Kitchen Power [W]"][1], False)
			active_power[l1:l2] += power

			# Computes the evening kitchen consumption.
			l1 = mins*j+rd_var.norm(param["Kitchen Evening Time (WE) [h]"][0]*60,
										param["Kitchen Evening Time (WE) [h]"][1]*60,
										True)
			l2 = l1+rd_var.norm(param["Kitchen Evening Duration [min]"][0],
									param["Kitchen Evening Duration [min]"][1],
									True)
			power = rd_var.norm(param["Kitchen Power [W]"][0], param["Kitchen Power [W]"][1], False)
			active_power[l1:l2] += power

		# Computes the evening lounge consumption.
		l1 = mins*j+rd_var.norm(param["Lounge Evening Time [h]"][0]*60,
									param["Lounge Evening Time [h]"][1]*60,
									True)
		l2 = l1+rd_var.norm(param["Lounge Evening Duration [min]"][0],
								param["Lounge Evening Duration [min]"][1],
								True)
		power = rd_var.norm(param["Lounge Power [W]"][0], param["Lounge Power [W]"][1], False)
		active_power[l1:l2] += power
				
		# No light between 8 am and 6 pm in the summer.
		if 90 <= j <= 272:
			active_power[mins*j+480:mins*j+1080] = 0
	
	return active_power
