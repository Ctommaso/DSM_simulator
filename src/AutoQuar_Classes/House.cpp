#include "House.h"

// Public Methods

//Constructor
House::House(double THERMIC_CAPACITY,double THERMIC_COND ,double HEATING_POWER, bool INTERRUPTEUR, double REF_T, double CONFORT_INTERVAL,double WINDOWS) //Constructeur:
{
	thermic_cond=THERMIC_COND;
	thermic_capacity=THERMIC_CAPACITY;
	heating_power=HEATING_POWER;
	interrupteur=INTERRUPTEUR;
	T0=REF_T;
	confort_interval=CONFORT_INTERVAL;
	windows_surf=WINDOWS;
	store=true;
	last_time_on=0;
	last_time_off=0;
}
