#include "Array.h"

// Public Methods
Array::Array(){}

//Constructor without parameters: contructs an array of zeros
Array::Array(int taille) 
{
	size=taille;
	for(int i(0); i<size;i++)
	{
		array.push_back(0);
	}
}

//Constructor
Array::Array(const Array& A)
{
	size=A.getSize();
	for(int i=0; i<size;i++)
	{
		array.push_back(A.getComposante(i));
	}
}	

//Constructor with parameters
Array::Array(int taille, const vector<double>& VecteurInit) 
{
	size=taille;
	for(int i=0; i<size;i++)
	{
		array.push_back(VecteurInit[i]);
	}
	
}

//Contructor from a file
Array::Array(string fileName)
{
	int compteur(0);
	
	ifstream infile;
   	infile.open(fileName.c_str());

	double element;
	while(true)
	{
		infile >> element;
		if(infile.eof()) break;
		array.push_back(element);
		compteur++;
	}
	infile.close();
	size=compteur;
}

//Displays the Array
void Array::showArray() 
{
	for(int i=0; i<size; i++)
	{
		cout<<array[i]<<" ";
	}
	cout<<endl;
}

//Overload of the operator +
Array Array::operator+(const Array& b) const 
{
	vector<double> sum(size);

	for(int i=0; i<size; i++)
	{
		sum[i]=array[i]+b.getComposante(i);
	}
	Array Sum(size,sum);
	return Sum;
}

//Overload of the operator +=
void Array::operator+=(const Array& b)
{
	for(int i=0; i<size; i++)
	{
		array[i] += b.getComposante(i);
	}
}

//Overload of the scalar multiplication
Array Array::operator*(double lambda) const 
{
	vector<double> product(size);
	for(int i=0; i<size; i++)
	{
		product[i]=lambda*array[i];
	}
	Array Product(size,product);
	return Product;
}

//Elementwise multiplication
Array Array::operator*(const Array & a) const 
{
    vector<double> product(size);
    for(int i=0; i<size; i++)
    {
        product[i]=a.getComposante(i)*array[i];
    }
    Array Product(size,product);
    return Product;
}

//Friend Function, commutativity of the scalar multiplication
Array operator*(double lambda, const Array& b)
{
	return b*lambda;
}

//Overload of << 
ostream& operator<<(ostream& os, const Array& ToPrint)
{	
	for(int i=0; i<ToPrint.getSize(); i++)
	{
		os<<ToPrint.getComposante(i)<<" ";
	}
    return os;
}

//Returns the element of the array with the largest absolute value
double Array::abs_max()
{
	double max_temp(0);
	double max (0);
	for(unsigned int i(0); i<array.size();i++)
	{
		max_temp=std::abs(array[i]);
		if(max_temp>max)
		{
			max=max_temp;
		}
	}
	return max;
}

//Returns the largest element of the array
double Array::max()
{
	double max(array[0]),temp(0);
	for(unsigned int i(0); i<array.size();i++)
	{
		temp=array[i];
		if(temp>max)
		{
			max=temp;
		}
	}
	return max;
}
