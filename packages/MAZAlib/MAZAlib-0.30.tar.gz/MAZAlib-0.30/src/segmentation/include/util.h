/*
*	Copyrighted, Research Foundation of SUNY, 1998
*/
#ifndef _UTIL_H_
#define _UTIL_H_


#include <fstream>
#include <iostream>
#include <iomanip>
#include <math.h>
#include <cstdlib>
#include <type_traits>


#define EPS_THINY 0.0000001

//using namespace std;

#include <algorithm>


//#include "mystring.h"  // string class
#include <string>




///////////////////////////////////////


#ifdef MPI

#include "mpi_util.h"

#else

inline void gsync()    {}
inline int  mynode()   { return 0; }
inline int  numnodes() { return 1; }

#define PRINT_NODE_NO
#define EVERY_NODE_BEGIN 
#define EVERY_NODE_END 

#endif // MPI


//#define REPEAT(i,X)  { for (int _x_=0; _x_<i; _x_++ ) X;}
//#define BLANK_LINE   { cout << endl;}


void print_prologue(int=1);
void print_epilogue();

inline void announce(const std::string& msg1,
		     const std::string& msg2="",
                     const std::string& msg3="")
{
#ifdef MPI
    if (mynode()!=ROOTNODE) return;
#endif
	std::cerr << msg1; std::cerr << msg2; std::cerr << msg3; std::cerr.flush();
	std::cout << msg1; std::cout << msg2; std::cout << msg3; std::cout.flush();
}

inline void test(const std::string& where) {
#ifdef MPI
    PRINT_NODE_NO
#endif
    //announce("\n\nWarning in ",where," should be tested further.\n\n");
	std::cerr.flush(); std::cout.flush();
}

inline void todo(const std::string& message, const std::string& where="") {
#ifdef MPI
    PRINT_NODE_NO
#endif
    announce("\n\nTO DO: ",message);    
    announce(" ",where,"\n\n");    
	std::cerr.flush(); std::cout.flush();
}

inline void warning(const std::string& message, const char* where="") {
#ifdef MPI
    PRINT_NODE_NO
#endif
    if (where=="") announce("\n\nWarning: ");    
    else announce("\n\nWarning in ",where,": ");
    announce(message,"\n\n");    
	std::cerr.flush(); std::cout.flush();
}

static int ERROR_;

inline void file_error(const std::string& filename, const std::string& where) {
#ifdef MPI
    PRINT_NODE_NO
#endif
    if (where=="") announce("\n\nError: ");
    else announce("\n\nError in ",where,": ");
    announce("cannot open file ",filename,"\n\n");
	std::cerr.flush(); std::cout.flush();
    ERROR_=1;
    exit(ERROR_);
}

inline void not_implemented(const std::string& name) {
#ifdef MPI
    PRINT_NODE_NO
#endif
    announce("\n\nERROR: ",name," is not implemented yet.\n\n");
	std::cerr.flush(); std::cout.flush();
    ERROR_=2;
    exit(ERROR_);
}

inline void not_parallel(const std::string name) {
#ifdef MPI
    PRINT_NODE_NO
#endif
    announce("\n\nERROR: ",name," is not in parallel yet.\n\n");
	std::cerr.flush(); std::cout.flush();
    ERROR_=3;
    exit(ERROR_);
}

inline void error(const std::string& message, const std::string& where) {
#ifdef MPI
    PRINT_NODE_NO
#endif
    if (where=="") announce("\n\nError: ");
    else announce("\n\nError in ",where,": ");
    announce(message,"\n\n");
	std::cerr.flush(); std::cout.flush();
    ERROR_=4;
    exit(ERROR_);
}


// Some mathematical functions

inline int ipow(int n, int m)
{
    int i,power=1;
    if ( m < 0 ) {
	std::cerr << "\n\nipow()  m must be non-negative.\n";
	exit(1);
    }
    if (m==0) return 1;
    for(i=1;i<=m;i++) {
	power=power*n;
    }
    return power;
}
inline int iround(double x)
{
    int ix=(int)(floor(x));
    if (x-ix >=0.5) return ix+1;
    else return ix;
}

inline int kroneker_delta(int i, int j)
{
    return (i==j);
}

inline double linear_interpolate(const double x,
                                 const double x0, const double x1,
				 const double v0, const double v1)
{
    double weight=(x-x0)/(x1-x0);
    return (1-weight)*v0+weight*v1;
}

//////////////////////////////////////////////////


template <class T> 
void ask(const char* msg, T& input)
{
#ifdef MPI
    if (mynode()==ROOTNODE)
#endif
    {
		std::cerr << msg << ": ";
		std::cin  >> input;
		std::cerr << input << std::endl;
		std::cout << msg << ": " << input << std::endl;
	char ignore[128];
	std::cin.getline(ignore,128);
    }
#ifdef MPI
//  MPI_COMM_WORLD.Bcast(&input,1,mpi_type(input),ROOTNODE);
    MPI_Bcast(&input,1,mpi_type(input),ROOTNODE,MPI_COMM_WORLD);
#endif
}


inline void ask(const char* msg, std::string& input)
{
    char tmp[128];
#ifdef MPI
    if (mynode()==ROOTNODE) 
#endif
    {
		std::cerr << msg << ": ";
		std::cin.getline(tmp,128);
		std::cerr << tmp << std::endl;
		std::cout << msg << ": " << tmp << std::endl;
    }
#ifdef MPI
    MPI_Bcast(tmp,128,MPI_CHAR,ROOTNODE,MPI_COMM_WORLD);
#endif
    input = std::string(tmp);
}

template <class T1, class T2> 
void ask(const char* msg, T1& input1, T2& input2)
{
#ifdef MPI
    if (mynode()==ROOTNODE)
#endif
    {
		std::cerr << msg << ": ";
		std::cin  >> input1 >> input2;
		std::cerr << input1 << " " << input2 << std::endl;
		std::cout << msg << ": " << input1 << " " << input2 << std::endl;
	char ignore[128];
	std::cin.getline(ignore,128);
    }
#ifdef MPI
//  MPI_COMM_WORLD.Bcast(&input1,1,mpi_type(input1),ROOTNODE);
//  MPI_COMM_WORLD.Bcast(&input2,1,mpi_type(input2),ROOTNODE);
    MPI_Bcast(&input1,1,mpi_type(input1),ROOTNODE,MPI_COMM_WORLD);
    MPI_Bcast(&input2,1,mpi_type(input2),ROOTNODE,MPI_COMM_WORLD);
#endif
}    


template <class T1, class T2, class T3>
void ask(const char* msg, T1& input1, T2& input2, T3& input3)
{
#ifdef MPI
    if (mynode()==ROOTNODE) 
#endif
    {    
		std::cerr << msg << ": ";
		std::cin  >> input1 >> input2 >> input3;
		std::cerr << input1 << " " << input2 << " " << input3 << std::endl;
		std::cout << msg << ": "  << input1 << " "
             << input2 << " "<< input3 << std::endl;
	char ignore[128];
	std::cin.getline(ignore,128);
    }
#ifdef MPI
//  MPI_COMM_WORLD.Bcast(&input1,1,mpi_type(input1),ROOTNODE);
//  MPI_COMM_WORLD.Bcast(&input2,1,mpi_type(input2),ROOTNODE);
//  MPI_COMM_WORLD.Bcast(&input3,1,mpi_type(input3),ROOTNODE);
    MPI_Bcast(&input1,1,mpi_type(input1),ROOTNODE,MPI_COMM_WORLD);
    MPI_Bcast(&input2,1,mpi_type(input2),ROOTNODE,MPI_COMM_WORLD);
    MPI_Bcast(&input3,1,mpi_type(input3),ROOTNODE,MPI_COMM_WORLD);
#endif
}


template <class T> 
inline void ask(const std::string& msg, T& input)
{
  ask(msg.c_str(),input);
}


template <class T1, class T2> 
inline void ask(const std::string& msg, T1& input1, T2& input2)
{
  ask(msg.c_str(),input1,input2);
}

    
template <class T1, class T2, class T3>
inline void ask(const std::string& msg, T1& input1, T2& input2, T3& input3)
{
  ask(msg.c_str(),input1,input2,input3);
}



///////////////////////////////////////////////////////////////

typedef unsigned char uc;

const  uc     uc_ext_value =  255;
const  int    i_ext_value  = 1<<31;
const  float  f_ext_value  = -128.0;
const  double d_ext_value  = -128.0;
inline uc     ext_value(const uc)     { return uc_ext_value;}
inline int    ext_value(const int)    { return i_ext_value; }
inline float  ext_value(const float)  { return f_ext_value; }
inline double ext_value(const double) { return d_ext_value; }

///////////////////////////////////////////////////////////////


// Statistical functions

#if __GNUC__ >= 3
template <class Iterator>
double mean(Iterator begin, Iterator end)
{
    double s=0.0;
    typedef typename Iterator::value_type T;
    const T ext_v=ext_value(T(0));
    int n=0;
    Iterator p=begin;
    while (p != end) {
	if (*p != ext_v) {
            s += *p; ++n;
        }
        ++p;
    }
    return (s/n);
}
#else
template <class Iterator>
double mean(Iterator begin, Iterator end)
{
    double s=0.0;
	size_t n=0;
	typedef const std::common_type<int, double>::type T;
	T ext_v=ext_value(T(0));
    Iterator p=begin;
    while (p != end) {
		if (*p != ext_v) {
            s += *p;n++; 
		}
        ++p;
    }
    return (s/n);
}
template <class T>
double mean(const T* begin, const T* end)
{
    double s=0.0;
    const T ext_v=ext_value(T(0));
    size_t n=0;
    const T *p=begin;
    while (p != end) {
	if (*p != ext_v) {
            s += *p; ++n;
        }
        ++p;
    }
    return (s/n);
}
#endif

#if __GNUC__ >= 3
template <class Iterator>
double variance(Iterator begin, Iterator end, const double mean)
// corrected two-pass algorithm, see pp. 613 of NR in C
{
    double s1=0.0, s2=0.0;
    typedef typename Iterator::value_type T;
    T ext_v=ext_value(T(0));    
    register double dev;
    Iterator p=begin;
    int n=0;
    while (p != end) {
	if ((dev=*p++) == ext_v) continue;
	dev -= mean;
	s1 +=dev*dev;
	s2 +=dev;
	++n;
    }
    return (s1-s2*s2/n)/(n-1);
}
#else
template <class T>
double variance(const T* begin, const T* end, const double mean)
// corrected two-pass algorithm, see pp. 613 of NR in C
{
    double s1=0.0, s2=0.0;
    T ext_v=ext_value(T(0));    
    register double dev;
    const T* p=begin;
    int n=0;
    while (p != end) {
	if ((dev=*p++) == ext_v) continue;
	dev -= mean;
	s1 +=dev*dev;
	s2 +=dev;
	++n;
    }
    return (s1-s2*s2/n)/(n-1);
}
#endif

template <class Iterator>
inline double variance(Iterator begin, Iterator end) {
//template <class T>
//inline double variance(const T* begin, const T* end) {
    double mean=::mean(begin,end);
	double s1=0.0, s2=0.0;
    typedef typename Iterator::value_type T;
    T ext_v=ext_value(T(0));    
    register double dev;
    Iterator p=begin;
    long long n=0;
    while (p != end) {
	if ((dev=*p++) == ext_v) continue;
	dev -= mean;
	s1 +=dev*dev;
	s2 +=dev;
	++n;
    }
    return (s1-s2*s2/n)/(n-1);
}

	template <class Iterator, class T>
	void minmax(Iterator begin, Iterator end, T &min, T &max)
		//template <class T>
		//void minmax(const T *begin, const T *end, T &min, T &max)
	{
		max = T(-1.0e8);
		min = T(1.0e8);
		const T ext_v = ext_value(T(0));
		Iterator pp = begin;
		while (pp != end)
		{
			if (*pp != ext_v) {
				if (*pp > max) max = *pp;
				else if (*pp < min) min = *pp;
			}
			pp++;
		}
	}


template <class T>
inline void stats(const T* begin, const T* end,
		  double& mean, double& var) {
    mean=::mean<T>(begin,end);
    var=::variance<T>(begin,end);
}


template <class Iterator, class T>
void stats(Iterator first, Iterator last, 
	   T& min, T& max, double& mean, double& var)
//template <class T>
//void stats(const T* first, const T* last, 
//	   T& min, T& max, double& mean, double& var) 
{
    ::minmax(first,last,min,max);
    mean=::mean(first,last);
	
    var=::variance(first,last);
}

template <class Iterator, class T>
void stats_p(Iterator begin, Iterator end, 
	     T& min, T& max, double& mean, double& var) {
//template <class T>
//void stats_p(const T* begin, const T* end, 
//	     T& min, T& max, double& mean, double& var) {
    stats(begin,end,min,max,mean,var);
  //  if (mynode()==0) {
		//std::cout << std::endl;
  //      std::cout << "Minimum is "  << min  << std::endl
  //           << "Maximum is "  << max  << std::endl
  //           << "Mean is "     << mean << std::endl
  //           << "Variance is " << var  << std::endl << std::endl;
  //  }
}


template <class T>
void normalize(T* first, T* end,
	       const double target_mean, const double target_var,
	       const double mean, const double var)
{
    T* pt=first;
    double c=sqrt(target_var/var);
    double a=T(target_mean-sqrt(target_var/var)*mean);
    while (pt != end) {
	*pt = *pt*c+a;
	++pt;
    }
}

template <class T>
inline void normalize(T* begin, T* end, const double target_mean,
                      const double target_var)
{
    double mean=::mean(begin,end);
    double var=::variance(begin,end,mean);
    normalize(begin,end,target_mean,target_var,mean,var);
}

    
////////////////////////////////////////////////////////////////

// modified from numerical recipes

template <class T>
int locate(const T& x, const T* table, const int n)
{
    int jl = -1;
    int ju = n;
    int jm;
    
    int ascnd=(table[n-1] > table[0]); // ascending or descending

    while (ju-jl > 1) {
	jm=(ju+jl) >> 1;
	if (x >= table[jm] == ascnd)
	    jl=jm;
	else
	    ju=jm;
    }
    return jl;
}
/*
template <class T>
int count(const T* begin, const T* end)
{
    return end-begin;
}
*/


// sort the arryas array1 and array2 according to the order of array1
template <class T1, class T2>
void sort(T1* array1, T2* array2, const int left, const int right)// right is inclusive
{
    int i, last;
    if (left >= right) return;
    
    iter_swap(array1+left,array1+(left+right)/2);
    iter_swap(array2+left,array2+(left+right)/2);    
    last=left;
    for(i=left+1;i<=right;i++) {
	if(array1[i] < array1[left])  {
	    ++last;
	    iter_swap(array1+last,array1+i);
	    iter_swap(array2+last,array2+i);
	}
    }
    iter_swap(array1+left,array1+last);
    iter_swap(array2+left,array2+last);
    sort(array1,array2,left,last-1);
    sort(array1,array2,last+1,right);
}


/////////////////////////////////////////////////////////////////

// Input & output related

template <class T>
inline void dump(const std::string& fn, const T* v, const size_t size) {
	std::string fname("inline void dump(const string&, const T*, const size_t)");
	std::ofstream file(fn.c_str());
    if (file.fail()) file_error(fn,fname);
    file.write((const char*)v,int(size)*sizeof(T));    
    file.close();
}

template <class T>
inline void read(T* v, const int size, const std::string& fn) {
    ::read(v,size,fn,0);
}


template <class Iterator>
void print(Iterator begin, Iterator end, std::ostream& os,
	   int how_many_in_a_row)
//template <class T>
//void print(const T* begin, const T* end, ostream& os,
//	   int how_many_in_a_row)
{
    int n=0;
    Iterator pv=begin;
    while(pv != end) {
	os << std::setw(12) << std::setprecision(6) << *pv++ << " " ;
        ++n;
        if (n==how_many_in_a_row) {
            n=0;
            os << std::endl;
        }
    }
    if (n>0) os << std::endl;
}

inline void print(const uc* begin, const uc* end, std::ostream& os,
                  int how_many_in_a_row)
{
    int n=0;
    const uc* pv=begin;
    while(pv != end) {
	os << std::setw(12) << std::setprecision(6) << int(*pv) << " " ;
        ++n;++pv;
        if (n==how_many_in_a_row) {
            n=0;
            os << std::endl;
        }
    }
    if (n>0) os << std::endl;
}

template <class T>
void read(T* v, const int length, const std::string& fn, const int offset)
{
	std::string fname("void read(T*, const int, const string&, const int)");
	std::ifstream file(fn);
    if (file.fail()) file_error(fn,fname);
    if (offset > 0) file.seekg(offset*sizeof(T));
    file.read((char*)v,length*sizeof(T));
    file.close();
}


/////////////////////////////////////////////////////////////////////

// Other functions


template <class Iterator, class T>
void convert(Iterator first, Iterator last, T *converted)
//template <class T1, class T2>
//void convert(const T1* first, const T1* last, T2* converted)
{
    Iterator pt = first;
    while( pt != last ) *converted++ = static_cast<T>(*pt++);
}

template <class T>
void copy(T* begin, const T* end, const int size, const int stride)
{
    T* pto=begin;
    const T* pfrom=end;
    for (int i=0;i<size;i++) {
	*pto = *pfrom;
	pto++;
	pfrom+=stride;
    }
}

template <class Iterator, class T>
void scale(Iterator begin, Iterator end, const T target_low, 
	   const T target_high, const T min, const T max)
//template <class T>
//void scale(T* begin, T* end, const T target_low, const T target_high,
//	   const T min, const T max)
{
    Iterator p=begin;
    T m=T((target_high-target_low)/(max-min));
    T s=T((target_low*max-target_high*min)/(max-min));
    T ext_v=ext_value(T(0));
    while (p !=end) {
	if ( *p != ext_v ) *p = (*p)*m+s;
	++p;
    }
}


/////////////////////////////////////

#endif // _UTIL_H_
