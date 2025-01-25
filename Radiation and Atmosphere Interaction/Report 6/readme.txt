how to run the model : 
uvspec <6.inp> 6.out

6.out contains: wavelength, direct horizontal irradiance, diffuse downward horizontal irradiance,diffuse upward horizontal irradiance (reflected), uavgdirect, 
uavgdiffuse downward,uavgdiffuse upward 





Homework: 


PART 1:
For a low cloud: 
wc-set-tau=5
Note that in WC6.dat, the cloud lies at 1km and has a geometrical depth of 1km
change zout from 0 to 8 step 1km


run the model for sza=20 and 70 degrees. 
Calculate 
actinic flux 2ð = (uavgdirect + uavgdiffuse downward)  * 4* pi
global irradiance on a horizontal surface (looking upwards, like a pyranometer) = direct + diffuse downward
Integrate and calculate the sums in UVB (300-320), UVA (320-400), VIS (400-700) and IR (700-1100)

Do the same for wc-set-tau=0



Compare results and make a presentation about how all these radiative quantities (direct, diffuse down, total for both irradiance and actinic flux 2ð, are changing with height and what is the effect of cloudiness.




PART 2:
For a HIGH cloud: 
wc-set-tau=2
Change WC6.dat, to place the cloud lies at 6km and has a geometrical depth of 1km
change zout from 0 to 8 step 1km


run the model for sza=20 and 70 degrees. 
Calculate 
actinic flux 2ð = (uavgdirect + uavgdiffuse downward)  * 4* pi
global irradiance on a horizontal surface (looking upwards, like a pyranometer) = direct + diffuse downward

Integrate and calculate the sums in UVB (300-320), UVA (320-400), VIS (400-700) and IR (700-11000)
Do the same for wc-set-tau=0


Compare results and make a presentation about how all these radiative quantities (direct, diffuse down, total for both irradiance and actinic flux 2ð, are changing with height and what is the effect of cloudiness.


IMPORTANT NOTE: for multiple runs, check file "bat.bat"



