import pandas as pd
import os
import glob

# Input and output folders
input_folder = "1011"
output_folder = "reshaped_data"
os.makedirs(output_folder, exist_ok=True)

# Get all CSV files in the input folder (case-insensitive)
csv_files = list({f for f in glob.iglob(os.path.join(input_folder, "*.csv"))} |
                 {f for f in glob.iglob(os.path.join(input_folder, "*.CSV"))})

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in: {input_folder}")

reshaped_files = []

# -------------------------
# Reshape all CSV files
# -------------------------
for file_path in csv_files:
    # Load CSV
    df = pd.read_csv(file_path, header=None)

    # Extract date and time
    dates = df.iloc[0, 1:]
    times = df.iloc[1, 1:]
    date_time = dates + " " + times

    # Extract wavelengths
    wavelengths = df.iloc[7:, 0]

    # Extract irradiance values
    irradiance_values = df.iloc[7:, 1:]

    # Create long-format dataframe
    long_df = pd.DataFrame({
        'DateTime': sum([[dt]*len(wavelengths) for dt in date_time], []),
        'Wavelength': list(wavelengths) * irradiance_values.shape[1],
        'Irradiance': irradiance_values.values.flatten('F')
    })

    # Drop rows where DateTime is not valid
    long_df = long_df[long_df['DateTime'].notna()]

    # Prepare output file path
    filename = os.path.basename(file_path)
    output_path = os.path.join(output_folder, filename)

    # Save reshaped CSV
    long_df.to_csv(output_path, index=False)
    reshaped_files.append(output_path)
    print(f"Reshaped and saved: {output_path}")

print("All CSV files have been reshaped and saved.")

# -------------------------
# Merge all reshaped CSVs
# -------------------------
df_list = []
for file_path in reshaped_files:
    temp = pd.read_csv(file_path)
    
    # Strip whitespace and parse DateTime safely
    temp['DateTime'] = pd.to_datetime(temp['DateTime'].astype(str).str.strip(), errors='coerce')
    
    # Drop any rows where DateTime could not be parsed
    temp = temp[temp['DateTime'].notna()]

    df_list.append(temp)

if df_list:
    # Concatenate all reshaped DataFrames
    merged_df = pd.concat(df_list, ignore_index=True)
    
    # Sort by DateTime and Wavelength
    merged_df = merged_df.sort_values(['DateTime', 'Wavelength']).reset_index(drop=True)

    # Save merged CSV in the current working directory
    merged_file_path = os.path.join(os.getcwd(), "merged_reshaped_data.csv")
    merged_df.to_csv(merged_file_path, index=False)
    print(f"Merged CSV saved as: {merged_file_path}")
else:
    print("No reshaped CSV files found to merge.")
