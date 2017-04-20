import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import sys
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

### Function plots the aggregated load data
def plot_aggregated_load(num_houses,starting_day,num_days,T,R90,R40,Residual_load,pv_efficiency,pv_surf,city,simulate_boilers,*standalone): 
	
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

	T=T[0:24*60*num_days]
	R90=R90[0:24*60*num_days]
	R40=R40[0:24*60*num_days]
	Residual_load=Residual_load[0:24*60*num_days]
	power_pv=R40*pv_efficiency*pv_surf*num_houses
	
	### PLOTTING PART ###
	fig, (ax1,ax2,ax3,ax4) = plt.subplots(4, sharex=True)
	fig.subplots_adjust(right=0.93, left=0.07,top=0.95,bottom=0.08,hspace=0.15)

	ax1.set_title(city+r" $S_\textrm{pv} =$"+str(pv_surf)+r"$[m^2]$",fontsize=25)	

	ax2bis=ax2.twinx()
	
	p1=ax1.plot(time, 1e-06*Residual_load, "k-", label=r"Residual load",linewidth=1.5)# Residual Load in [MW],
	if simulate_boilers==True:
		p1bis=ax1.plot(time, 1e-06*(Residual_load+res_boilers_smart), "r-", label=r"Residual load + Smart Boilers",linewidth=1.5)# Residual Load + Boilers in [MW],
		p1tris=ax1.plot(time, 1e-06*(res_boilers_smart), "k:", label=r"Smart Boilers")# Boilers in [MW],
	
	p2=ax2.plot(time, T, "-",color=[1,0.5,0], label=r"$T_{\rm ext}$",linewidth=1.5)
	p2bis=ax2bis.plot(time, 1e-03*R90, "b-", label=r"$p_{\rm  rad}$",linewidth=1.5)#Radiation power in [kW]
	p2tris=ax2bis.plot(time, 1e-03*R40, "g:", label=r"$p_{\rm  rad_{40}}$",linewidth=1.5)#Radiation power in [kW]
	
	p3=ax3.plot(time,1e-06*power_hp_thermostat, "g-", label=r"No Ctrl",linewidth=1.5)# Pelectric in [MW], COP=3
	p3bis=ax3.plot(time,1e-06*power_hp_smart, "r-", label=r"Ctrl",linewidth=1.5)# Pelectric in [MW], COP=3
	
	if simulate_boilers==True:
		p4=ax4.plot(time, 1e-06*(power_hp_thermostat+Residual_load+res_boilers), "g-", label=r"No Ctrl",linewidth=1.5)# Pelectric in [MW], COP=3
		p4bis=ax4.plot(time, 1e-06*(power_hp_smart+Residual_load+res_boilers_smart), "r-", label=r"Ctrl",linewidth=1.5)# Pelectric in [MW], COP=3
		p4tris=ax4.plot(time, 1e-06*(power_hp_smart_B+Residual_load+res_boilers_smart), "b-", label=r"Ctrl + Batt",linewidth=1.5)# Pelectric in [MW], COP=3
	else:
		p4=ax4.plot(time, 1e-06*(power_hp_thermostat+Residual_load), "g-", label=r"No Ctrl",linewidth=1.5)# Pelectric in [MW], COP=3
		p4bis=ax4.plot(time, 1e-06*(power_hp_smart+Residual_load), "r-", label=r"Ctrl",linewidth=1.5)# Pelectric in [MW], COP=3
		p4tris=ax4.plot(time, 1e-06*(power_hp_smart_B+Residual_load), "b-", label=r"Ctrl + Batt",linewidth=1.5)# Pelectric in [MW], COP=3
	
	positions=[n*24 for n in range(starting_day,starting_day+num_days+1)]
	if num_days>20:
		labels=[n if n%5==0 else "" for n in range(starting_day,starting_day+num_days+1)]	
	else:
		labels=[n for n in range(starting_day,starting_day+num_days+1)]	
	ax4.set_xticklabels(labels)
	
	ax4.set_xlabel(r"Day", fontsize=22)
	ax4.set_ylabel(r"$P_{\rm el}$"+" "+r"$[{\rm MW}]$", fontsize=22)
	ax3.set_ylabel(r"$P_{\rm el}$"+" "+r"$[{\rm MW}]$", fontsize=22)
	ax2.set_ylabel(r"$T_{\rm ext}$"+" "+r"$[^\circ {\rm C}]$", fontsize=22)
	ax2bis.set_ylabel(r"$p_{\rm rad}$"+" "+r"$[{\rm kW/m}^2]$", fontsize=22)
	ax1.set_ylabel(r"Residual load"+" "+r"$[{\rm MW}]$", fontsize=22)
	
	axes=[ax1,ax2,ax3,ax4]
	panels=[r"a)",r"b)",r"c)",r"d)"]
	for i in range(0,len(axes)):
		axes[i].set_xlim(24*starting_day, 24*(starting_day+num_days)),
		axes[i].annotate(panels[i], xy=(0.002,0.85),xycoords="axes fraction",fontsize=22)
		axes[i].xaxis.grid()
		axes[i].yaxis.set_label_coords(-0.05, 0.5)
		axes[i].tick_params(axis='both', which='major', labelsize=22)
		axes[i].xaxis.set_ticks(positions)	
	
	ax2bis.yaxis.set_label_coords(1.05, 0.5)
	ax2bis.tick_params(axis='both', which='major', labelsize=22)
	ax2bis.set_xlim(24*starting_day, 24*(starting_day+num_days))
		
	P1=p1
	if simulate_boilers==True:
		P1+=p1bis+p1tris
	P2=p2+p2bis+p2tris
	P3=p3+p3bis
	P4=p4+p4bis+p4tris
	for p in [P1,P2,P3,P4]:
		labs=[l.get_label() for l in p]
		axes[[P1,P2,P3,P4].index(p)].legend(p,labs,fancybox=False)

	fig.set_size_inches(18.5, 12.5, forward=True)
	plt.savefig("Results_"+city+"/Aggregated_load_PV="+str(pv_surf)+".pdf",format='pdf',dvi=700)
	plt.savefig("Results_"+city+"/Aggregated_load_PV="+str(pv_surf)+".eps",format='eps',dvi=700)
	
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
	T=np.loadtxt(dir_name+'T.dat')
	R40=np.loadtxt(dir_name+'R40.dat')
	R90=np.loadtxt(dir_name+'R90.dat')	
	Residual_load=np.loadtxt(dir_name+'Residual_load.dat')
	
	if os.path.exists(dir_name+'Input_Boilers.txt'):
		simulate_boilers=True
	else:
		simulate_boilers=False
	
	standalone=True
	plot_aggregated_load(num_houses,starting_day,num_days,T,R90,R40,Residual_load,pv_efficiency,pv_surf,city,simulate_boilers,standalone)
	
if __name__ == '__main__':
	main()
