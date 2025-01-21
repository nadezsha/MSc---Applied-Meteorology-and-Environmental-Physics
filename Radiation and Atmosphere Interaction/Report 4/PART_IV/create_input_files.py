import os

# Define your input parameters
sza_values = [10, 40, 70, 85]
ssa_values = [round(x * 0.1 + 0.65, 2) for x in range(4)]  # 0.65, 0.75, 0.85, 0.95
angstrom_b_values = [round(x * 0.2, 1) for x in range(6)]  # 0.0, 0.2, 0.4, 0.6, 0.8, 1.0
spline_sets = [
    (300, 300),  # Set 1
    (900, 900)   # Set 2
]

# Template content for the configuration file
template_content = """
atmosphere_file ../data/atmmod/afglus.dat
source solar ../data/solar_flux/kurudz_1.0nm.dat
sza {sza}
wavelength 290.0 1100.0
spline {spline_x} {spline_y} 10
mol_abs_param sbdart
rte_solver sdisort
number_of_streams 4
aerosol_default
aerosol_angstrom 1.5 {angstrom_b}
aerosol_modify ssa scale {ssa}
aerosol_modify gg set 0.70
"""

# Directory to save the new files
output_dir = "generated_files"
os.makedirs(output_dir, exist_ok=True)

# Generate files
for idx, (spline_x, spline_y) in enumerate(spline_sets):
    for sza in sza_values:
        for ssa in ssa_values:
            for angstrom_b in angstrom_b_values:
                # Format the filename
                filename = f"run_set_{idx+1}_sza_{sza}_ssa_{ssa}_angstrom_{angstrom_b}.dat"
                file_path = os.path.join(output_dir, filename)
                
                # Format the template with the current values
                file_content = template_content.format(
                    sza=sza,
                    spline_x=spline_x,
                    spline_y=spline_y,
                    ssa=ssa,
                    angstrom_b=angstrom_b
                )
                
                # Write the generated content to the file
                with open(file_path, 'w') as f:
                    f.write(file_content)
                
                print(f"Generated: {file_path}")

print("All files have been generated!")
