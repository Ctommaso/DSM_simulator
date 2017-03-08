#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <chrono>
#include <queue>
#include <functional>
#include <stdio.h>
#include <sstream>
#include "AutoQuar_Classes/Array.h"
#include "AutoQuar_Classes/Boiler.h"
#include "AutoQuar_Classes/Weather.h"
using namespace std;

//************************* FUNCTION DEFINITIONS **************************************
//*************************************************************************************
void Euler(vector<Boiler> & B, int step, double deltat, bool smart, const vector<Array> & Water_cons); // Euler step
double rhs_b(const Boiler & B, int step, const Array & Water_cons); // Heat flow equation for boilers
void update_boiler_switch_Thermostat(vector<Boiler> & B);//Updates the switches: Thermostat
void update_boiler_switch_smart(vector<Boiler> & B, int step);//Updates the switches intelligently
void save_boiler_settings(vector<Boiler> & B, string fn);//Saves boiler settings
vector <Boiler> load_boiler_settings(string fn);//Function to initialize the vector of from a settings file
vector <Boiler> init_boilers(unsigned int num_houses);//Function to initialize the vector of boilers
vector <Array> init_water_cons(string Water_fn);//Function to initialize the water consumptions
//double probability(double T,double Tref,double Delta, int minute_of_day); // Probability function for smart switching 
Array Generate_prob(const Weather & w,int time); //Updates the probability distribution 
//*************************************************************************************
//*************************************************************************************

int main()
{
	unsigned int num_days,starting_day,num_houses, day(0);
	bool smart; 
	double deltat(1.0/60.0),tot_consumption(0); // Pas temporel = 1minute =1/60 h,
	string Water_fn,Res_fn("Res_Boiler"),Text_fn,Rad90_fn,Rad40_fn;
	
	cin >> num_houses >> starting_day >> num_days >> smart >> Water_fn >> Text_fn >> Rad90_fn >> Rad40_fn;
	
	cout<<"START"<<endl;
	vector <Boiler> B;
	vector <Array> Water_cons(init_water_cons(Water_fn));

	Weather w(Text_fn,Rad90_fn,Rad40_fn);
	Array Cumulative_Prob(24*60);

	if(smart){
		B=init_boilers(num_houses);
		Res_fn+="_Control.dat";
		save_boiler_settings(B,"Boiler_Settings.dat");
		
	}else{
		B=load_boiler_settings("Boiler_Settings.dat");
		Res_fn+="_Thermostat.dat";
	}
	
	ofstream Results(Res_fn,ios::binary | ios::out);//Creates file to store the results
	for(unsigned int step(0);step<60*24*(num_days);step++){//60*24*num_days 60*24*(num_days-1)	
		if(step%(24*60)==0){
			cout<<"*** DAY "<<starting_day+day<<" ***"<<endl;
			day++;
			if(smart){
				Cumulative_Prob=Generate_prob(w,step);
				for(unsigned int i(0);i<B.size();i++){
					B[i].set_switch_time(Cumulative_Prob);
				}
			}
		}
		Euler(B,step,deltat,smart,Water_cons);//Euler step 
		tot_consumption=0;
		Results << starting_day*24+step*deltat <<" ";
		//Saves individual temperatures
		for(unsigned int i(0);i<B.size();i++){
			Results<<B[i].get_T()<<" ";
		}
		//Saves individual powers
		for(unsigned int i(0);i<B.size();i++){
			Results<<B[i].Heating_power()<<" ";
			tot_consumption+=B[i].Heating_power();
		} 
		Results<<tot_consumption<<endl;
	}
	Results.close();
	return 0;
}
//*********************** INITIALIZE BOILERS **************************************************
vector <Boiler> init_boilers(unsigned int num_houses)
{
	double Tref(55),Tcold(10),comfort_interval(5);
	std::random_device rd1,rd2,rd3,rd4;
	std::mt19937 gen1(rd1()),gen2(rd2()),gen3(rd3()),gen4(rd4());
	std::discrete_distribution<int> dis1 {0.15,0.35,0.35,0.15}; //Discrete Probabilites for boiler of (150,200,250,300) Liters
	vector<double> Boiler_size={200,250,300,350};// volume of Boilers in Liters
	vector<double> Thermal_cond={0.98,1.16,1.34,1.52};// Thermal conductivity values in [W/°K] (From TD J.Mayor)
	std::uniform_real_distribution<> dis2(10,20); //Heating power between [10,20][W/liter]
	std::bernoulli_distribution dis3(0.2); // 1/5 Bernoulli distribution 1/5 prob of having boiler on 
	std::uniform_real_distribution<> dis4(Tref-comfort_interval,Tref+comfort_interval); //Starting Temperature
	
	vector<Boiler> B;
	int index;
	double volume;
	double power;
	bool Switch;
	double Tstart;
	
	for(unsigned int i(0); i<num_houses; i++)
	{
		index = dis1(gen1);//choose index form 1 to 4
		volume = Boiler_size[index]; //VOL [liters]
		power = dis2(gen2)*volume; //[10,20][W/liters] * Volume[liters]
		Switch = dis3(gen3);
		Tstart = dis4(gen4);

		Boiler b(volume,power,Switch,Tref,comfort_interval,Tstart,Tcold,Thermal_cond[index]);
		B.push_back(b);
		/*cout<<"Boiler "<<i<<" Vol="<<volume<<"[litres]  power="<<power<<"[W]";
		cout<<" Switch "<<Switch<<" Tref="<<Tref<<" Comfort="<<comfort_interval<<" Tstart="<<Tstart;
		cout<<" Tcold="<<Tcold<<"Thermal cond="<<Thermal_cond[index]<<"[W/°k]"<<endl;*/
	}
	return B;
}
//*********************** INITIALIZE WATER CONS ***********************************************
vector <Array> init_water_cons(string Water_fn)
{
	vector< Array > allData;
	ifstream fin(Water_fn);
	string line;
	while (getline(fin, line)){      // for each line
		vector<double> lineData;     // create a new row
		double val;
		istringstream lineStream(line); 
		while (lineStream >> val){        // for each value in line
			lineData.push_back(val);      // add to the current row
		}
		Array Water_cons(lineData.size(), lineData);
		Water_cons=Water_cons*60;         //This transforms the water flow from [liters/min] to [liters/h]
		allData.push_back(Water_cons);    // add row to allData
	}
	return allData;
}

//************************ SAVES BOILER SETTINGS **********************************************
void save_boiler_settings(vector<Boiler> & B, string fn)
{
	ofstream file;
	file.open(fn);
	for(unsigned int i(0);i<B.size();i++)
	{
		file<<B[i].get_Volume()<<" "<<B[i].get_Heating_Power()<<" "<<B[i].on()<<" ";
		file<<B[i].get_Tref()<<" "<<B[i].get_ConfortInterval()<<" "<<B[i].get_T()<<" ";
		file<<B[i].get_Tcold()<<" "<<B[i].get_Th_Cond()<<endl;
	}
	file.close();
}

//************************ INITIALIZE BOILERS FROM FILE ***************************************
//Generates a vector of Boilers by reading a file where each line describes the physical parameters of a boiler
vector <Boiler> load_boiler_settings(string fn)
{
	vector <Boiler> B;
	ifstream infile;
	infile.open(fn);

	double volume,power,Tref,comfort_interval,Tstart,Tcold,thermal_cond;
	bool Switch;
	
	while(true)
	{
		infile >> volume >> power >> Switch >> Tref >> comfort_interval >> Tstart >> Tcold >> thermal_cond;
		if(infile.eof()) break;
		Boiler b(volume,power,Switch,Tref,comfort_interval,Tstart,Tcold,thermal_cond);
		B.push_back(b);
	}
	infile.close();
	return B;
}
//************************* INTEGRATION STEP **************************************************
void Euler(vector<Boiler> & B, int step, double deltat, bool smart, const vector <Array> & Water_cons)
{
	
	for(unsigned int i(0);i<B.size();i++){
		B[i].set_T( B[i].get_T() + deltat*rhs_b(B[i],step,Water_cons[i]) ); // Euler update
	}
	if(smart){
		update_boiler_switch_smart(B,step);// updates the boiler switches:smart
	}else{
		update_boiler_switch_Thermostat(B);// updates the boiler switches:thermostat
	}	
}
//********************** EVALUATION RHS *******************************************************
double rhs_b(const Boiler & B, int step, const Array & Water_cons) // Heat flow equation for boilers
{
	double Heating_pow(0.0);
	double T_house(20); // set the temperature of the house to 20 °C
	if(B.on()){
		Heating_pow=B.get_Heating_Power();
	}
	return (Water_cons.getComposante(step)*(B.get_Tcold()-B.get_T()) + (Heating_pow+B.get_Th_Cond()*(T_house-B.get_T()))/B.get_Th_Capacity())/B.get_Volume();
}
//************************* UPDATE SWITCH THERMOSTAT ******************************************
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
//************************* UPDATE SWITCH SMART ******************************************
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
//************************* GENERATE CUMULATIVE DISTRIBUTION FUNCTION ******************************************
Array Generate_prob(const Weather & w, int time) //Generate probability distribution 
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


