import pandas as pd
import glob
import os

# Get the folder where the script is saved
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the "2024" subfolder
data_dir = os.path.join(script_dir, "2024")

# Match both .csv and .CSV, but ensure uniqueness
all_files = list({f for f in glob.iglob(os.path.join(data_dir, "*.csv"))} |
                 {f for f in glob.iglob(os.path.join(data_dir, "*.CSV"))})

if not all_files:
    raise FileNotFoundError("No CSV files found in: " + data_dir)

df_list = []
for file in all_files:
    temp = pd.read_csv(file)
    temp['Datetime_UTC'] = pd.to_datetime(
        temp['Datetime_UTC'], errors='coerce', infer_datetime_format=True
    )

    if temp['Datetime_UTC'].isna().any():
        print(f"⚠️ Warning: {file} contains unparsed datetime values.")

    df_list.append(temp)

# Merge and sort
df = pd.concat(df_list, ignore_index=True)
df = df.sort_values('Datetime_UTC').reset_index(drop=True)

# Save in the same folder as the script
output_file = os.path.join(script_dir, "merged_timeseries.csv")
df.to_csv(output_file, index=False)

print(f"Merged CSV saved as: {output_file}")