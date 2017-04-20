#ifndef CONTROL_H
#define CONTROL_H
#include <iostream>
#include <queue>
#include "Neighborhood.h"
#include "SortingPairs.h"
#include "Weather.h"
using namespace std;

//Thermostatic control
void update_hp_switch_Thermostat(Neighborhood & n, double time);

//Smart control
void update_hp_switch(Neighborhood & n, double Ei, double time, double COP, bool battery);

//Estimation of the thermal energy requirement for a given horizon
std::pair<double, double> Estimate_Etot(Neighborhood & n,const Weather & w, double time, int step, int horizon); 

//Computation of the optimal istantaneous consumption
double Opt_consumption(double E_estimated, int step, int horizon, const  Array & Residual_load, double COP);

#endif