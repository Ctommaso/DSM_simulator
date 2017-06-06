import numpy as np
import pandas as pd
import os
import sys

def prepare_load_flow_data(num_nodes,start_day,num_days,R40,Domestic_appliances,pv_efficiency,pv_surf,city,simulate_boilers,*standalone):

	### GATHER DATA ###
	num_days=num_days-1
	
	res_fn_smart_B="Results_"+city+"/Res_HP_Control_B.dat"
	res_fn_smart="Results_"+city+"/Res_HP_Control.dat"
	res_fn="Results_"+city+"/Res_HP_Thermostat.dat"
	
	res_smart_B = pd.read_csv(res_fn_smart_B,delim_whitespace=True,header=None,index_col=False)
	res_smart_B = res_smart_B.values
	res_smart = pd.read_csv(res_fn_smart,delim_whitespace=True,header=None,index_col=False)
	res_smart = res_smart.values
	res_thermostat = pd.read_csv(res_fn,delim_whitespace=True,header=None,index_col=False)
	res_thermostat = res_thermostat.values
	
	if simulate_boilers==True:
		res_boilers_smart = pd.read_csv("Results_"+city+"/Res_Boiler_Control.dat",delim_whitespace=True,header=None,index_col=False)
		res_boilers_smart = (res_boilers_smart.values)[0:24*60*num_days,num_nodes+1:2*num_nodes+1]
		res_boilers=pd.read_csv("Results_"+city+"/Res_Boiler_Thermostat.dat",delim_whitespace=True,header=None,index_col=False)
		res_boilers = (res_boilers.values)[0:24*60*num_days,num_nodes+1:2*num_nodes+1]
	
	time=res_smart[:,0]
	power_hp_smart_B=res_smart_B[:,1:num_nodes+1]
	power_hp_smart=res_smart[:,1:num_nodes+1]
	power_hp_thermostat=res_thermostat[:,1:num_nodes+1]

	R40=R40[0:24*60*num_days]
	power_pv=R40*pv_efficiency*pv_surf
	power_pv=np.tile(power_pv,(num_nodes,1))
	power_pv=np.transpose(power_pv)
	
	Domestic_appliances=Domestic_appliances[0:24*60*num_days,:]

	if simulate_boilers==True:
		Load_T=(power_hp_thermostat + res_boilers + Domestic_appliances - power_pv)#[W] load thermostat
		Load_C=(power_hp_smart + res_boilers_smart + Domestic_appliances - power_pv)#[W] load control
		Load_C_B=(power_hp_smart_B + res_boilers_smart + Domestic_appliances - power_pv)#[W] load control + batteries
	else:
		Load_T=(power_hp_thermostat+Domestic_appliances-power_pv)#[W] load thermostat
		Load_C=(power_hp_smart+Domestic_appliances-power_pv)#[W] load control
		Load_C_B=(power_hp_smart_B + Domestic_appliances - power_pv)#[W] load control + batteries
	
	np.save("Load_T", Load_T[24*60:24*60*(num_days),:])
	np.save("Load_C", Load_C[24*60:24*60*(num_days),:])
	np.save("Load_C_B", Load_C_B[24*60:24*60*(num_days),:])
	
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
	Domestic_appliances=np.loadtxt(dir_name+"House_aggregate.dat")

	if os.path.exists(dir_name+'Input_Boilers.txt'):
		simulate_boilers=True
	else:
		simulate_boilers=False
	standalone=True
	
	prepare_load_flow_data(num_houses,starting_day,num_days,R40,Domestic_appliances,pv_efficiency,pv_surf,city,simulate_boilers,standalone)

if __name__ == '__main__':
	main()	
