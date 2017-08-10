#ifndef HOUSE_H
#define HOUSE_H
#include <iostream>
#include <vector>
#include <iomanip>
#include <fstream>
using namespace std;

class House{

	public:
    //Constructeur:
    House(double THERMIC_CAPACITY,double THERMIC_COND ,double HEATING_POWER, bool INTERRUPTEUR, double REF_T, double CONFORT_INTERVAL, double WINDOWS);
	
	double get_HP_Coeff() const {return heating_power;};
	double get_Th_Cond() const {return thermic_cond;};	
	double get_Th_Capacity() const {return thermic_capacity;};	
	
	bool HP_on() const {return interrupteur;};
	bool Blinds_up() const {return store;};
	void setSwitch(bool a){interrupteur=a;};
	void setBlinds(bool a){store=a;};
	
	double get_Tref() const {return T0;};
	double get_ConfortInterval() const {return confort_interval;};
	double get_Window_Surf() const {return windows_surf;};
	
	double get_last_time_off() const {return last_time_off;};
	double get_last_time_on() const {return last_time_on;};
	void set_last_time_off(double t){last_time_off=t;};
	void set_last_time_on(double t){last_time_on=t;};


	private:

	double thermic_cond; // Thermic conductivity of the house
	double thermic_capacity; // Thermic capacity of the house
	double heating_power; // Heat power of the heat pump
	double T0; // Internal reference temperature
	double confort_interval; // Temperature interval regarded as confortable
	double windows_surf; // Windows surface [m^2]
	bool interrupteur; // True(false), means heat pump is on(off)
	bool store; // True(false), means blinds are up(down)
	double last_time_on; //Time when the pump was turned off
	double last_time_off; //Time when the pump was turned on 
};

#endif
