

how to run the model : uvspec <1.inp> 1.out
1.out contains: wavelength, direct horizontal irradiance, diffuse downward horizontal irradiance,
diffuse upward horizontal irradiance (reflected), uavg1, uavg2, uavg....
uavg: proportional to actinic flux (the radiation that a shpere receives). 
actinic flux = uavg * 4* pi


global irradiance on a horizontal surface (looking upwards, like a pyranometer) =
 direct + diffuse downward


Run the model once. Take the output file.
Make a figure of the direct, diffuse and global irradiance
Make a figure of the global and the extraterrestrial irradiance. 
For global irradiance, integrate and calculate the sums in SW (290-4000), UVB (290-320), 
UVA (320-400), VIS (400-700) and IR (700-4000)



Homework: 
run the model for sza=0, 20, 40,  60,  80 degrees. 
calculate global and integrate again as before but for all three radiation 
components (direct, diffuse, global).
Calculate the direct/global and diffuse/global ratios.
Make a figure with these ratios for all these integrals as function of the solar zenith angle 

IMPORTANT NOTE: for multiple runs, check file "bat.bat"