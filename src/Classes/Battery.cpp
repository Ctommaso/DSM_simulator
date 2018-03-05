#include "Battery.h"

// Public Methods

//Constructor
Battery::Battery(double CAPACITY, double POWER) //Constructeur:
{
	capacity=CAPACITY; // Battery capacity in [Wh]
	power=POWER; // Nominal power fo the battery [W]
	battery_state=0; // Set the battery state to 0 (still)
	
	//Initialize state of charge randomly between 0 and 1, according to a uniform distribution function 
	/*std::random_device rd1;
	std::mt19937 gen1(rd1());
	std::uniform_real_distribution<> dis1(0,0.3);// uniform_real distribution between numbers [n,m)
	state_of_charge=dis1(gen1);
	*/
	
	// Initialize state of charge at 0
	state_of_charge=0.0;
}
