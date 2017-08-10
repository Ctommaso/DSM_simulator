#include "Neighborhood.h"

//Constructor from parameters
Neighborhood::Neighborhood(int NUM_HOUSES, std::pair<double, double> THERMIC_CAP, 
                           std::pair<double, double> THERMIC_COND, std::pair<double, double> REF_T, 
                           std::pair<double, double> CONFORT_INTERVAL, std::pair<double,double> WINDOWS,
                           std::pair<double,double> BATTERY)
{
	// Generates random values for the physical building constants which are drawn from a uniform distribution
	num_houses=NUM_HOUSES;
	std::random_device rd1,rd2,rd3,rd4,rd5,rd6,rd7;
	std::mt19937 gen1(rd1()),gen2(rd2()),gen3(rd3()),gen4(rd4()),gen5(rd5()),gen6(rd6()),gen7(rd7());
	std::uniform_real_distribution<> dis1(REF_T.first,REF_T.second);// uniform_real distribution between numbers [n,m)
	std::uniform_real_distribution<> dis2(THERMIC_COND.first,THERMIC_COND.second);
	std::uniform_real_distribution<> dis3(THERMIC_CAP.first,THERMIC_CAP.second);
	std::uniform_real_distribution<> dis4(WINDOWS.first,WINDOWS.second);
	std::uniform_real_distribution<> dis7(CONFORT_INTERVAL.first,CONFORT_INTERVAL.second);

	std::bernoulli_distribution dis5(0.33); // 1/3 of pumps are on (arbitrary choice)
		
	vector< int > SWITCH_COUNTER(NUM_HOUSES,0);
	switch_counter=SWITCH_COUNTER;
	
	vector <double> Tinitiale;
	
	Battery b(BATTERY.first,BATTERY.second);// Capacity Wh, Power W, Check battery constructor to see SoC and initial state
	
	for(int i(0);i<num_houses;i++)
	{
		//House initialization
		double tref(dis1(gen1)), conductivity(dis2(gen2)),capacity(dis3(gen3)),window_surface(dis4(gen4)), confort_interval(dis7(gen7));
		bool Switch_initial(dis5(gen5));
		std::uniform_real_distribution<> dis6(tref-confort_interval,tref+confort_interval); 
		Tinitiale.push_back(dis6(gen6)); //The starting temperature is chosen randomly from the interval [Tconf-confort_interval,Tconf+confort_interval]
		if(Switch_initial){Ptot_HP+=conductivity*30.0;}
		House h(capacity,conductivity,conductivity*30.0,Switch_initial,tref,confort_interval,window_surface); 
		houses.push_back(h);
		
		// All batteries are the same
		batteries.push_back(b);
	}
	Array t(num_houses,Tinitiale);
	T=t;
}

//Constructor from file
//Generates a neighborhood by reading a file where each line describes the physical parameters of a house
Neighborhood::Neighborhood(int NUM_HOUSES, string filename, std::pair<double,double> BATTERY)
{
	num_houses=NUM_HOUSES;
	int compteur(0);
	ifstream infile;
	infile.open(filename);

	double t_ref,tinitiale,conductivity,capacity,windows,confort_interval;
	vector<double> Tinitiale;
	bool Switch_initial;
	
	vector< int > SWITCH_COUNTER(NUM_HOUSES,0);
	switch_counter=SWITCH_COUNTER;
	
	while(true)
	{
		// Careful we are not loading the battery specs from file 
		infile >> t_ref >> confort_interval >> conductivity >> capacity >> tinitiale >> Switch_initial
		       >> windows;
		if(infile.eof()) break;
		Tinitiale.push_back(tinitiale);
		if(Switch_initial){Ptot_HP+=conductivity*30.0;}
		House h(capacity,conductivity,conductivity*30.0,Switch_initial,t_ref,confort_interval,windows);
		houses.push_back(h);
		
		// All batteries are the same, consturctor: SoC = 0 and initial state = 0
		Battery b(BATTERY.first,BATTERY.second);// Capacity Wh, Power W
		batteries.push_back(b);
		
		compteur++;
	}
	infile.close();
	Array t(num_houses,Tinitiale);
	T=t;
}

//Save Neighboorhood settings to file
void Neighborhood::Save_state(string filename)
{
	ofstream file;
	file.open(filename);
	
	for(int i(0);i<num_houses;i++)
	{
		file<<houses[i].get_Tref()<<" "<<houses[i].get_ConfortInterval()<<" "
		    <<houses[i].get_Th_Cond()<<" "<<houses[i].get_Th_Capacity()<<" "
		    <<T.getComposante(i)<<" "<<houses[i].HP_on()<<" "<<houses[i].get_Window_Surf()<<endl;
		    //Not saving to file the battery data
		    //<<" "<<batteries[i].get_capacity()<<" "<<batteries[i].get_power()<<endl;
	}
	file.close();
}

//Saves to file the switch on/off statistics for the neighborhood
void Neighborhood::SaveSwitchData(string filename)
{
	ofstream file;
	file.open(filename);
		
	for(int i(0);i<num_houses;i++)
	{
		file<<switch_counter[i]<<endl;
	}
	file.close();
}

//Computes the total niehgboorhood's Heat Pump consumption (thermal power)
void Neighborhood::ComputePtot_HP()
{
	Ptot_HP=0;
	for(unsigned int i(0); i<houses.size() ; i++)
	{
		if(houses[i].HP_on())
		{
			Ptot_HP+=houses[i].get_HP_Coeff();
		}
	}
}

//Computes the total niehgboorhood's Battery consumption (electric power)
void Neighborhood::ComputePtot_Batteries()
{
	Ptot_Batteries=0;
	for(unsigned int i(0); i<batteries.size() ; i++)
	{
		Ptot_Batteries+=batteries[i].get_power()*batteries[i].get_state();
	}
}

// Returns an array containing the istantaneous thermal load of the individual heat pumps
// (i.e. checks if the Heat pumps are on)
Array Neighborhood::get_Individual_Load_HP()
{
	vector<double> individual_load(houses.size(), 0.0);
	for(unsigned int i(0); i<houses.size() ; i++)
	{
		if(houses[i].HP_on())
		{
			individual_load[i]=houses[i].get_HP_Coeff();
		}
	}
	Array Individual_Load(individual_load.size(), individual_load); 
	return Individual_Load;
}

// Returns an array containing the istantaneous electric consumption of the individual batteries
// (i.e. checks the battery status)
Array Neighborhood::get_Individual_Load_Batteries()
{
	vector<double> individual_load(batteries.size(), 0.0);
	for(unsigned int i(0); i<batteries.size() ; i++)
	{
		individual_load[i]=batteries[i].get_power()*batteries[i].get_state();
	}
	Array Individual_Load(individual_load.size(), individual_load); 
	return Individual_Load;
}

// Returns an array containing the istantaneous electric consumption of the individual batteries
// (i.e. checks the battery status)
Array Neighborhood::get_Individual_SoC()
{
	vector<double> individual_SoC(batteries.size(), 0.0);
	for(unsigned int i(0); i<batteries.size() ; i++)
	{
		individual_SoC[i]=batteries[i].get_SoC();
	}
	Array Individual_SoC(individual_SoC.size(), individual_SoC); 
	return Individual_SoC;
}
