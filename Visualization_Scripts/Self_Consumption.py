import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import sys
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

### Compute daily self-consumption and autonomy
def daily_self_cons(Net_Load, power_pv, num_houses, num_days):
	
	self_cons=[] # ratio of locally consumed PV / total PV production
	autonomy=[] # ratio of locally consumed PV / total consumption
	Load=np.maximum(Net_Load+power_pv,np.zeros(len(Net_Load))) # Extract only the consumption 
	for d in range(0,num_days): #daily computation
		consumedPV=(np.minimum(Load[d*24*60:(d+1)*24*60],power_pv[d*24*60:(d+1)*24*60])).sum()
		totPV=power_pv[d*24*60:(d+1)*24*60].sum()
		totLoad=(Load[d*24*60:(d+1)*24*60]).sum()
		self_cons.append(consumedPV/totPV)
		autonomy.append(consumedPV/totLoad)
	return [np.array(self_cons),np.array(autonomy)]

### Compute average self-consumption and autonomy over the whole simulation period
def average_self_cons(Net_Load, power_pv, num_houses, num_days):
	
	Load=np.maximum(Net_Load+power_pv,np.zeros(len(Net_Load)))# Extract only the consumption 
	consumedPV=(np.minimum(Load,power_pv)).sum()
	totPV=power_pv.sum()
	totLoad=Load.sum()
	return consumedPV/totPV , consumedPV/totLoad

### Plot self consumption and autonomy results
def plot_self_consumption(num_houses,starting_day,num_days,R40,Residual_load,pv_efficiency,pv_surf,city,simulate_boilers,*standalone): 

	### GATHERING DATA ###
	num_days=num_days-1
	
	res_fn_smart_B="Results_"+city+"/Res_HP_Control_B.dat"
	res_fn_smart="Results_"+city+"/Res_HP_Control.dat"
	res_fn="Results_"+city+"/Res_HP_Thermostat.dat"

	res_smart_B=pd.read_csv(res_fn_smart_B,delim_whitespace=True,header=None,index_col=False)
	res_smart_B = res_smart_B.values
	res_smart=pd.read_csv(res_fn_smart,delim_whitespace=True,header=None,index_col=False)
	res_smart = res_smart.values
	res_thermostat=pd.read_csv(res_fn,delim_whitespace=True,header=None,index_col=False)
	res_thermostat = res_thermostat.values
	
	if simulate_boilers==True:
		res_boilers_smart=pd.read_csv("Results_"+city+"/Res_Boiler_Control.dat",delim_whitespace=True,header=None,index_col=False)
		res_boilers_smart = (res_boilers_smart.values)[0:24*60*num_days,-1]
		res_boilers=pd.read_csv("Results_"+city+"/Res_Boiler_Thermostat.dat",delim_whitespace=True,header=None,index_col=False)
		res_boilers = (res_boilers.values)[0:24*60*num_days,-1]
	
	time=res_smart[:,0]
	power_hp_smart_B=res_smart_B[:,1:num_houses+1].sum(axis=1)
	power_hp_smart=res_smart[:,1:num_houses+1].sum(axis=1)
	power_hp_thermostat=res_thermostat[:,1:num_houses+1].sum(axis=1)

	R40=R40[0:24*60*num_days]
	Residual_load=Residual_load[0:24*60*num_days]
	power_pv=R40*pv_efficiency*pv_surf*num_houses
	
	if simulate_boilers==True:
		Aggregated_load_control_B = power_hp_smart_B+Residual_load+res_boilers_smart
		Aggregated_load_control = power_hp_smart+Residual_load+res_boilers_smart
		Aggregated_load_thermostat = power_hp_thermostat+Residual_load+res_boilers
	else:
		Aggregated_load_control_B = power_hp_smart_B+Residual_load
		Aggregated_load_control = power_hp_smart+Residual_load
		Aggregated_load_thermostat = power_hp_thermostat+Residual_load
	
	#Compute daily self-consumption and autonomy
	self_cons_control_B , autonomy_control_B = daily_self_cons(Aggregated_load_control_B, power_pv, num_houses, num_days)
	self_cons_control , autonomy_control = daily_self_cons(Aggregated_load_control, power_pv, num_houses, num_days)
	self_cons_thermostat , autonomy_thermostat = daily_self_cons(Aggregated_load_thermostat, power_pv, num_houses, num_days)
	
	#Compute self-consumption and autonomy over the whole simulation period
	average_self_cons_control_B , average_autonomy_control_B = average_self_cons(Aggregated_load_control_B, power_pv, num_houses, num_days)
	average_self_cons_control , average_autonomy_control = average_self_cons(Aggregated_load_control, power_pv, num_houses, num_days)
	average_self_cons_thermostat , average_autonomy_thermostat = average_self_cons(Aggregated_load_thermostat, power_pv, num_houses, num_days)
	
	### PLOTTING PART ###
	fig, (ax1,ax2) = plt.subplots(2, sharex=False)
	fig.subplots_adjust(right=0.97, left=0.08,top=0.95,bottom=0.08,hspace=0.20)

	ax1.set_title(city+r" $S_\textrm{pv} =$"+str(pv_surf)+r"$[m^2]$",fontsize=25)	
	
	p1=ax1.plot(np.array([0.5+starting_day+n for n in range(0,num_days)]), self_cons_thermostat, "g-o", label=r"Thermostat",linewidth=1.5)
	p1bis=ax1.plot(np.array([0.5+starting_day+n for n in range(0,num_days)]), self_cons_control, "r-o", label=r"Control",linewidth=1.5)
	p1tris=ax1.plot(np.array([0.5+starting_day+n for n in range(0,num_days)]), self_cons_control_B, "b-o", label=r"Control + Batt",linewidth=1.5)
	
	p2=ax2.plot(np.array([0.5+starting_day+n for n in range(0,num_days)]), autonomy_thermostat, "g-o", label=r"Thermostat",linewidth=1.5)
	p2bis=ax2.plot(np.array([0.5+starting_day+n for n in range(0,num_days)]), autonomy_control, "r-o", label=r"Control",linewidth=1.5)
	p2tris=ax2.plot(np.array([0.5+starting_day+n for n in range(0,num_days)]), autonomy_control_B, "b-o", label=r"Control + Batt",linewidth=1.5)
	
	positions=[starting_day+n for n in range(0,num_days+1)]
	if num_days>20:
		labels=[n if n%5==0 else "" for n in range(starting_day,starting_day+num_days+1)]	
	else:
		labels=[n for n in range(starting_day,starting_day+num_days+1)]	
	
	ax1.set_xticklabels(labels)
	ax2.set_xticklabels(labels)
	
	ax1.set_xlabel(r"Day", fontsize=30)
	ax2.set_xlabel(r"Day", fontsize=30)
	ax1.set_ylabel(r"Self consumption rate", fontsize=30)
	ax2.set_ylabel(r"Autonomy rate", fontsize=30)
	
	axes=[ax1,ax2]
	panels=[r"a)",r"b)"]
	for i in range(0,len(axes)):
		axes[i].set_xlim(starting_day, (starting_day+num_days)),
		axes[i].annotate(panels[i], xy=(0.005,0.94),xycoords="axes fraction",fontsize=25)
		axes[i].xaxis.grid()
		axes[i].yaxis.set_label_coords(-0.05, 0.5)
		axes[i].tick_params(axis='both', which='major', labelsize=22)
		axes[i].xaxis.set_ticks(positions)	
	
	ax1.annotate("Total self-cons rate ", xy=(0.005,0.2),xycoords="axes fraction",fontsize=15)
	ax1.annotate("Thermostat "+str(np.round(average_self_cons_thermostat,3)), xy=(0.005,0.15),xycoords="axes fraction",fontsize=15)
	ax1.annotate("Control "+str(np.round(average_self_cons_control,3)), xy=(0.005,0.1),xycoords="axes fraction",fontsize=15)
	ax1.annotate("Control + Battery "+str(np.round(average_self_cons_control_B,3)), xy=(0.005,0.05),xycoords="axes fraction",fontsize=15)
	
	ax2.annotate("Total autonomy rate ", xy=(0.005,0.2),xycoords="axes fraction",fontsize=15)
	ax2.annotate("Thermostat "+str(np.round(average_autonomy_thermostat,3)), xy=(0.005,0.15),xycoords="axes fraction",fontsize=15)
	ax2.annotate("Control "+str(np.round(average_autonomy_control,3)), xy=(0.005,0.1),xycoords="axes fraction",fontsize=15)
	ax2.annotate("Control + Battery "+str(np.round(average_autonomy_control_B,3)), xy=(0.005,0.05),xycoords="axes fraction",fontsize=15)
	
	P1=p1+p1bis+p1tris
	P2=p2+p2bis+p2tris
	for p in [P1,P2]:
		labs=[l.get_label() for l in p]
		axes[[P1,P2].index(p)].legend(p,labs,fancybox=False)

	fig.set_size_inches(18.5, 12.5, forward=True)
	plt.savefig("Results_"+city+"/Self_consumption_PV="+str(pv_surf)+".pdf",format='pdf',dvi=700)
	
	if not standalone:
		plt.ion()
	plt.show()

def main():
	
	city=sys.argv[1]
	dir_name='Results_'+city+'/'
	f = open(dir_name+'Input_Heat_Pump.txt', 'r')
	data = f.readlines()
	f.close()
	num_houses =int(data[0])
	starting_day =int(data[1])
	num_days =int(data[2])
	pv_surf = float(data[11])
	pv_efficiency = float(data[12])
	R40=np.loadtxt(dir_name+'R40.dat')
	Residual_load=np.loadtxt(dir_name+'Residual_load.dat')
	
	if os.path.exists(dir_name+'Input_Boilers.txt'):
		simulate_boilers=True
	else:
		simulate_boilers=False
	
	standalone=True
	plot_self_consumption(num_houses,starting_day,num_days,R40,Residual_load,pv_efficiency,pv_surf,city,simulate_boilers,standalone)
	
if __name__ == '__main__':
	main()
