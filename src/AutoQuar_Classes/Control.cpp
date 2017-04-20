#include "Control.h"

//Global variables for defining summer time
double SUMMER_START = 172*24.0;  //Beginning of summer 21 june in [h]
double SUMMER_END = 264*24.0; //End of summer 21 september [h]

//**********************************************************************
// Estimation of the thermal energy need of the neighborhood based on the weather 
// forecast for over a given horizon
std::pair<double, double> Estimate_Etot(Neighborhood & n,const Weather & w, double time, int step, int horizon)
{
	std::pair<double, double> Thermal_energy_needs;
	
	if(time < SUMMER_START || time > SUMMER_END) // Estimate thermal energy need in the cold period
	{
		double Tav(0.0),Etot(0.0),RadAv(0.0),deltaE(0.0),transmission_coeff(0.6);
		for(int i(0);i<horizon;i++)
		{
			Tav+=w.get_Text(step+i);
			RadAv+=w.get_Rad(step+i);
		}
		Tav=Tav/(horizon);
		RadAv=RadAv/(horizon);
		
		for(int i(0);i<n.getNumHouses();i++)
		{
			deltaE+=(*n.getHouses())[i].get_Th_Capacity()*(-(*n.getT()).getComposante(i)+(*n.getHouses())[i].get_Tref()); 
			Etot+=horizon*(-(*n.getHouses())[i].get_Th_Cond()*(Tav-(*n.getHouses())[i].get_Tref())-(*n.getHouses())[i].get_Window_Surf()*RadAv*transmission_coeff);
		}
		Thermal_energy_needs = std::make_pair(Etot,deltaE*60);// multiplied by 60 for units matching
	}else // summer time
	{
		Thermal_energy_needs = std::make_pair(0,0);// no thermal energy need in the summer time
	}
	return Thermal_energy_needs;
}
//**********************************************************************
// Cumputation of the optimal instantaneous consumption according to the 
// Lagrangian minimization
double Opt_consumption(double E_estimated, int step, int horizon, const Array & Residual_load, double COP)
{
	double sum(0);
	for(int i(0); i<horizon; i++)
	{
		sum+=Residual_load.getComposante(i+step);
	}
	//For explanation of COP, see notes!!!
	return (sum+E_estimated/COP)/horizon-Residual_load.getComposante(step);	
}

//**********************************************************************
// Thermostatic regulation of Heat pumps
// They are turned on (resp. off) if T<Tref+Delta (resp. T>Tref+Delta)
void update_hp_switch_Thermostat(Neighborhood & n, double time)
{
	double T(0),Tref(0),Delta(0);
	std::random_device rd1;
	std::mt19937 gen1(rd1());
	std::uniform_real_distribution<> dis1(0.5,1);
	if(time < SUMMER_START || time > SUMMER_END)
	{
		for(int i(0); i < n.getNumHouses(); i++)
		{
			bool switch_old((*n.getHouses())[i].HP_on());
			Delta=(*n.getHouses())[i].get_ConfortInterval();
			Tref=(*n.getHouses())[i].get_Tref();
			T=(*n.getT()).getComposante(i);
			if(T<(Tref-Delta))
			{
				(*n.getHouses())[i].setSwitch(true); // turns on the heat pump
			}
			if(T>Tref+Delta)
			{
				(*n.getHouses())[i].setSwitch(false); // turns off the heat pump
			}
			//blinds
			//if(T>Tref+Delta*dis1(gen1))
			if(T>Tref+Delta*2.0/3.0)
			{
				(*n.getHouses())[i].setBlinds(false); // closes the blinds
			}
			if(T<Tref)
			{
				(*n.getHouses())[i].setBlinds(true); // opens the blinds
			}
			
			if(switch_old==false && (*n.getHouses())[i].HP_on()) //il y a eu allumage
			{
				n.UpdateSwitchCounter(i);
			}
		}
	}else{//During the summer all heat pumps are off
		for(int i(0); i < n.getNumHouses(); i++)
		{
			(*n.getHouses())[i].setSwitch(false);
		}
	}
}

//**********************************************************************
// Smart regulation performed by the central controller
void update_hp_switch(Neighborhood & n, double Ei, double time, double COP, bool battery)
{
	double T(0),Tref(0),Delta(0),SoC(0);
	std::random_device rd1;
	std::mt19937 gen1(rd1());
	std::uniform_real_distribution<> dis1(0.5,1);
	
	// Temporary electric consumption of HP and Batteries
	double Ptemp(0.0);

	// Priority queues to sort the Houses to make:
	// -HP consume more: Having the coldest house at the top of the queue.
	// -HP consume less: Having the hottest house at the top of the queue.
	std::priority_queue< std::pair<double, int>, vector< std::pair<double,int>>, GreaterOnTop > On_Pumps;
	std::priority_queue< std::pair<double, int>, vector< std::pair<double,int>>, LowestOnTop > Off_Pumps;
	
	// Priority queues to sort batteries available for:
	// -Discharge: Having the largest state of charge at the top of the queue.
	// -Charging: Having the lowest state of charge at the top of the queue.
	std::priority_queue< std::pair<double, int>, vector< std::pair<double,int>>, GreaterOnTop > Available_to_discharge;
	std::priority_queue< std::pair<double, int>, vector< std::pair<double,int>>, LowestOnTop > Available_to_charge;
	
	// needed to keep track of the change in HP status
	vector <bool> switch_old(n.getNumHouses(),false);
	 
	for (int i(0); i < n.getNumHouses(); i++)
	{
		if(time < SUMMER_START || time > SUMMER_END)
		{
			switch_old[i]=(*n.getHouses())[i].HP_on();
			Delta=(*n.getHouses())[i].get_ConfortInterval();
			Tref=(*n.getHouses())[i].get_Tref();
			T=(*n.getT()).getComposante(i);

			// Modifiy the switches such that the new house temperatures remain in the comfort interval
			if(T<(Tref-Delta))
			{
				(*n.getHouses())[i].setSwitch(true); // turns on the heat pump
			}else if(T>(Tref+Delta))
			{
				(*n.getHouses())[i].setSwitch(false); // turns off the heat pump
			}

			// Blinds
			//if(T>Tref+Delta*dis1(gen1))
			if(T>Tref+Delta*2.0/3.0)
			{
				(*n.getHouses())[i].setBlinds(false); // closes the blinds
			}
			if(T<Tref)
			{
				(*n.getHouses())[i].setBlinds(true); // opens the blinds
			}
			
			// After having modified the HP switches to maintain temperatures within comfort limits
			// we determine the electric consumption of HP that are on.
			if((*n.getHouses())[i].HP_on())
			{
				Ptemp+=(*n.getHouses())[i].get_HP_Coeff()/COP;
			}

			// Priority signal to sort houses according to the temperature measured relative
			// to the comfort interval
			double signal((T-(Tref-Delta))/(2*Delta));
			// HP flexibility pools
			if((*n.getHouses())[i].HP_on())
			{
				On_Pumps.push(std::pair<double, int>(signal, i));//list of ON PUMPS sorted by decreasing temperatures
			}else if(!(*n.getHouses())[i].HP_on())
			{
				Off_Pumps.push(std::pair<double, int>(signal, i));//list of OFF PUMPS sorted by increasing temperatures
			}
		}else{ //During the summer all heat pumps are off
			for(int i(0); i < n.getNumHouses(); i++)
			{
				switch_old[i]=(*n.getHouses())[i].HP_on();
				(*n.getHouses())[i].setSwitch(false);
			}
		}
		
		if(battery)
		{
			SoC=(*n.getB())[i].get_SoC();
			// If the SoC of the battery exceeds 1 or falls below 0, the battery state is changed to zero.
			if(SoC<0 || SoC>1 )
			{
				(*n.getB())[i].set_state(0); //battery stops charging or discharging
			}
			// After having modified the Battery states to maintain 0<SoC<1 
			// we incorporate the consumption of batteries that are either charging or discharging.
			if((*n.getB())[i].get_state()==-1 || (*n.getB())[i].get_state()==1)
			{
				Ptemp+=(*n.getB())[i].get_state() * (*n.getB())[i].get_power();
			}
			// Battery flexibility pools
			if((*n.getB())[i].get_state()==1 || (*n.getB())[i].get_state()==0) //Available to discharge
			{
				// list of batteries that are not already discharging sorted by decreasing SoC
				Available_to_discharge.push(std::pair<double, int>((*n.getB())[i].get_SoC(), i));
			}
			if((*n.getB())[i].get_state()==-1 || (*n.getB())[i].get_state()==0) //Available to charge		
			{
				// list of batteries that are not already charging sorted by increasing SoC
				Available_to_charge.push(std::pair<double, int>((*n.getB())[i].get_SoC(), i));
			}
			//Batteries that are neither charging not discharging (i.e. state=0) appear in both lists)
		}
  	}
	
	if(Ei>Ptemp) // We need to consume more 
	{
		if(time < SUMMER_START || time > SUMMER_END) //Cold period when heat pumps are functionning
		{
			// Turn on some pumps, choose the ones which are off and which have the lowest T
			while(Ptemp < Ei && Off_Pumps.size()>0)
			{
				int k=Off_Pumps.top().second; // k is the position of the coldest pump which is OFF
				//Possibility to overrule the central controllers demand to switch on if the temperature is too high
				//This is to avoid frequent switchings of the heat pump and to ensure temperature constraints are not violated
				if((*n.getT()).getComposante(k)<(*n.getHouses())[k].get_Tref()+0.9*(*n.getHouses())[k].get_ConfortInterval())
				{
					(*n.getHouses())[k].setSwitch(true); // which we then turn on
					Ptemp+=(*n.getHouses())[k].get_HP_Coeff()/COP;
				}
				Off_Pumps.pop();
			}
		}
		// If Ptemp is still lower than Ei, we still need to consume more by charging the batteries
		if(battery)
		{
			while(Ptemp < Ei && Available_to_charge.size()>0)
			{
				int k=Available_to_charge.top().second; // k is the position of the most empty battery which is not already charging
				int old_state((*n.getB())[k].get_state()); // get the state of the battery which is either: 0 (still) or -1 (dicharging)
				if((*n.getB())[k].get_SoC()<1)
				{
					(*n.getB())[k].set_state(1); // which we set to charging mode
					if(old_state==0)
					{
						// updates the consumption now that the k^th battery is consuming
						Ptemp+=(*n.getB())[k].get_power();
					}else if(old_state==-1)
					{
						// updates the consumption now that the k^th battery is consuming
						// factor 2 comes from the fact that the battery was discharging before and now is charging
						Ptemp+=2*(*n.getB())[k].get_power();
					}
				}
				Available_to_charge.pop();
			}
			/*if(Available_to_charge.size()==0 && Off_Pumps.size()==0)
			{
			cout<<"NO MORE FLEXIBILITY TO CONSUME MORE at time "<<time<<endl;
			}*/
		}
		
	}else{ //(Ei<Ptemp) we need to consume less
		if(time < SUMMER_START || time > SUMMER_END) //Cold period when heat pumps are functionning
		{
			// Turn off some pumps, choose the ones which are on and which have the highest temperature
			while(Ptemp > Ei && On_Pumps.size()>0)
			{
				int k=On_Pumps.top().second; // k is the position of the hottest pump which is ON
				//Possibility to overrule the central controllers demand to switch off if the temperature is too low
				//This is to avoid frequent switchings of the heat pump and to ensure temperature constraints are not violated
				if((*n.getT()).getComposante(k)>(*n.getHouses())[k].get_Tref()-0.9*(*n.getHouses())[k].get_ConfortInterval())
				{
					(*n.getHouses())[k].setSwitch(false); // which we then turn off
					Ptemp=Ptemp-(*n.getHouses())[k].get_HP_Coeff()/COP;
				}
				On_Pumps.pop();
			}
		}
		if(battery)
		{
			// If Ptemp is still greated than Ei, we discharge the batteries to effectively consume less
			while(Ptemp > Ei && Available_to_discharge.size()>0)
			{
				int k=Available_to_discharge.top().second; // k is the position of the fullest battery that can be discharged
				int old_state((*n.getB())[k].get_state()); // get the state of the battery which is either: 0 (still) or 1 (charging)
				if((*n.getB())[k].get_SoC()>0)
				{
					(*n.getB())[k].set_state(-1); // which we set to discharging mode
					if(old_state==0)
					{
						// updates the consumption now that the k^th battery is injecting power to the grid
						Ptemp=Ptemp-(*n.getB())[k].get_power(); 
					}else if (old_state==1)
					{
						// updates the consumption now that the k^th battery is injecting power to the grid
						// factor 2 comes from the fact that the battery was charging before and now is discharging
						Ptemp=Ptemp-2*(*n.getB())[k].get_power(); 
					}
				}
				Available_to_discharge.pop();
			}
			/*if(Available_to_discharge.size()==0 && On_Pumps.size()==0)
			{
				cout<<"NO MORE FLEXIBILITY TO CONSUME LESS at time "<<time<<endl;
			}*/
		}
	}//if Ei=Ptemp then we do nothing, i.e. there is no need to modify the switches anymore
  	
  	//Updates the HP switch counter 
   	for (int i(0); i < n.getNumHouses(); i++)
	{
		if(switch_old[i]==false && (*n.getHouses())[i].HP_on()) //a heat pump turned on
		{
			n.UpdateSwitchCounter(i);
		}
	}
}

//**********************************************************************
// Thermostatic regulation of Boilers
// They are turned on (resp. off) if T<Tref+Delta (resp. T>Tref+Delta)
void update_boiler_switch_Thermostat(vector<Boiler> & B)
{
	double T(0), Tref(0), Delta(0);
	for(unsigned int i(0);i<B.size();i++){
		T=B[i].get_T();
		Tref=B[i].get_Tref();
		Delta=B[i].get_ConfortInterval();
		if(T<Tref-Delta){
			B[i].setSwitch(true); // turns on the boiler
		}else if(T>Tref+Delta){
			B[i].setSwitch(false); // turns off the boiler
		}
	}
}

//**********************************************************************
// Smart boiler regulation based, switch on time based on probability distribution
void update_boiler_switch_smart(vector<Boiler> & B, int step)
{
	double T(0), Tref(0), Delta(0);
	double Tmax(0),Tmin(0);
	int minute(step%1440);
	
	for(unsigned int i(0);i<B.size();i++){
		T=B[i].get_T();
		Tref=B[i].get_Tref();
		Delta=B[i].get_ConfortInterval();
		
		//T_MAX
		if((0 <= minute && minute <7*60) || (B[i].get_switch_time() <= minute && minute <=24*60)){
			Tmax=Tref+Delta;
			
		}
		if((7*60 <= minute && minute < B[i].get_switch_time())){
			Tmax=Tref-1.5*Delta;
		}
		
		//T_MIN
		if(0 <= minute && minute < 5.5*60){
			Tmin=Tref+(2.0/3.0)*Delta;
		}
		if((B[i].get_switch_time() <= minute && minute <=24*60)){
			Tmin=Tref-Delta+Delta*(5.0/3.0)*(minute-(B[i].get_switch_time()))/(1440-(B[i].get_switch_time()));
		}
		if(5.5*60 <= minute && minute < B[i].get_switch_time()){
			Tmin=Tref-2.5*Delta;
		}

		if(T<Tmin){
			B[i].setSwitch(true); // turns on the boiler
		}else if(T>Tmax){
			B[i].setSwitch(false); // turns off the boiler
		}
	}
}

//**********************************************************************
// Generate probability distribution of switching on times based on PV profile
Array Generate_prob(const Weather & w, int time)
{
	double sum(0);
	double net(0);
	vector <double> cumulative_dist(24*60,0.0);
	for(unsigned int i(0);i<cumulative_dist.size();i++)
	{
		net=w.get_Rad40(time+i);
		if(net<0)
		{
			net=0;
		}
		sum+=net;
		cumulative_dist[i]=sum;	
	}
	Array Cumulative_Dist(cumulative_dist.size(),cumulative_dist);
	
	Cumulative_Dist=(1.0/sum)*Cumulative_Dist;
	return Cumulative_Dist;
}


