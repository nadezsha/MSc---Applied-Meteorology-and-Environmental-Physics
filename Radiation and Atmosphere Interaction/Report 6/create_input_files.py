# range for zout and the sza values
zout_values = range(0, 9)  # zout from 0 to 8 (inclusive) in steps of 1
sza_values = [20, 70]  # sza values of 20 and 70

# template of the file content with placeholders for zout and sza
template = '''atmosphere_file ../data/atmmod/afglus.dat
source solar ../data/solar_flux/kurudz_1.0nm.dat
sza {sza}
wavelength 290.0 1100.0
spline 300 1100 10
mol_abs_param sbdart
rte_solver sdisort
number_of_streams 4
aerosol_default
aerosol_angstrom 1.5 0.1
aerosol_modify ssa scale 0.95
aerosol_modify gg set 0.70
wc_file 1D ./WC6_part2.DAT
wc_modify tau set 2.0
zout {zout}
'''

# Iterate over the combinations of zout and sza
for zout in zout_values:
    for sza in sza_values:
        # Create the filename based on zout and sza
        filename = f"input_zout{zout}_sza{sza}_part2.inp"
        
        # Format the content with the current zout and sza values
        file_content = template.format(zout=zout, sza=sza)
        
        # Write the content to a file
        with open(filename, 'w') as file:
            file.write(file_content)
        
        print(f"Created file: {filename}")
