#ifndef BATTERY_H
#define BATTERY_H
#include <iostream>
#include <random>
using namespace std;

class Battery{

	public:
    //Constructeur:
    Battery(double CAPACITY, double POWER);
	
	double get_power() const {return power;};
	double get_capacity() const {return capacity;};	
	double get_SoC() const {return state_of_charge;};	
	int get_state() const {return battery_state;};
	
	void set_SoC(double SoC) {state_of_charge=SoC;};
	void set_state(int s) {battery_state=s;};
	
	private:

	double state_of_charge; // State of charge of the battery in [0,1]
	double capacity; // Battery capacity in [Wh]
	double power; // Nominal poer fo the battery [W]
	int battery_state; // Can take values: -1, 0, 1 for (discharging, still, charging) states.
};

#endif
