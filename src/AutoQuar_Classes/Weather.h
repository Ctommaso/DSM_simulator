#ifndef WEATHER_H
#define WEATHER_H
#include <iostream>
#include <vector>
#include <iomanip>
#include <fstream>
#include "Array.h"
using namespace std;

class Weather{

	public:
    // Constructor:
    Weather(string filename_Text, string filename_Radiation, string filename_Radiation40);
	
	// Access temperature and radiation data;
	double get_Rad(int i) const {return Radiation.getComposante(i);};
	double get_Rad40(int i) const {return Radiation40.getComposante(i);};
	double get_Text(int i) const {return Text.getComposante(i);};	
	double get_Tmax() {return Text.max();};
	double get_Rmax() {return Radiation.max();};
	double get_R40max() {return Radiation40.max();};
	private:
	Array Text; // Meteonorm Temperature data [every minute]
	Array Radiation; // Meteonorm Radiation data [every minute] orientation South, on 90° oriented surface
	Array Radiation40; // Meteonorm Radiation data [every minute] orientation South, on 40° oriented surface
};

#endif
