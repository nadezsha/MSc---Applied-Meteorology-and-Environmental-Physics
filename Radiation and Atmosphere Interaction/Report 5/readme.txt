how to run the model : 
uvspec <5.inp> 5.out

5.out contains: wavelength, direct horizontal irradiance, diffuse downward horizontal irradiance,diffuse upward horizontal irradiance (reflected), uavgdirect, 
uavgdiffuse downward,uavgdiffuse upward 





Homework: 

run the model for sza=20, 50 and 80 degrees. 
change wc-set-tau from:
0 to 2 step 0.5
2 to 5 step 1
5 to 20 step 5

Calculate 
actinic flux 2ð = (uavgdirect + uavgdiffuse downward)  * 4* pi
global irradiance on a horizontal surface (looking upwards, like a pyranometer) = direct + diffuse downward

Integrate and calculate the sums in UVB (300-320), UVA (320-400), VIS (400-700) and IR (700-1100)

Compare results and make a presentation about how all these radiative quantities (direct, diffuse down (BUT NOT UP!), total for both irradiance and actinic flux 2ð ) and are affected by the increase of cloud optical depth.



IMPORTANT NOTE: for multiple runs, check file "bat.bat"



