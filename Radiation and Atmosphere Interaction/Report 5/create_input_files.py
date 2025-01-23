import os

# Define your input parameters
sza_values = [20, 50, 80]
tau_values = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 10.0, 15.0, 20.0]

# Template content for the configuration file
template_content = """
atmosphere_file ../data/atmmod/afglus.dat
source solar ../data/solar_flux/kurudz_1.0nm.dat
sza {sza_value}
wavelength 290.0 1100.0
spline 300 1100 10
mol_abs_param sbdart
rte_solver sdisort
number_of_streams 4 
aerosol_default
aerosol_angstrom 1.5 0.1
aerosol_modify ssa scale 0.95
aerosol_modify gg set 0.70
wc_file 1D C:/cygwin64/home/stavros/libRadtran-2.0.1/ergasia5/WC5.DAT
wc_modify tau set {tau_value}
"""

# Directory to save the new files
output_dir = "libRadtran_inputs"
os.makedirs(output_dir, exist_ok=True)

# Loop over all combinations of sza and tau
for sza in sza_values:
    for tau in tau_values:
        # Create file name based on sza and tau
        file_name = f"config_sza{int(sza)}_tau{int(tau*10)}.inp"  # Multiplying tau by 10 for simplicity in the file name
        file_path = os.path.join(output_dir, file_name)
        
        # Substitute the sza and tau values into the template content
        file_content = template_content.format(sza_value=sza, tau_value=tau)
        
        # Write the generated content to the file
        with open(file_path, 'w') as file:
            file.write(file_content)

        print(f"Generated file: {file_path}")
