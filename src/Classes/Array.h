#ifndef ARRAY_H
#define ARRAY_H
#include <iostream>
#include <vector>
#include <iomanip>
#include <fstream>
#include <iterator> 
#include <cmath>  
using namespace std;

class Array{

	public:
	Array();
	Array(const Array&);	//Constructor
	Array(int taille); //Constructor 
	Array(int taille, const vector<double>& VecteurInit); //Constructor with vector argument
	Array(string fileName);// Constructor from a file, determines the length of the array from the number of lines in the file
	void showArray();
	double getComposante(int i) const {return array.at(i);};
	void setComposante(int i,double value) { array[i]=value; };
	int getSize() const {return size;};	
	double abs_max(); //returns the element of the array with the largest absolute value
	double max(); //returns the largest element of the array
	
	//Operator orverloading
	Array operator+(const Array & b) const;
	void operator+=(const Array& b);
	Array operator*(double lambda) const;
    Array operator*(const Array & a) const;
	//Friend functions
	friend Array operator*(double lambda, const Array& b);
	friend ostream& operator<<(ostream& os, const Array& ToPrint);

	private:

	int size;
	vector<double> array;

};

#endif
