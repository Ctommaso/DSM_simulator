#ifndef NEIGHBORHOOD_H
#define NEIGHBORHOOD_H
#include <iostream>
#include <vector>
#include <iomanip>
#include <fstream>
#include "Array.h"
#include "House.h"
#include "Battery.h"
#include <random>
using namespace std;

class Neighborhood{

	public:
    
    // Constructors
    Neighborhood(int NUM_HOUSES, std::pair<double, double> THERMIC_CAP, std::pair<double, double> THERMIC_COND, 
                                 std::pair<double, double> REF_T, std::pair<double, double> CONFORT_INTERVAL, 
                                 std::pair<double,double> WINDOWS, std::pair<double,double> BATTERY); // Constructor from parameters
    Neighborhood(int NUM_HOUSES, string filename, std::pair<double,double> BATTERY); //Constructor based on data FILE
	Neighborhood() = default; //Default constructor
	
	void Save_state(string filename); //Saves Nieghborhood to file
	void SaveSwitchData(string filename);
	vector<House>* getHouses(){return &houses;}	// Returns a pointer which points onto the vector of Houses called houses
	vector<Battery>* getB(){return &batteries;}	// Returns a pointer which points onto the vector of Batteries called batteries
	Array* getT(){return &T;}	//Returns a pointer which points onto the Array T.
	// whenever we call this funtion of the Neighborhood class, if one wants to use the array of temperatures (i.e. access
	// values in the Euler scheme for exemple), one needs to add * before the pointer returned by getT()
	
	// Functions that return: 
	int getNumHouses() const {return num_houses;}; // Number of houses
	double getPtot_HP() const {return Ptot_HP;}; // Total thermal power of HP 
	double getPtot_Batteries() const {return Ptot_Batteries;}; // Total electric power of HP 
	
	void ComputePtot_HP();// Computes the total consumption of the neighborhood's Heat pumps (thermal power)
	void ComputePtot_Batteries();// Computes the total consumption of the neighborhood's Batteries (electric power)
	
	void UpdateSwitchCounter(int i){switch_counter[i]+=1;}
	
	// returns an array containing the istantaneous thermal load of the individual HP
	// (i.e. checks if the Heat pumps are on)
	Array get_Individual_Load_HP();
	
	// returns an array containing the istantaneous power of the individual batteries
	// (i.e. checks the Battery status)
	Array get_Individual_Load_Batteries(); 
	                             
	// returns an array containing the SoC of the individual houses 
	Array get_Individual_SoC(); 
	
	private:
	
	int num_houses;
	Array T; // Temperatures inside the houses
	vector< int > switch_counter; // Keeps track of the number of times the heat pumps will be turned on
	vector<House> houses; // Vector of houses
	vector<Battery> batteries; // Vector of batteries
	double Ptot_HP; // Neighborhood's total HEATPUMP thermal power consumption
	double Ptot_Batteries; // Neighborhood's total BATTERY electric power consumption
	
};

#endif
