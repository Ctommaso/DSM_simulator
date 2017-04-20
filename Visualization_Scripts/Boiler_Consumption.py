import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

### Function to plot the electric consumption of all boilers 
def plot_boilers(start_day,num_days,hot_water,city,*standalone):
	
	### Load the results of the boiler simulation
	res_fn_smart="Results_"+city+"/Res_Boiler_Control.dat"
	res_fn="Results_"+city+"/Res_Boiler_Thermostat.dat"
	
	res_smart=pd.read_csv(res_fn_smart,delim_whitespace=True,header=None,index_col=False)
	res_smart = (res_smart.values)[:,-1]
	res_thermostat=pd.read_csv(res_fn,delim_whitespace=True,header=None,index_col=False)
	res_thermostat = (res_thermostat.values)[:,-1]
	
	time=np.array([start_day+n/1440.0 for n in range(0,60*24*num_days)])
	
	### Plotting part
	fig, (ax0,ax1) = plt.subplots(2, sharex=True)
	fig.subplots_adjust(right=0.93, left=0.07,top=0.9,bottom=0.1,wspace=0.3)
	
	ax0bis=ax0.twinx()
	ax1bis=ax1.twinx()
	
	if hot_water.ndim==1:
		totWater_cons=hot_water
	else:
		totWater_cons=np.sum(hot_water,axis=1)
	
	ax0.set_title("Thermostatically controlled Boilers", fontsize=30)
	ax1.set_title("Smart Boilers", fontsize=30)
	p0bis=ax0bis.plot(time,totWater_cons,"b",label=r"Total Water cons")	
	p1bis=ax1bis.plot(time,totWater_cons,"b",label=r"Total Water cons")
	
	p0=ax0.plot(time,res_thermostat*1e-03,"g",linewidth=2.0,label=r"Heating power")
	p1=ax1.plot(time,res_smart*1e-03,"g",linewidth=2.0,label=r"Heating power")
	
	P0=p0+p0bis
	P1=p1+p1bis
	axes=[ax0,ax1]
	for p in [P0,P1]:
		labs=[l.get_label() for l in p]
		axes[[P0,P1].index(p)].legend(p,labs,fancybox=False)
	
	#Cosmetics
	ax1.set_xlabel(r"Day", fontsize=25)
	
	ax0.set_ylabel(r"$P_{\rm el}^{\rm tot}$"+" "+r"$[{\rm kW}]$", fontsize=25)
	ax1.set_ylabel(r"$P_{\rm el}^{\rm tot}$"+" "+r"$[{\rm kW}]$", fontsize=25)

	ax0bis.set_ylabel(r"Hot water flow"+" "+r"$[{\rm L/min}]$", fontsize=25)
	ax1bis.set_ylabel(r"Hot water flow"+" "+r"$[{\rm L/min}]$", fontsize=25)
	
	ax=[ax0,ax1,ax0bis,ax1bis]
	ticks=[start_day+n for n in range(0,num_days)]
	minor_ticks=[start_day+n+0.5 for n in range(0,num_days)]
	
	if num_days>20:
		labels=[n if n%5==0 else "" for n in range(start_day,start_day+num_days+1)]	
	else:
		labels=[n for n in range(start_day,start_day+num_days+1)]	
	
	for i in range(0,len(ax)):
		ax[i].set_xlim(start_day, start_day+num_days)
		ax[i].tick_params(axis='both', which='major', labelsize=23)
		ax[i].set_xticks(ticks)
		ax[i].set_xticklabels(labels)
		ax[i].set_xticks(minor_ticks, minor = True)
		ax[i].tick_params(axis='both', which='major', labelsize=23)
		ax[i].xaxis.grid(which='major', alpha=1)
		ax[i].xaxis.grid(which='minor', alpha=0.5)
	
	fig.set_size_inches(17, 12, forward=True)
	plt.savefig("Results_"+city+"/Boiler_consumption.pdf",format='pdf',dvi=700)
	
	if not standalone:
		plt.ion()
	plt.show()
	
############################## MAIN ###############################################
def main():
	
	city=sys.argv[1]
	dir_name='Results_'+city+'/'
	standalone=True
	if os.path.exists(dir_name+'Input_Boilers.txt'):
		f = open(dir_name+'Input_Boilers.txt', 'r')
		data = f.readlines()
		f.close()
		start_day =int(data[1])
		num_days =int(data[2])
		
		hot_water=pd.read_csv(dir_name+"Hot_water.dat",delim_whitespace=True,header=None,index_col=False)
		hot_water = np.transpose(hot_water.values)
		plot_boilers(start_day,num_days,hot_water,city,standalone)
	
if __name__ == '__main__':
    main()
