from Tkinter import *
from PIL import Image
import os
import shutil
import numpy as np
import sys
import platform
import gc
from pympler.tracker import SummaryTracker
from src.behavsim.behavsim_kernel import run_behavsim
from Visualization_Scripts.Aggregated_Load import plot_aggregated_load
from Visualization_Scripts.Battery_Usage import plot_battery_usage
from Visualization_Scripts.Self_Consumption import plot_self_consumption
from Visualization_Scripts.Line_Load import plot_line_load
from Visualization_Scripts.Switch_counts import plot_switch_counts
from Visualization_Scripts.Boiler_Consumption import plot_boilers


class Simulator(object):
	# DEFINE SIMULATOR
	def __init__(self, master):
		
		self.master = master
		# Simulation parameters
		self.num_nodes = 0
		self.start_day = 0
		self.num_days = 0
		self.PV_surface = 0
		self.PV_peak_power = StringVar()
		self.PV_peak_power.set("")
		self.PV_efficiency=0.18
		self.average_window_surf=10
		self.R90 = None
		self.R40 = None
		self.T = None
		self.Residual_load = None
		self.Domestic_appliances = None
		self.Hot_water = None
		self.city_choices = ["Fribourg","Lausanne","Geneve","Sion","Zurich","Ljubljana","London","Milan","Paris"]
		self.city = StringVar()
		self.city.set("select")
		self.smart_washers = None
		self.smart_washers_label = StringVar()
		self.smart_washers_label.set("select")
		self.simulate_boilers = None
		self.boilers_label = StringVar()
		self.boilers_label.set("select")
		self.battery_capacity = 0
		self.battery_power = 0

		self.simulation_over=False
		self.message=StringVar()
		self.message.set("STATUS: Enter simulation parameters")
		
		self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
		
		# Icons
		houses_image = PhotoImage(file='icons/houses60x60.gif')
		start_day_image = PhotoImage(file='icons/start_day60x60.gif')
		num_days_image = PhotoImage(file='icons/num_days60x60.gif')
		PV_image = PhotoImage(file='icons/PV60x60.gif')
		city_image = PhotoImage(file='icons/city60x60.gif')
		boiler_image = PhotoImage(file='icons/hot60x60.gif')
		washer_image = PhotoImage(file='icons/laundry-service60x60.gif')
		battery_cap_image = PhotoImage(file='icons/battery_capacity60x60.gif')
		battery_pow_image = PhotoImage(file='icons/battery_power60x60.gif')
		
		# Labels
		self.label_message = Label(master, textvariable=self.message,height=1,font=("Helvetica", 15),fg='red',bg='white')
		self.label_nodes = Label(master, text="Number of Houses:",image=houses_image,font=("Helvetica", 12),fg='black',bg='white',compound = 'left')
		self.label_nodes.photo=houses_image
		self.label_start_day = Label(master, text="Starting day:",image=start_day_image,font=("Helvetica", 12),fg='black',bg='white',compound= 'left')
		self.label_start_day.photo=start_day_image
		self.label_num_days = Label(master, text="Number of days:",image=num_days_image,font=("Helvetica", 12),fg='black',bg='white',compound = 'left')
		self.label_num_days.photo=num_days_image
		self.label_PV = Label(master, text="PV surface/house [m2]:",image=PV_image,font=("Helvetica", 12),fg='black',bg='white',compound = 'left')
		self.label_PV.photo=PV_image
		self.label_PV_peak_power = Label(master, textvariable=self.PV_peak_power,font=("Helvetica", 12),fg='black',bg='white',compound = 'left')
		self.label_city = Label(master, text="City:",image=city_image,font=("Helvetica", 12),fg='black',bg='white',compound = 'left')
		self.label_city.photo=city_image
		self.label_boilers = Label(master, text="Electric boilers:",image=boiler_image,font=("Helvetica", 12),fg='black',bg='white',compound = 'left')
		self.label_boilers.photo=boiler_image
		self.label_washers = Label(master, text="Smart washers:",image=washer_image,font=("Helvetica", 12),fg='black',bg='white',compound = 'left')
		self.label_washers.photo=washer_image
		self.label_battery_capacity = Label(master, text="Battery Capacity [kWh]:",image=battery_cap_image,font=("Helvetica", 12),fg='black',bg='white',compound= 'left')
		self.label_battery_capacity.photo=battery_cap_image
		self.label_battery_power = Label(master, text="Battery Power [kW]:",image=battery_pow_image,font=("Helvetica", 12),fg='black',bg='white',compound= 'left')
		self.label_battery_power.photo=battery_pow_image
		
		# Entry menus 
		vcmd = master.register(self.validate) 
		self.entry_nodes = Entry(master, validate="key", validatecommand=(vcmd, '%P',"nodes"),font=("Helvetica", 12))
		self.entry_start_day = Entry(master, validate="key", validatecommand=(vcmd, '%P',"start day"),font=("Helvetica", 12))
		self.entry_num_days = Entry(master, validate="key", validatecommand=(vcmd, '%P',"num days"),font=("Helvetica", 12))
		self.entry_PV = Entry(master, validate="key", validatecommand=(vcmd, '%P',"PV"),font=("Helvetica", 12))
		self.entry_battery_capacity = Entry(master, validate="key", validatecommand=(vcmd, '%P',"battery capacity"),font=("Helvetica", 12))
		self.entry_battery_power = Entry(master, validate="key", validatecommand=(vcmd, '%P',"battery power"),font=("Helvetica", 12))
		self.city_menu = OptionMenu(master, self.city,  *self.city_choices, command=self.validate_city)
		self.city_menu.config(font=("Helvetica", 12),indicator=0,bg='white',fg='black')
		self.washers_menu = OptionMenu(master, self.smart_washers_label,  *["No","Yes"], command=self.validate_washers)
		self.washers_menu.config(font=("Helvetica", 12),indicator=0,bg='white',fg='black')
		self.boilers_menu = OptionMenu(master, self.boilers_label,  *["No","Yes"], command=self.validate_boilers)
		self.boilers_menu.config(font=("Helvetica", 12),indicator=0,bg='white',fg='black',compound='left')

		# Buttons
		self.run_button = Button(master, text="Run", command=self.run,font=("Helvetica", 12),bg='white',fg='black')
		self.aggregated_load_button = Button(master, text="Plot Aggregated Load", command=self.plot_aggregated_load,font=("Helvetica", 12),bg='white',fg='black')
		self.autoconsumption_button = Button(master, text="Plot Self Consumption Rate", command=self.plot_self_consumption,font=("Helvetica", 12),bg='white',fg='black')
		self.battery_button = Button(master, text="Plot Battery Usage", command=self.plot_battery_usage,font=("Helvetica", 12),bg='white',fg='black')
		self.switches_button = Button(master, text="Plot Switching Rate", command=self.plot_switch_counts,font=("Helvetica", 12),bg='white',fg='black')
		self.boiler_button = Button(master, text="Plot Boiler Details", command=self.plot_boilers,font=("Helvetica", 12),bg='white',fg='black')
		self.network_load_button = Button(master, text="Plot Network Load", command=self.plot_network_load,font=("Helvetica", 12),bg='white',fg='black')

		# Layout
		self.master.title("Simulator AUTOQUAR")
		self.master.configure(background='white')
		self.label_message.grid(row=0, column=0,columnspan=3, sticky=W)
		self.label_nodes.grid(row=1, column=0, sticky=W)
		self.label_start_day.grid(row=2, column=0, sticky=W)
		self.label_num_days.grid(row=3, column=0, sticky=W)
		self.label_PV.grid(row=4, column=0, sticky=W)
		self.label_PV_peak_power.grid(row=5, column=0, sticky=W)
		self.label_battery_capacity.grid(row=6, column=0, sticky=W)
		self.label_battery_power.grid(row=7, column=0, sticky=W)
		self.label_city.grid(row=8, column=0, sticky=W)
		self.label_boilers.grid(row=9, column=0, sticky=W)
		self.label_washers.grid(row=10, column=0, sticky=W)
			
		self.entry_nodes.grid(row=1, column=2, sticky=W+E)
		self.entry_start_day.grid(row=2, column=2, sticky=W+E)
		self.entry_num_days.grid(row=3, column=2, sticky=W+E)
		self.entry_PV.grid(row=4, column=2, sticky=W+E)
		self.entry_battery_capacity.grid(row=6, column=2, sticky=W+E)
		self.entry_battery_power.grid(row=7, column=2, sticky=W+E)
		
		self.city_menu.grid(row=8, column=2, sticky=W+E)	
		self.boilers_menu.grid(row=9, column=2, sticky=W+E)	
		self.washers_menu.grid(row=10, column=2, sticky=W+E)	
		self.run_button.grid(row=11, column=1,sticky=W+E)
		self.aggregated_load_button.grid(row=12, column=0,sticky=W+E)
		self.autoconsumption_button.grid(row=12, column=1,sticky=W+E)
		self.battery_button.grid(row=12, column=2,sticky=W+E)
		self.switches_button.grid(row=13, column=0,sticky=W+E)
		self.boiler_button.grid(row=13, column=1,sticky=W+E)
		self.network_load_button.grid(row=13, column=2,sticky=W+E)
							
	#Function to validate the entries
	def validate(self,new_text,entry_type):
				
		if entry_type=="nodes":
			try:
				self.num_nodes = int(new_text)
				return True
			except ValueError:
				return False
		if entry_type=="start day":
			try:
				self.start_day = int(new_text)
				return True
			except ValueError:
				return False
		if entry_type=="num days":
			try:
				self.num_days = int(new_text)
				return True
			except ValueError:
				return False
		if entry_type=="PV":
			try:
				self.PV_surface = float(new_text)
				if len(new_text)>0:
					#Computes approximate peak power in kW based on a solar radiation of 1000 W/m^2
					self.PV_peak_power.set("Approx. "+str(self.PV_surface*self.PV_efficiency)+" kWpeak")
					self.master.update_idletasks()
				return True
			except ValueError:
				return False
		if entry_type=="battery capacity":
			try:
				self.battery_capacity = float(new_text)
				return True
			except ValueError:
				return False
		if entry_type=="battery power":
			try:
				self.battery_power = float(new_text)
				return True
			except ValueError:
				return False
	
	#Set the choosen city into the variable
	def validate_city(self,choice):
		try:
			self.city.set(choice)
			return True
		except ValueError:
				return False
	
	#Validate washers
	def validate_washers(self,choice):
		try:
			self.smart_washers_label.set(choice)
			if self.smart_washers_label.get()=="Yes":
				self.smart_washers=True
			else:
				self.smart_washers=False
			return True
		except ValueError:
				return False
	
	#Validate boilers
	def validate_boilers(self,choice):
		try:
			self.boilers_label.set(choice)
			if self.boilers_label.get()=="Yes":
				self.simulate_boilers=True
			else:
				self.simulate_boilers=False
			return True
		except ValueError:
				return False
	
	#Function to run the simulation
	def run(self):
		
		self.clean_up()
		self.message.set("STATUS: Preparing weather data")
		self.master.update_idletasks()
		
		# Number of minutes per day
		mins=1440
		
		# Start and End minutes of the simulation
		t_start=self.start_day*mins
		t_end=(self.num_days+self.start_day)*mins
		
		# Load metereological data
		self.T=np.load("Data/Metereological_data/"+self.city.get()+"_Temperature.npy")[t_start:t_end]
		self.R90=np.load("Data/Metereological_data/"+self.city.get()+"_Radiation_90.npy")[t_start:t_end]
		self.R40=np.load("Data/Metereological_data/"+self.city.get()+"_Radiation_40.npy")[t_start:t_end]
		
		self.message.set("STATUS: Running behavsim")
		self.master.update_idletasks()
		
		# Run behavsim kernel
		self.Domestic_appliances, self.Hot_water = run_behavsim(self.num_nodes,self.num_days,self.smart_washers)
		print "BEHAVSIM DONE!!!"
		# Compute aggregated residual load 
		self.Residual_load=(self.Domestic_appliances).sum(axis=1)-self.R40*self.PV_efficiency*self.PV_surface*self.num_nodes
		
		# Creates directory containg results.
		results_path="Results_"+self.city.get()
		if os.path.exists(results_path):
			# Careful: removes existing directory having the same name
			shutil.rmtree(results_path)
			os.makedirs(results_path)
		else:
			os.makedirs(results_path)
		os.chdir(results_path)
		
		# Saves the timeseries used in the simulation 
		self.message.set("STATUS: Storing Time Series")
		self.master.update_idletasks()
		
		np.savetxt("T.dat",self.T,fmt='%.2f',delimiter="\n")
		np.savetxt("R90.dat",self.R90,fmt='%.2f',delimiter="\n")
		np.savetxt("R40.dat",self.R40,fmt='%.2f',delimiter="\n")
		np.savetxt("Residual_load.dat",self.Residual_load,fmt='%.2f',delimiter="\n")
		np.savetxt("House_aggregate.dat",self.Domestic_appliances,fmt='%.2f')
		
		# Checks the on which platform the program is running 
		op_sys = platform.system()
		if op_sys=='Linux':
			# Prefix for executables on Linux Platform
			prefix="./"
		else:
			prefix=""
			
		# Electric Boiler simulation
		if self.simulate_boilers==True:
			np.savetxt("Hot_water.dat",np.transpose(self.Hot_water),fmt='%.2f')
			shutil.copy("../src/Boilers.exe",os.getcwd())
			self.message.set("STATUS: Simulating smart boilers")
			self.master.update_idletasks()
			Input_file_Boilers(self.num_nodes, self.start_day, self.num_days, 1)
			os.system (prefix+"Boilers.exe < Input_Boilers.txt")
			os.remove("Input_Boilers.txt")
			self.message.set("STATUS: Simulating boilers")
			self.master.update_idletasks()
			Input_file_Boilers(self.num_nodes, self.start_day, self.num_days, 0)
			os.system (prefix+"Boilers.exe < Input_Boilers.txt")
			os.remove("Boilers.exe")
			np.savetxt("Residual_load_boilers.dat",self.Residual_load+np.loadtxt("Res_Boiler_Control.dat")[:,-1])
		
		# Start simulation of controlled heat pumps
		shutil.copy("../src/HeatPump.exe",os.getcwd())		
		self.message.set("STATUS: Simulating neighborhood")
		self.master.update_idletasks()
		
		# Input file for c++ simulation 
		Input_file_Heat_Pumps(self.num_nodes, self.start_day, self.num_days, 
		                      self.average_window_surf,self.battery_capacity,
		                      self.battery_power,self.PV_surface,
		                      self.PV_efficiency,self.simulate_boilers)
		# Run c++
		os.system (prefix+"HeatPump.exe < Input_Heat_Pump.txt")
		os.remove("HeatPump.exe")

		self.message.set("STATUS: Simulation completed")
		self.master.update_idletasks()
		os.chdir("../")
		self.simulation_over=True
		
	#Function to free the memory
	def clean_up(self):
		
		#tracker = SummaryTracker()

		gc.collect()
		del self.T
		del self.R90
		del self.R40
		del self.Domestic_appliances
		del self.Residual_load
		del self.Hot_water
		self.T=None
		self.R40=None
		self.R90=None
		self.Domestic_appliances=None
		self.Residual_load=None
		self.Hot_water=None
		
		#tracker.print_diff()
		
	#Function to free the memory on closing
	def on_closing(self):
		self.clean_up()
		self.master.destroy()
		
	#Function to plot the net aggregated load
	def plot_aggregated_load(self):
		if self.simulation_over:
			self.message.set("STATUS: Plotting data")
			self.master.update_idletasks()
			plot_aggregated_load(self.num_nodes,self.start_day,self.num_days,self.T,
			          self.R90,self.R40,self.Residual_load,self.PV_efficiency,
			          self.PV_surface,self.city.get(),self.simulate_boilers)
			self.message.set("STATUS: Done plotting")
			self.master.update_idletasks()
		else:
			print "Simulation data not available"

	#Function to plot the self-consumption and autonomy rates
	def plot_self_consumption(self):
		if self.simulation_over:
			self.message.set("STATUS: Plotting data")
			self.master.update_idletasks()
			plot_self_consumption(self.num_nodes,self.start_day,self.num_days,self.R40,
					  self.Residual_load,self.PV_efficiency,self.PV_surface,
					  self.city.get(),self.simulate_boilers)
			self.message.set("STATUS: Done plotting")
			self.master.update_idletasks()
		else:
			print "Simulation data not available"
	
	#Function to plot the battery usage
	def plot_battery_usage(self):
		if self.simulation_over:
			self.message.set("STATUS: Plotting data")
			self.master.update_idletasks()
			plot_battery_usage(self.num_nodes,self.start_day,self.num_days,
			                   self.Residual_load,self.PV_surface,self.city.get(),
			                   self.simulate_boilers)
			self.message.set("STATUS: Done plotting")
			self.master.update_idletasks()
		else:
			print "Simulation data not available"
	
	
	#Function to plot the network load
	def plot_network_load(self):
		if self.simulation_over:
			self.message.set("STATUS: Plotting data")
			self.master.update_idletasks()
			plot_line_load(self.num_nodes,self.start_day,self.num_days,
			               self.R40,self.Domestic_appliances,self.PV_efficiency,
			               self.PV_surface,self.city.get(),self.simulate_boilers)
			self.message.set("STATUS: Done plotting")
			self.master.update_idletasks()
		else:
			print "Simulation data not available"

	#Function to plot the number of times the HP switches on
	def plot_switch_counts(self):
		if self.simulation_over:
			self.message.set("STATUS: Plotting data")
			self.master.update_idletasks()
			plot_switch_counts(self.city.get())
			self.message.set("STATUS: Done plotting")
			self.master.update_idletasks()
		else:
			print "Simulation data not available"
	
	#Function to plot details about boiler consumption
	def plot_boilers(self):
		if self.simulation_over and self.simulate_boilers:
			self.message.set("STATUS: Plotting data")
			self.master.update_idletasks()
			plot_boilers(self.start_day,self.num_days,self.Hot_water,self.city.get())
			self.message.set("STATUS: Done plotting")
			self.master.update_idletasks()
		else:
			print "Simulation data not available"

# Creates the input file for the Heat Pump c++ executable 
def Input_file_Heat_Pumps(num_houses,starting_day,num_days,window_surf,battery_capacity,battery_power,pv_surface,pv_efficiency,simulate_boilers):
	f=open("Input_Heat_Pump.txt",'w')
	f.write(str(num_houses) +'\n')
	f.write(str(starting_day) +'\n')
	f.write(str(num_days) +'\n')
	f.write("T.dat" +'\n')
	f.write("R90.dat" +'\n')
	f.write("R40.dat" +'\n')
	if simulate_boilers==False:
		f.write("Residual_load.dat" +'\n')
	else:
		f.write("Residual_load_boilers.dat" +'\n')
	f.write(str(window_surf)+'\n')
	f.write(str(battery_capacity)+'\n')
	f.write(str(battery_power)+'\n')
	f.write(str(pv_surface)+'\n')
	f.write(str(pv_efficiency)+'\n')
	f.close()
	
# Creates the input file for the Boilers c++ executable 
def Input_file_Boilers(num_houses,starting_day,num_days,algorithm):
	f=open("Input_Boilers.txt",'w')
	f.write(str(num_houses) +'\n')
	f.write(str(starting_day) +'\n')
	f.write(str(num_days) +'\n')
	f.write(str(algorithm) +'\n')
	f.write("Hot_water.dat" +'\n')
	f.write("T.dat" +'\n')
	f.write("R90.dat" +'\n')
	f.write("R40.dat" +'\n')
	f.close()

def main():
	
	root = Tk()
	my_gui = Simulator(root)
	root.mainloop()
	return 0

if __name__ == '__main__':
	main()
