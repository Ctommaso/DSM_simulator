#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <functional>
#include <random>
#include "Classes/Array.h"
#include "Classes/House.h"
#include "Classes/Neighborhood.h"
#include "Classes/Weather.h"
#include "Classes/Battery.h"
#include "Classes/Control.h"
#include "Classes/Time_integration.h"
using namespace std;

//Function definitions *****
void run_simulation(Neighborhood n, int num_days, int starting_day, bool smart, const Array & Residual_load, const Weather & w); 
void run_simulation(Neighborhood n, int num_days, int starting_day, bool smart, bool battery, const Array & Residual_load, const Weather & w); 
void init_neighborhood(Neighborhood & n, int house_num, bool load_neighborhood, double Av_window_S, double battery_capacity, double battery_power);
//**************************

int main()
{
	int house_num(0), num_days(0), starting_day(0);
	double Av_window_S(0), battery_capacity(0), battery_power(0);
	string file_T,file_Rad90,file_Rad40, file_Residual;
	bool load_neighborhood(false);
	cin >> house_num >> starting_day >> num_days >> file_T >> file_Rad90 
	    >> file_Rad40 >> file_Residual >> Av_window_S >> battery_capacity >> battery_power >> load_neighborhood;
	
	Weather w(file_T,file_Rad90,file_Rad40);
	Array Residual_load(file_Residual);
	
	auto start = chrono::steady_clock::now(); //Start timing
		
	Neighborhood n;
	init_neighborhood(n, house_num, load_neighborhood, Av_window_S, battery_capacity, battery_power);
	
	run_simulation(n, num_days, starting_day, false, Residual_load, w); //Simulate Thermostat
	run_simulation(n, num_days, starting_day, true, Residual_load, w); //Simulate Smart
	run_simulation(n, num_days, starting_day, true, true, Residual_load, w); //Simulate Smart & Battery
	
	auto end = chrono::steady_clock::now();	
	auto diff = end - start;
	cout <<"Duration="<< (chrono::duration <double, milli> (diff).count())/1000 << "seconds" << endl;
	
	return 0;
}

// *********************************************************************
void init_neighborhood(Neighborhood & n, int house_num, bool load_neighborhood, double Av_window_S, double battery_capacity, double battery_power)
{	
	std::pair<double, double> BATTERY(1000*battery_capacity,1000*battery_power); // Pair to describe battery (capacity, power)[Wh, W]
	string fn("Neighborhood.dat");
	
	if(load_neighborhood==true)
	{
		cout << "YO NO NEED TO INVENT ONE"<<endl;
		n = Neighborhood(house_num, fn, BATTERY); //Load neighborhood from existing file
	}else{
		std::pair<double, double> TH_CAPACITY(13000,27000); // Thermal Capacity interval [Wh/°K] corresponding to [50-100] MJ/°K 13000,27000
		std::pair<double, double> TH_COND(150,300); // Thermal Conductivity interval [W/°C]
		std::pair<double, double> REF_T(21,23);// Comfort Temperature
		std::pair<double, double> CONFORT_INTERVAL(1.5,1.5);// Comfort Interval
		std::pair<double, double> WINDOWS(Av_window_S-5,Av_window_S+5); // South oriented window surface		
		
		//Neighborhood constructor, based on uniform distribution
		n = Neighborhood(house_num, TH_CAPACITY, TH_COND, REF_T, CONFORT_INTERVAL, WINDOWS, BATTERY); 
		n.Save_state(fn);
	}
}

// *********************************************************************
void run_simulation(Neighborhood n, int num_days, int starting_day, bool smart , bool battery, const Array & Residual_load, const Weather & w)
{
	double COP(3.0); // Coefficient of performance P_thermal=COP*P_electric
	double deltat(1.0/60.0); // Time step = 1 minute =1/60 h,
	int horizon(24*60); // 1440 minutes
	double to_match(0);
	int day_counter(0); 
	
	string fn("Res_HP_Control_B.dat"),fn2("Switch_counts_Control_B.dat"),fn3("Battery_SoC_Control_B.dat");
		
	ofstream Res_HP(fn,ios::binary | ios::out);//Creates file to store the results
	ofstream Res_B_SoC(fn3,ios::binary | ios::out);//Creates file to store the results
	
	//Time evolution starts here
	for(int step(0);step<60*24*(num_days-1);step++)
	{	
		if(step%(24*60)==0)
		{
			cout<<"*** DAY "<<starting_day+day_counter<<" ***"<<endl;
			day_counter++;
		}
		if(smart) // receeding horizon every minute
		{
			std::pair<double, double> Etot(Estimate_Etot(n,w,starting_day*24+step*deltat,step,horizon)); 
			if(step%(24*60)==0)
			{
				cout<<"Etot "<<Etot.first<<endl;
				cout<<"Terme correctif "<<Etot.second<<endl;
			}
			// Optimal consumption to match
			to_match=Opt_consumption(Etot.first+Etot.second,step,horizon,Residual_load,COP);
		}
		//Euler step 
		Euler(n,starting_day,step,deltat,to_match,smart,w,COP, battery);
		//Prints to file: time in [h], Istantaneous HP electrical power [W], Total electrical Power [W]
		Res_HP << starting_day*24+step*deltat <<" "<<(1.0/COP)*n.get_Individual_Load_HP() + n.get_Individual_Load_Batteries() 
		       <<" "<<(1.0/COP)*n.getPtot_HP() + n.getPtot_Batteries() << endl;
		
		//Prints to file: individual SoC
		Res_B_SoC << n.get_Individual_SoC() << endl;
	}

	Res_HP.close();
	Res_B_SoC.close();
	n.SaveSwitchData(fn2);
}

// *********************************************************************
void run_simulation(Neighborhood n, int num_days, int starting_day, bool smart , const Array & Residual_load, const Weather & w)
{
	bool battery(false);
	double COP(3.0); // Coefficient of performance P_thermal=COP*P_electric
	double deltat(1.0/60.0); // Time step = 1 minute =1/60 h,
	int horizon(24*60); // 1440 minutes
	double to_match(0);
	int day_counter(0); 
	
	string fn("Res_HP"),fn2("Switch_counts");
	if(smart)
	{		
		fn+="_Control.dat";
		fn2+="_Control.dat";
	}else
	{
		fn+="_Thermostat.dat";
		fn2+="_Thermostat.dat";
	}

	ofstream Res_HP(fn,ios::binary | ios::out);//Creates file to store the results
	
	//Time evolution starts here
	for(int step(0);step<60*24*(num_days-1);step++)
	{	
		if(step%(24*60)==0)
		{
			cout<<"*** DAY "<<starting_day+day_counter<<" ***"<<endl;
			day_counter++;
		}
		if(smart) // receeding horizon every minute
		{
			std::pair<double, double> Etot(Estimate_Etot(n,w,starting_day*24+step*deltat,step,horizon)); 
			if(step%(24*60)==0)
			{
				cout<<"Etot "<<Etot.first<<endl;
				cout<<"Terme correctif "<<Etot.second<<endl;
			}
			// Optimal consumption to match
			to_match=Opt_consumption(Etot.first+Etot.second,step,horizon,Residual_load,COP);
		}
		//Euler step 
		Euler(n,starting_day,step,deltat,to_match,smart,w,COP, battery);
		//Prints to file: time in [h], Istantaneous HP electrical power [W], Total electrical Power [W]
		Res_HP << starting_day*24+step*deltat <<" "<<(1.0/COP)*n.get_Individual_Load_HP()<<" "<<(1.0/COP)*n.getPtot_HP()<<endl;
	}

	Res_HP.close();
	n.SaveSwitchData(fn2);
}
