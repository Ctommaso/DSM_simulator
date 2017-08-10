#include "Weather.h"

// Public Methods

// Constructor
Weather::Weather(string filename_Text, string filename_Radiation, string filename_Radiation40) 
{
	Array TEXT(filename_Text), RADIATION(filename_Radiation), RADIATION40(filename_Radiation40);
	Text=TEXT;
	Radiation=RADIATION;
	Radiation40=RADIATION40;
}
