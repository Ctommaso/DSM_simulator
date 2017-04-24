#ifndef BOILER_H
#define BOILER_H
#include <iostream>
#include <iomanip>
#include <fstream>
#include <random>
#include "Array.h"
#include <random>
using namespace std;

class Boiler{

	public:
    //Constructeur:
    Boiler(double VOLUME, double POWER, bool INTERRUPTEUR, double REF_T, double CONFORT_INTERVAL, double T_START, double TCOLD,double THERMAL_COND);
	
	double get_Heating_Power() const {return power;};
	double get_Th_Capacity() const {return thermal_capacity;};
	double get_Th_Cond() const {return thermal_cond;};
	double get_Volume() const {return volume;};
	
	double get_T() const {return T;};//Acces and modify boiler temperature
	void set_T(double t) {T=t;};
	
	double get_Tref() const {return T0;};
	double get_Tcold() const {return Tcold;};
	double get_ConfortInterval() const {return confort_interval;};
	int get_Switch_counter() const {return switch_counter;};
	void setSwitch(bool a); 
	bool on() const {return Switch;};
	
	void set_switch_time(double prob, Array Cumulative_Prob_dist);
	int get_switch_time() const {return switch_time;};
	double Heating_power();
	
	private:

	double T;// Temerature of the water in the boiler
	double volume;// Volume of the boiler
	double thermal_capacity;//Thermal capacity of water
	double thermal_cond;//Thermal cond of boiler
	double power;// Electric power of the boiler [W] (Electric Power=Heating Power)
	bool Switch;// True(false), means boiler is on(off)
	double T0; // Internal reference temperature for the water in the boiler
	double confort_interval; // Temperature interval regarded as confortable and hygenic
	double Tcold;// Temperature of the cold water entering the boiler
	int switch_counter; // integer counting the number of times the boiler was turned on
	int switch_time; //time for switching on the boiler
};

#endif
