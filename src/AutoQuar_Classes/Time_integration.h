#ifndef TIMEINTEGRATION_H
#define TIMEINTEGRATION_H
#include <iostream>
#include <queue>
#include "Neighborhood.h"
#include "Weather.h"
#include "Control.h"
using namespace std;

// Euler integration step
void Euler(Neighborhood & n, int starting_day, int step, double deltat, double Ei, bool smart, const Weather & w, double COP, bool battery);

// Heat flow equation
Array rhs(const Array & T, const vector< House > & houses, int step, const Weather & w); 


#endif
