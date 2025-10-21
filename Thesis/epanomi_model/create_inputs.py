import os
import numpy as np

# Path to your template file
template_file = r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\epanomi_model\typical_profile.inp"   

# Folder to save new inputs
output_dir = r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\epanomi_model\inputs"
os.makedirs(output_dir, exist_ok=True)

# Read template content
with open(template_file, "r") as f:
    template_content = f.readlines()

# Generate sza values from 15.0 to 90.0 with step 0.5
sza_values = np.arange(15.0, 90.0 + 0.5, 0.5)

for sza in sza_values:
    # Modify template content
    new_content = []
    for line in template_content:
        if line.strip().startswith("sza "):
            new_content.append(f"sza {sza:.1f}\n")
        else:
            new_content.append(line)

    # Save new file with sza in filename
    output_file = os.path.join(output_dir, f"typical_profile_sza_{sza:.1f}.inp")
    with open(output_file, "w") as f:
        f.writelines(new_content)

print(f"Created {len(sza_values)} input files in '{output_dir}' folder.")
