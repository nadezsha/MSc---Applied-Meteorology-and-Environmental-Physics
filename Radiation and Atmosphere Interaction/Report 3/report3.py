import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read files
grass = []
cdry = []
sand = []
sno2 = []

sza_list = [10, 40, 70]

filename_grass = [f'3-{sza}.out' for sza in sza_list]
filename_cdry = [f'3-cdry-{sza}.out' for sza in sza_list]
filename_sand = [f'3-sand-{sza}.out' for sza in sza_list]
filename_sno2 = [f'3-sno2-{sza}.out' for sza in sza_list]

col_names = ['wavelength', 'direct horizontal irradiance', 'diffuse downward horizontal irradiance',
'diffuse upward horizontal irradiance (reflected)', 'uavgdirect', 'uavgdiffuse downward', 'uavgdiffuse upward']

for filename in filename_grass:
	file = pd.read_csv(filename, delimiter=r"\s+", names=col_names) 
	grass.append(file) 

for filename in filename_cdry:
	file = pd.read_csv(filename, delimiter=r"\s+", names=col_names) 
	cdry.append(file) 

for filename in filename_sand:
	file = pd.read_csv(filename, delimiter=r"\s+", names=col_names) 
	sand.append(file) 

for filename in filename_sno2:
	file = pd.read_csv(filename, delimiter=r"\s+", names=col_names) 
	sno2.append(file) 

# create more data columns
for i in range(0,3):
	grass[i]['actinic flux direct'] = grass[i]['uavgdirect']*4*np.pi
	cdry[i]['actinic flux direct'] = cdry[i]['uavgdirect']*4*np.pi
	sand[i]['actinic flux direct'] = sand[i]['uavgdirect']*4*np.pi
	sno2[i]['actinic flux direct'] = sno2[i]['uavgdirect']*4*np.pi
	
	grass[i]['actinic flux diffuse downward'] = grass[i]['uavgdiffuse downward']*4*np.pi
	cdry[i]['actinic flux diffuse downward'] = cdry[i]['uavgdiffuse downward']*4*np.pi
	sand[i]['actinic flux diffuse downward'] = sand[i]['uavgdiffuse downward']*4*np.pi
	sno2[i]['actinic flux diffuse downward'] = sno2[i]['uavgdiffuse downward']*4*np.pi

	grass[i]['actinic flux diffuse upward'] = grass[i]['uavgdiffuse upward']*4*np.pi
	cdry[i]['actinic flux diffuse upward'] = cdry[i]['uavgdiffuse upward']*4*np.pi
	sand[i]['actinic flux diffuse upward'] = sand[i]['uavgdiffuse upward']*4*np.pi
	sno2[i]['actinic flux diffuse upward'] = sno2[i]['uavgdiffuse upward']*4*np.pi

	grass[i]['global irradiance horizontal'] = grass[i]['direct horizontal irradiance'] + grass[i]['diffuse downward horizontal irradiance']
	cdry[i]['global irradiance horizontal'] = cdry[i]['direct horizontal irradiance'] + cdry[i]['diffuse downward horizontal irradiance']
	sand[i]['global irradiance horizontal'] = sand[i]['direct horizontal irradiance'] + sand[i]['diffuse downward horizontal irradiance']
	sno2[i]['global irradiance horizontal'] = sno2[i]['direct horizontal irradiance'] + sno2[i]['diffuse downward horizontal irradiance']

	grass[i]['actinic flux semispherical'] = grass[i]['actinic flux direct'] + grass[i]['actinic flux diffuse downward']
	cdry[i]['actinic flux semispherical'] = cdry[i]['actinic flux direct'] + cdry[i]['actinic flux diffuse downward']
	sand[i]['actinic flux semispherical'] = sand[i]['actinic flux direct'] + sand[i]['actinic flux diffuse downward']
	sno2[i]['actinic flux semispherical'] = sno2[i]['actinic flux direct'] + sno2[i]['actinic flux diffuse downward']

	#print(cdry[0]['global irradiance horizontal'])

# calculate the percentages for global irradiance, diffuse upward horizontal irradiance, actinic flux on a semispherical surface, actinic flux diffuse upward
for i in range(0,3):
	grass[i]['GHI-grass-cdry'] = (cdry[i]['global irradiance horizontal'] - grass[i]['global irradiance horizontal'])/grass[i]['global irradiance horizontal']*100
	grass[i]['GHI-grass-sand'] = (sand[i]['global irradiance horizontal'] - grass[i]['global irradiance horizontal'])/grass[i]['global irradiance horizontal']*100
	grass[i]['GHI-grass-sno2'] = (sno2[i]['global irradiance horizontal'] - grass[i]['global irradiance horizontal'])/grass[i]['global irradiance horizontal']*100
		
	grass[i]['duhi-grass-cdry'] = (cdry[i]['diffuse upward horizontal irradiance (reflected)'] - grass[i]['diffuse upward horizontal irradiance (reflected)'])/grass[i]['diffuse upward horizontal irradiance (reflected)']*100
	grass[i]['duhi-grass-sand'] = (sand[i]['diffuse upward horizontal irradiance (reflected)'] - grass[i]['diffuse upward horizontal irradiance (reflected)'])/grass[i]['diffuse upward horizontal irradiance (reflected)']*100
	grass[i]['duhi-grass-sno2'] = (sno2[i]['diffuse upward horizontal irradiance (reflected)'] - grass[i]['diffuse upward horizontal irradiance (reflected)'])/grass[i]['diffuse upward horizontal irradiance (reflected)']*100
		
	grass[i]['AF-semi-grass-cdry'] = (cdry[i]['actinic flux semispherical'] - grass[i]['actinic flux semispherical'])/grass[i]['actinic flux semispherical']*100
	grass[i]['AF-semi-grass-sand'] = (sand[i]['actinic flux semispherical'] - grass[i]['actinic flux semispherical'])/grass[i]['actinic flux semispherical']*100
	grass[i]['AF-semi-grass-sno2'] = (sno2[i]['actinic flux semispherical'] - grass[i]['actinic flux semispherical'])/grass[i]['actinic flux semispherical']*100
		
	grass[i]['afdu-grass-cdry'] = (cdry[i]['actinic flux diffuse upward'] - grass[i]['actinic flux diffuse upward'])/grass[i]['actinic flux diffuse upward']*100
	grass[i]['afdu-grass-sand'] = (sand[i]['actinic flux diffuse upward'] - grass[i]['actinic flux diffuse upward'])/grass[i]['actinic flux diffuse upward']*100
	grass[i]['afdu-grass-sno2'] = (sno2[i]['actinic flux diffuse upward'] - grass[i]['actinic flux diffuse upward'])/grass[i]['actinic flux diffuse upward']*100

# plotting the figures
for i in range(0,3):
	plt.plot(grass[i]["wavelength"], grass[i]["GHI-grass-cdry"], color ='g', label = "cdry")
	plt.plot(grass[i]["wavelength"], grass[i]["GHI-grass-sand"], color ='brown', label = "sand")
	plt.plot(grass[i]["wavelength"], grass[i]["GHI-grass-sno2"], color ='b', label = "sno2")
	plt.xlabel(" Wavelength (nm)")
	plt.ylabel("'%' differences relative to the reference (grass)")
	plt.legend()
	plt.grid()
	plt.title("global irradiance for sza = " +str(sza_list[i])+" degrees")
	plt.show()

for i in range(0,3):
	plt.plot(grass[i]["wavelength"], grass[i]["duhi-grass-cdry"], color ='g', label = "cdry")
	plt.plot(grass[i]["wavelength"], grass[i]["duhi-grass-sand"], color ='brown', label = "sand")
	plt.plot(grass[i]["wavelength"], grass[i]["duhi-grass-sno2"], color ='b', label = "sno2")
	plt.xlabel(" Wavelength (nm)")
	plt.ylabel("'%' differences relative to the reference (grass)")
	plt.legend()
	plt.grid()
	plt.title("diffuse upward horizontal irradiance (reflected) for sza = " +str(sza_list[i])+" degrees")
	plt.show()

for i in range(0,3):
	plt.plot(grass[i]["wavelength"], grass[i]["AF-semi-grass-cdry"], color ='g', label = "cdry")
	plt.plot(grass[i]["wavelength"], grass[i]["AF-semi-grass-sand"], color ='brown', label = "sand")
	plt.plot(grass[i]["wavelength"], grass[i]["AF-semi-grass-sno2"], color ='b', label = "sno2")
	plt.xlabel(" Wavelength (nm)")
	plt.ylabel("'%' differences relative to the reference (grass)")
	plt.legend()
	plt.grid()
	plt.title("actinic flux on a semispherical surface for sza = " +str(sza_list[i])+" degrees")
	plt.show()

for i in range(0,3):
	plt.plot(grass[i]["wavelength"], grass[i]["afdu-grass-cdry"], color ='g', label = "cdry")
	plt.plot(grass[i]["wavelength"], grass[i]["afdu-grass-sand"], color ='brown', label = "sand")
	plt.plot(grass[i]["wavelength"], grass[i]["afdu-grass-sno2"], color ='b', label = "sno2")
	plt.xlabel(" Wavelength (nm)")
	plt.ylabel("'%' differences relative to the reference (grass)")
	plt.legend()
	plt.grid()
	plt.title("actinic flux diffuse upward for sza = " +str(sza_list[i])+" degrees")
	plt.show()


# calculate mean albedos and plot with wavelength for all surfaces
names = ['wavelength', 'albedo']
gras = pd.read_csv('gras.dat',delimiter=r"\s+", skiprows=6, names = names)
cdry = pd.read_csv('cdry.dat',delimiter=r"\s+", skiprows=6, names = names)
sand = pd.read_csv('sand.dat',delimiter=r"\s+", skiprows=6, names = names)
sno2 = pd.read_csv('sno2.dat',delimiter=r"\s+", skiprows=6, names = names)
gras.head()

print("the mean albedo values for the grass, cdry, sand and sno2 are:")
print(gras['albedo'].mean().round(2), cdry['albedo'].mean().round(2), sand['albedo'].mean().round(2), sno2['albedo'].mean().round(2))

plt.plot(gras['wavelength'], gras['albedo'], label = 'gras', color = 'g')
plt.plot(cdry['wavelength'], cdry['albedo'], label = 'cdry', color = 'r')
plt.plot(sand['wavelength'], sand['albedo'], label = 'sand' , color = 'orange')
plt.plot(sno2['wavelength'], sno2['albedo'], label = 'sno2', color = 'b')
plt.xlabel("wavelength (nm)")
plt.ylabel("albedo")
plt.grid()
plt.legend(loc = 'best')
plt.title("albedo values for the ")
plt.show()


# plots for the direct and diffused irradiances
for i in range(0,3):
    grass[i]["direct_g_cdr"] = (cdry[i]['direct horizontal irradiance'] - grass[i]['direct horizontal irradiance'])/grass[i]['direct horizontal irradiance'] *100
    grass[i]["direct_g_snd"] = (sand[i]['direct horizontal irradiance'] - grass[i]['direct horizontal irradiance'])/grass[i]['direct horizontal irradiance'] *100
    grass[i]["direct_g_sno"] = (sno2[i]['direct horizontal irradiance'] - grass[i]['direct horizontal irradiance'])/grass[i]['direct horizontal irradiance'] *100
	
    grass[i]["diffused_g_cdr"] = (cdry[i]['diffuse downward horizontal irradiance'] - grass[i]['diffuse downward horizontal irradiance'])/grass[i]['diffuse downward horizontal irradiance'] *100
    grass[i]["diffused_g_snd"] = (sand[i]['diffuse downward horizontal irradiance'] - grass[i]['diffuse downward horizontal irradiance'])/grass[i]['diffuse downward horizontal irradiance'] *100
    grass[i]["diffused_g_sno"] = (sno2[i]['diffuse downward horizontal irradiance'] - grass[i]['diffuse downward horizontal irradiance'])/grass[i]['diffuse downward horizontal irradiance'] *100


for i in range(0,3):
	plt.plot(grass[i]["wavelength"], grass[i]["direct_g_cdr"], color ='r', label = "cdry")
	plt.plot(grass[i]["wavelength"], grass[i]["direct_g_snd"], color ='g', label = "snd")
	plt.plot(grass[i]["wavelength"], grass[i]["direct_g_sno"], color ='b', label = "sno2")
	plt.xlabel(" Wavelength (nm)")
	plt.ylabel("% differences relative to the reference (grass)")
	plt.legend()
	plt.grid()
	plt.title("direct irradiance for sza = "+str(sza_list[i])+" degrees")
	plt.show()

for i in range(0,3):
	plt.plot(grass[i]["wavelength"], grass[i]["diffused_g_cdr"], color ='r', label = "cdry")
	plt.plot(grass[i]["wavelength"], grass[i]["diffused_g_snd"], color ='g', label = "snd")
	plt.plot(grass[i]["wavelength"], grass[i]["diffused_g_sno"], color ='b', label = "sno2")
	plt.xlabel(" Wavelength (nm)")
	plt.ylabel("% differences relative to the reference (grass)")
	plt.legend()
	plt.grid()
	plt.title("diffused irradiance for sza = "+str(sza_list[i])+" degrees")
	plt.show()
