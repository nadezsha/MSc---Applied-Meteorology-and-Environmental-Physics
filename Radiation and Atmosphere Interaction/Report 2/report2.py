import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the files
two_str = []
four_str = []
eight_str = []
sixteen_str = []

sza_list = [10, 30, 40, 60, 80, 85]

filename_2str = [f'2a_{sza}.out' for sza in sza_list]
filename_4str = [f'2b_4str_{sza}.out' for sza in sza_list]
filename_8str = [f'2b_8str_{sza}.out' for sza in sza_list]
filename_16str = [f'2b_16str_{sza}.out' for sza in sza_list]

col_names_2str = ['Wavelength', 'Direct', 'Diffuse_Down', 'Diffuse_Up', 'uavg']
col_names_other_str = ['Wavelength', 'Direct', 'Diffuse_Down', 'Diffuse_Up', 'uavg_direct', 'uavg_diffuse_down', 'uavg_diffuse_up']

for filename in filename_2str:
	file = pd.read_csv(filename, delimiter=r"\s+", names=col_names_2str) 
	two_str.append(file) 

for filename in filename_4str:
	file = pd.read_csv(filename, delimiter=r"\s+", names=col_names_other_str) 
	four_str.append(file) 

for filename in filename_8str:
	file = pd.read_csv(filename, delimiter=r"\s+", names=col_names_other_str) 
	eight_str.append(file) 

for filename in filename_16str:
	file = pd.read_csv(filename, delimiter=r"\s+", names=col_names_other_str) 
	sixteen_str.append(file) 

'''
Now two_str is a list containing 6 DataFrames. Every DataFrame contains values for a different zenith angle.
The other lists accordingly.
'''

for i in range(0,6):
	two_str[i]['Actinic_flux'] = two_str[i]['uavg']*4*np.pi
	two_str[i]['Global'] = two_str[i]['Direct'] + two_str[i]['Diffuse_Down']

#print(two_str[0])
#print(four_str)

for i in range(0,6):
	four_str[i]['Actinic_flux'] = (four_str[i]['uavg_direct']+four_str[i]['uavg_diffuse_down'])*4*np.pi
	eight_str[i]['Actinic_flux'] = (eight_str[i]['uavg_direct']+eight_str[i]['uavg_diffuse_down'])*4*np.pi
	sixteen_str[i]['Actinic_flux'] = (sixteen_str[i]['uavg_direct']+sixteen_str[i]['uavg_diffuse_down'])*4*np.pi

	four_str[i]['Global'] = four_str[i]['Direct'] + four_str[i]['Diffuse_Down']
	eight_str[i]['Global'] = eight_str[i]['Direct'] + eight_str[i]['Diffuse_Down']
	sixteen_str[i]['Global'] = sixteen_str[i]['Direct'] + sixteen_str[i]['Diffuse_Down']

#print(four_str[0])

for i in range(0,6):
	sixteen_str[i]["Actinic_2_16"] = (two_str[i]['Actinic_flux'] - sixteen_str[i]['Actinic_flux'])/sixteen_str[i]['Actinic_flux'] *100
	sixteen_str[i]["Actinic_4_16"] = (four_str[i]['Actinic_flux'] - sixteen_str[i]['Actinic_flux'])/sixteen_str[i]['Actinic_flux'] *100
	sixteen_str[i]["Actinic_8_16"] = (eight_str[i]['Actinic_flux'] - sixteen_str[i]['Actinic_flux'])/sixteen_str[i]['Actinic_flux'] *100

	sixteen_str[i]["Global_2_16"] = (two_str[i]['Global'] - sixteen_str[i]['Global'])/sixteen_str[i]['Global'] *100
	sixteen_str[i]["Global_4_16"] = (four_str[i]['Global'] - sixteen_str[i]['Global'])/sixteen_str[i]['Global'] *100
	sixteen_str[i]["Global_8_16"] = (eight_str[i]['Global'] - sixteen_str[i]['Global'])/sixteen_str[i]['Global'] *100

print(sixteen_str[0])
'''
for i in range(0,6):
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["Actinic_2_16"], color ='b', label = "2 streams")
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["Actinic_4_16"], color ='r', label = "4 streams")
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["Actinic_8_16"], color ='g', label = "8 streams")
	plt.xlabel(" Wavelength (nm)")
	plt.ylabel("'%' differences relative to the reference (16 str)")
	plt.legend()
	plt.grid()
	plt.title("Actinic flux for sza = "+str(sza_list[i])+" degrees")
	plt.show()

for i in range(0,6):
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["Global_2_16"], color ='b', label = "2 streams")
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["Global_4_16"], color ='r', label = "4 streams")
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["Global_8_16"], color ='g', label = "8 streams")
	plt.xlabel(" Wavelength (nm)")
	plt.ylabel("'%' differences relative to the reference (16 str)")
	plt.legend()
	plt.grid()
	plt.title("Global irradiance for sza = " +str(sza_list[i])+" degrees")
	plt.show()
'''

# extra stuff : find the % differences for the direct and diffused irradiance
for i in range(0,6):
	sixteen_str[i]["direct_2_16"] = (two_str[i]['Direct'] - sixteen_str[i]['Direct'])/sixteen_str[i]['Direct'] *100
	sixteen_str[i]["direct_4_16"] = (four_str[i]['Direct'] - sixteen_str[i]['Direct'])/sixteen_str[i]['Direct'] *100
	sixteen_str[i]["direct_8_16"] = (eight_str[i]['Direct'] - sixteen_str[i]['Direct'])/sixteen_str[i]['Direct'] *100

	sixteen_str[i]["diffused_2_16"] = (two_str[i]['Diffuse_Down'] - sixteen_str[i]['Diffuse_Down'])/sixteen_str[i]['Diffuse_Down'] *100
	sixteen_str[i]["diffused_4_16"] = (four_str[i]['Diffuse_Down'] - sixteen_str[i]['Diffuse_Down'])/sixteen_str[i]['Diffuse_Down'] *100
	sixteen_str[i]["diffused_8_16"] = (eight_str[i]['Diffuse_Down'] - sixteen_str[i]['Diffuse_Down'])/sixteen_str[i]['Diffuse_Down'] *100


for i in range(0,6):
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["direct_2_16"], color ='b', label = "2 streams")
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["direct_4_16"], color ='r', label = "4 streams")
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["direct_8_16"], color ='g', label = "8 streams")
	plt.xlabel(" Wavelength (nm)")
	plt.ylabel("'%' differences relative to the reference (16 str)")
	plt.legend()
	plt.grid()
	plt.title("direct irradiance for sza = "+str(sza_list[i])+" degrees")
	plt.show()

for i in range(0,6):
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["diffused_2_16"], color ='b', label = "2 streams")
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["diffused_4_16"], color ='r', label = "4 streams")
	plt.plot(sixteen_str[i]["Wavelength"], sixteen_str[i]["diffused_8_16"], color ='g', label = "8 streams")
	plt.xlabel(" Wavelength (nm)")
	plt.ylabel("'%' differences relative to the reference (16 str)")
	plt.legend()
	plt.grid()
	plt.title("diffused irradiance for sza = " +str(sza_list[i])+" degrees")
	plt.show()

# πινακάκια με αποκλίσεις : 3 στριμς * 4 μεγεθη * 6 ζενιθιες = 72 πινακακια... to be continued...
for i in range(0,6):
	ranges = [
    ("uvb", sixteen_str[i][sixteen_str[i]["Wavelength"] < 315]['diffused_2_16'].mean()),
    ("uva", sixteen_str[i][(sixteen_str[i]["Wavelength"] >= 315) & (sixteen_str[i]["Wavelength"] < 400)]['diffused_2_16'].mean()),
    ("vis", sixteen_str[i][(sixteen_str[i]["Wavelength"] >= 400) & (sixteen_str[i]["Wavelength"] < 800)]['diffused_2_16'].mean()),
    ("ir", sixteen_str[i][sixteen_str[i]["Wavelength"] >= 800]['diffused_2_16'].mean()),
	]
	result = pd.DataFrame(ranges)
	print(result)