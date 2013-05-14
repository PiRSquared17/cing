#ifndef  RC_H

/* Random coil values for 15N */

static float  N15RC[] = 
{ 123.8, 118.6, 120.4, 120.2, 120.3, 108.8, 118.2, 119.9, 120.4, 121.8,
119.6, 118.7, 0.0, 119.8,  120.5, 115.7, 113.6, 119.2, 121.3, 120.3 };

/* Calibrated HN random coil values */

/*
static float  HNRC[] = 
{ 8.24, 8.32, 8.34, 8.42, 8.30, 8.33, 8.32, 8.05, 8.29, 8.16, 8.28, 8.30,
0.0, 8.32, 8.23, 8.31, 8.15, 8.03, 8.15, 8.12 };
*/

/*
static float  HARC[] = 
{ 4.432847, 4.65, 4.725179, 4.364552, 4.430244, 3.97,  4.615947, 4.193333,
4.368070, 4.402746, 4.461933, 4.806587, 4.658447, 4.405826, 4.350150,
4.504638, 4.324869, 4.086605, 4.412784, 4.339301 };


static float  CARC[] = 
{ 52.26644, 57.791772, 54.158222, 56.503798, 57.64624, 45.486533,
55.660394, 61.206185, 56.243301, 54.957697, 55.367, 53.30902, 63.066266,
56.062813, 56.24026, 58.144025, 62.54202, 62.512466, 56.208648, 57.33818
};

static float  CBRC[] = 
{ 19.0, 41.8, 40.8, 29.7, 39.3, 0.0, 32.0, 37.5, 32.3,  41.9, 32.8, 39.0,
31.7, 30.1, 30.3, 62.7, 68.1, 31.7,  28.3, 38.7 }; 

static float  CORC[] =
{ 177.1, 175.1, 177.2, 176.1, 175.8, 173.6, 175.1,  176.8, 176.5, 177.1,
175.5, 175.5, 176.0, 176.3,  176.5, 173.7, 175.2, 177.1, 175.8, 175.7 };
*/

/* Revised values from 2000 Methods In Enzymology Paper (Wishart and Case) */
static float  HNRC[] = 
{ 8.24, 8.32, 8.34, 8.42, 8.30, 8.33, 8.42, 8.00, 8.29, 8.16, 8.28, 8.40,
0.0, 8.32, 8.23, 8.31, 8.15, 8.03, 8.25, 8.12 };


/* Calibrated HA random coil values for statistical method */

static float  HARC[] = 
{ 4.32, 4.55, 4.64, 4.35, 4.62, 3.96,  4.73, 4.17,
4.32, 4.34, 4.48, 4.74, 4.42, 4.34, 4.34,
4.47, 4.35, 4.12, 4.66, 4.55 };

/* Calibrated CA random coil values for statistical method */

static float  CARC[] = 
{ 52.5, 58.2, 54.2, 56.6, 57.7, 45.1,
55.0, 61.1, 56.2, 55.1, 55.4, 53.1, 63.3,
55.7, 56.0, 58.3, 61.8, 62.2, 57.5, 57.9
};

static float  CBRC[] = 
{ 19.1, 28.0, 41.1, 29.9, 39.6, 0.0, 29.0, 38.8, 33.1,  42.4, 32.9, 38.9,
32.1, 29.4, 30.9, 63.8, 69.8, 32.9,  29.6, 37.8 }; 

static float  CORC[] =
{ 177.8, 174.6, 176.3, 176.6, 175.8, 174.9, 174.1,  176.4, 176.6, 177.6,
176.3, 175.2, 177.3, 176.0,  176.3, 174.6, 174.7, 176.3, 176.1, 175.9 };

static float HBRC[] =
{1.39, 2.93, 2.72, 2.06, 3.14, 0.00, 3.29, 1.87, 1.84, 1.62,
 2.11, 2.83, 2.29, 2.12, 1.86, 3.89, 4.24, 2.08, 3.29, 3.03};

static float HSRC[NHATOMS][20] =
{
//AA,,    Ala,Cys (ox), Asp, Glu, Phe, Gly, His, Ile, Lys, Leu, Met, Asn, Pro, Gln, Arg, Ser, Thr, Val, Trp, Tyr,
/*NH,,*/ 8.24,    8.32,8.34,8.42, 8.3,8.33,8.42,   8,8.29,8.16,8.28, 8.4,   0,8.32,8.23,8.31,8.15,8.03,8.25,8.12,
/*AH,,*/ 4.32,    4.55,4.64,4.35,4.62, 0.0,4.73,4.17,4.32,4.34,4.48,4.74,4.42,4.34,4.34,4.47,4.35,4.12,4.66,4.55,
/*HA2,,*/   0,       0,   0,   0,   0,3.96,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HA3,,*/   0,       0,	  0,   0,   0,3.96,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HB,,*/    0,       0,   0,   0,   0,   0,   0,1.87,   0,   0,   0,   0,   0,   0,   0,   0,4.24,2.08,   0,   0,
/*HB1,,*/1.39,       0,	  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HB2,,*/1.39,    2.93,2.72,2.06,3.14,   0,3.29,   0,1.84,1.62,2.11,2.83,2.29,2.12,1.86,3.89,   0,   0,3.29,3.03,
/*HB3,,*/1.39,    2.93,2.65,1.96,3.04,   0,3.16,   0,1.75,1.62,2.01,2.75,1.94,1.99,1.76,3.87,   0,   0,3.27,2.98,
/*HD1,,*/   0,       0,   0,   0,7.28,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,7.27,7.14,
/*HD11,,*/  0,       0,   0,   0,   0,   0,   0,0.86,   0,0.92,   0,   0,   0,   0,   0,   0,   0,   0,   0   ,0,
/*HD12,,*/  0,       0,   0,   0,   0,   0,   0,0.86,   0,0.92,   0,   0,   0,   0,   0,   0,   0,   0,   0   ,0,
/*HD13,,*/  0,       0,   0,   0,   0,   0,   0,0.86,   0,0.92,   0,   0,   0,   0,   0,   0,   0,   0,   0   ,0,
/*HD2,,*/   0,       0,   0,   0,7.28,   0,8.58,   0,1.68,   0,   0,   0,3.63,   0, 3.2,   0,   0,   0,   0,7.14,
/*HD21,,*/  0,       0,   0,   0,   0,   0,   0,   0,   0,0.87,   0,7.59,   0,   0,   0,   0,   0,   0,   0,   0,
/*HD22,,*/  0,       0,   0,   0,   0,   0,   0,   0,   0,0.87,   0,6.91,   0,   0,   0,   0,   0,   0,   0,   0,
/*HD23,,*/  0,       0,   0,   0,   0,   0,   0,   0,   0,0.87,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HD3,,*/   0,		 0,   0,   0,   0,   0,   0,   0,1.68,   0,   0,   0,3.63,   0, 3.2,   0,   0,   0,   0,   0,
/*HE,,*/    0,       0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,8.07,   0,   0,   0,   0,   0,
/*HE1,,*/   0,       0,   0,   0,7.38,   0,7.29,   0,   0,   0, 2.1,   0,   0,   0,   0,   0,   0,   0,10.09,6.84,
/*HE2,,*/   0,       0,   0,   0,7.38,   0,   0,   0,2.99,   0, 2.1,   0,   0,   0,   0,   0,   0,   0,   0,6.84,
/*HE21,,*/  0,       0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,7.52,   0,   0,   0,   0,   0,   0,
/*HE22,,*/  0,       0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,6.85,   0,   0,   0,   0,   0,   0,
/*HE3,,*/   0,       0,   0,   0,   0,   0,   0,   0,2.99,   0, 2.1,   0,   0,   0,   0,   0,   0,   0, 7.5,   0,
/*HG,,*/    0,       0,   0,   0,   0,   0,   0,   0,   0,1.59,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HG1,,*/   0,       0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HG11,,*/  0,       0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,0.94,   0,   0,
/*HG12,,*/  0,       0,   0,   0,   0,   0,   0,1.45,   0,   0,   0,   0,   0,   0,   0,   0,   0,0.94,   0,   0,
/*HG13,,*/  0,       0,   0,   0,   0,   0,   0,1.16,   0,   0,   0,   0,   0,   0,   0,   0,   0,0.94,   0,   0,
/*HG2,,*/   0,		 0,   0,2.31,   0,   0,   0,   0,1.44,   0, 2.6,   0,2.02,2.36,1.63,   0,   0,   0,   0,   0,
/*HG21,,*/  0,		 0,   0,   0,   0,   0,   0,0.91,   0,   0,   0,   0,   0,   0,   0,   0,1.21,0.93,   0,   0,
/*HG22,,*/  0,		 0,   0,   0,   0,   0,   0,0.91,   0,   0,   0,   0,   0,   0,   0,   0,1.21,0.93,   0,   0,
/*HG23,,*/  0,		 0,   0,   0,   0,   0,   0,0.91,   0,   0,   0,   0,   0,   0,   0,   0,1.21,0.93,   0,   0,
/*HG3,,*/   0,		 0,   0,2.31,   0,   0,   0,   0,1.44,   0,2.54,   0,2.02,2.36,1.63,   0,   0,   0,   0,   0,
/*HH,,*/    0,		 0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HH11,,*/  0,		 0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HH12,,*/  0,		 0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HH2,,*/   0,		 0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,7.18,   0,
/*HH21,,*/  0,		 0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HH22,,*/  0,		 0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HZ,,*/    0,		 0,   0,   0,7.32,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HZ1,,*/   0,		 0,   0,   0,   0,   0,   0,   0,7.81,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
/*HZ2,,*/   0,		 0,   0,   0,   0,   0,   0,   0,7.81,   0,   0,   0,   0,   0,   0,   0,   0,   0,7.65,   0,
/*HZ3,,*/   0,		 0,   0,   0,   0,   0,   0,   0,7.81,   0,   0,   0,   0,   0,   0,   0,   0,   0,7.25,   0,
};

/* ADDNEW */
#define  RC_H

#endif
