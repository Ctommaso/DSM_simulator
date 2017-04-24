#include "Boiler.h"

// Public Methods
Boiler::Boiler(double VOLUME,double POWER, bool INTERRUPTEUR, double REF_T, double CONFORT_INTERVAL, double T_START, double TCOLD, double THERMAL_COND)//Constructeur:
{
	volume=VOLUME;
	thermal_capacity=1.1625; //Thermal capacity of liquid water 4185[J/Kg°K]=1.1625[Wh/Kg°K]=[Wh/(litre°K)]
	thermal_cond=THERMAL_COND; //Thermal conductivity for thermal losses with the exterior of the boiler
	power=POWER;//Power of the boiler [W]
	Switch=INTERRUPTEUR;
	T0=REF_T;
	confort_interval=CONFORT_INTERVAL;
	Tcold=TCOLD;
	switch_counter=0;
	switch_time=0;
	T=T_START;

}

// Function to change the state of the boiler, it also updates the switch counter 
void Boiler::setSwitch(bool a) 
{
	if(Switch==false && a) //the boiler was tuerned on, switch counter is updated
	{
		switch_counter+=1;
	}
	Switch=a; //change l'etat du boiler
}

// This function returns the istantaneous consumption of the boiler depending on
// wether it is on or off 
double Boiler::Heating_power()
{
	if(Switch==true)
	{
		return power;
	}else
	{
		return 0.0;
	}
}

// This function sets the switching time of the boiler given a probability distribution
void Boiler::set_switch_time(double prob, Array Cumulative_Prob_dist)
{
	int i(0);
	while(prob > Cumulative_Prob_dist.getComposante(i))
	{
		i++;
	}
	switch_time=i;
	//cout<<"prob"<<prob<<" switch_time"<<switch_time<<endl;
}
