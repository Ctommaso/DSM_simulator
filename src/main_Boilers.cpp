#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include "Classes/Array.h"
#include "Classes/Boiler.h"
#include "Classes/Weather.h"
#include "Classes/Time_integration.h"
#include "Classes/Control.h"
using namespace std;

// FUNCTION DEFINITIONS ************************************************
void save_boiler_settings(vector<Boiler> & B, string fn);//Saves boiler settings
vector <Boiler> load_boiler_settings(string fn);//Function to initialize the vector of from a settings file
vector <Boiler> init_boilers(unsigned int num_houses, bool load_neighborhood);//Function to initialize the vector of boilers
vector <Array> init_water_cons(string Water_fn);//Function to initialize the water consumptions
void run_simulation(unsigned int num_days,unsigned int starting_day, vector<Boiler> B, const vector <Array> & Water_cons, const Weather & w, bool smart, string Res_fn);
//**********************************************************************

int main()
{
	unsigned int num_days, starting_day, num_houses;
	bool load_neighborhood; 
	
	string Water_fn,Text_fn,Rad90_fn,Rad40_fn;
	
	cin >> num_houses >> starting_day >> num_days >> load_neighborhood >> Water_fn >> Text_fn >> Rad90_fn >> Rad40_fn;
	
	//Boiler initialization
	vector <Boiler> B(init_boilers(num_houses,load_neighborhood));
	
	//Hot water consumption initialization
	vector <Array> Water_cons(init_water_cons(Water_fn));

	Weather w(Text_fn,Rad90_fn,Rad40_fn);

	run_simulation(num_days, starting_day, B, Water_cons, w,true, "Res_Boiler_Control.dat");
	run_simulation(num_days, starting_day, B, Water_cons, w,false, "Res_Boiler_Thermostat.dat");
	
	return 0;
}

// ********************** RUN SIMULATION ******************************************************
void run_simulation(unsigned int num_days, unsigned int starting_day, vector<Boiler> B, const vector <Array> & Water_cons, const Weather & w, bool smart, string Res_fn)
{
	cout<<"START"<<endl;
	unsigned int day(0);
	double deltat(1.0/60.0),tot_consumption(0); // Pas temporel = 1minute =1/60 h,
	Array Cumulative_Prob(24*60);

	// Initialization of the random number generator for defining switch times
	std::random_device rd;
	std::mt19937 gen(rd());
	std::uniform_real_distribution<double> dis(0,1);
	double prob(0);
	
	ofstream Results(Res_fn,ios::binary | ios::out);//Creates file to store the results
	for(unsigned int step(0);step<60*24*(num_days);step++){//60*24*num_days 60*24*(num_days-1)	
		if(step%(24*60)==0){
			cout<<"*** DAY "<<starting_day+day<<" ***"<<endl;
			day++;
			if(smart){
				Cumulative_Prob=Generate_prob(w,step);
				for(unsigned int i(0);i<B.size();i++){
					prob=dis(gen);
					B[i].set_switch_time(prob, Cumulative_Prob);
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
}

//*********************** INITIALIZE BOILERS **************************************************
vector <Boiler> init_boilers(unsigned int num_houses, bool load_neighborhood)
{
	vector<Boiler> B;
	string fn("Boiler_settings.dat");
	
	if(load_neighborhood==true)
	{
		cout<<"I'VE LOADED THE BOILER FILE"<<endl;
		B = load_boiler_settings(fn);
	}else{
		cout<<"CREATING BOILER FILE"<<endl;
		double Tref(55),Tcold(10),comfort_interval(5);
		std::random_device rd1,rd2,rd3,rd4;
		std::mt19937 gen1(rd1()),gen2(rd2()),gen3(rd3()),gen4(rd4());
		std::discrete_distribution<int> dis1 {0.15,0.35,0.35,0.15}; //Discrete Probabilites for boiler of (150,200,250,300) Liters
		vector<double> Boiler_size={200,250,300,350};// volume of Boilers in Liters
		vector<double> Thermal_cond={0.98,1.16,1.34,1.52};// Thermal conductivity values in [W/°K] (From TD J.Mayor)
		std::uniform_real_distribution<> dis2(10,20); //Heating power between [10,20][W/liter]
		std::bernoulli_distribution dis3(0.2); // 1/5 Bernoulli distribution 1/5 prob of having boiler on 
		std::uniform_real_distribution<> dis4(Tref-comfort_interval,Tref+comfort_interval); //Starting Temperature
		
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
		}
		save_boiler_settings(B,fn);
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
