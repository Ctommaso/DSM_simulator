#include "Time_integration.h"

//**********************************************************************
// Euler time integration step T_i+1 = T_i + Delta_t * (dT_i/dt)
void Euler(Neighborhood & n, int starting_day, int step, double deltat, double Ei, bool smart, const Weather & w, double COP, bool battery)
{
	//Evolution of the House temperatures
	(*n.getT())=(*n.getT())+deltat*rhs((*n.getT()),(*n.getHouses()),step,w); //EULER

	//Evolution of the Battery state of charge
	if(battery)
	{
		double new_SoC(0);
		for(unsigned int j(0); j < (*n.getB()).size(); j++)
		{	
			new_SoC = (*n.getB())[j].get_SoC() + deltat*(*n.getB())[j].get_power()*(*n.getB())[j].get_state()/(*n.getB())[j].get_capacity();
			(*n.getB())[j].set_SoC(new_SoC);
		}
	}

	if(smart){
		update_hp_switch(n,Ei,starting_day*24+step*deltat,COP,battery);// updates the heat pump switches:controlled
	}else{
		update_hp_switch_Thermostat(n,starting_day*24+step*deltat);// updates the heat pump switches:thermostat
	}
	
	// Update the Neighborhood's total consumption after switches have been changed
	n.ComputePtot_HP();// update the total thermal power consumption of HP
	n.ComputePtot_Batteries();// update the total electric power consumption of Batteries
}

//*****************************************************************************
// Evaluation of dT/dt (thermal power equation for buildings)
Array rhs(const Array & T, const vector< House > & houses, int step, const Weather & w) 
{
	int hp_num(T.getSize());
	double transmission_windows(0.6); //Transmission coefficient for the windows extrated from Bonvin and Mayor
	
	vector<double> sol(hp_num,0.0);

	for(int j=0;j<hp_num;j++) //computes the right hand side for the different heat pumps indexed by j
	{
		double hp_contrib(0.0);
		double radiation_contrib(transmission_windows*w.get_Rad(step)*houses[j].get_Window_Surf());
		if(!houses[j].Blinds_up())
		{
			radiation_contrib=radiation_contrib*0.2; // take in only 20 % of radiation if blinds are down
		}
		if(houses[j].HP_on())
		{
			hp_contrib=houses[j].get_HP_Coeff();
		}
		sol[j]=(houses[j].get_Th_Cond()*(w.get_Text(step)-T.getComposante(j)) + hp_contrib + radiation_contrib)/houses[j].get_Th_Capacity();
	}

	Array Sol(hp_num,sol);
	return Sol;
}
