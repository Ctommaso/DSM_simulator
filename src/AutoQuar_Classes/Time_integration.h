#ifndef TIMEINTEGRATION_H
#define TIMEINTEGRATION_H
#include <iostream>
#include <queue>
#include "Neighborhood.h"
#include "Weather.h"
#include "Control.h"
#include "Boiler.h"
using namespace std;

// Euler integration step Heat Pumps
void Euler(Neighborhood & n, int starting_day, int step, double deltat, double Ei, bool smart, 
           const Weather & w, double COP, bool battery);

// Euler integration step boilers
void Euler(vector<Boiler> & B, int step, double deltat, bool smart, const vector <Array> & Water_cons);

// Thermal power equation for buildings
Array rhs(const Array & T, const vector< House > & houses, int step, const Weather & w); 

// Thermal power equation for boilers
double rhs_b(const Boiler & B, int step, const Array & Water_cons);

#endif
