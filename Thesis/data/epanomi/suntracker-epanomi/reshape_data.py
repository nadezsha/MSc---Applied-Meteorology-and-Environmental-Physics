import pandas as pd
import glob
import os

# === Locations ===
script_dir = os.path.dirname(os.path.abspath(__file__))

# year subfolders to include 
year_folders = {"2000", "2004", "2024", "2025"}

# === Collect all CSVs from the year subfolders (recursively) ===
pattern_lower = os.path.join(script_dir, "**", "*.csv")
pattern_upper = os.path.join(script_dir, "**", "*.CSV")

all_candidates = list(glob.iglob(pattern_lower, recursive=True)) + \
                 list(glob.iglob(pattern_upper, recursive=True))

# Keep only files that are actually inside the specified year folders
def is_in_year_folder(path: str) -> bool:
    parent = os.path.basename(os.path.dirname(path))
    return parent in year_folders

all_files = sorted({f for f in all_candidates if is_in_year_folder(f)})

if not all_files:
    raise FileNotFoundError(
        "No CSV files found under the year folders: "
        + ", ".join(sorted(year_folders))
        + f" inside {script_dir}"
    )

print(f"Found {len(all_files)} CSV files to merge.")

# === read, parse datetime, and collect ===
df_list = []
bad_files = []

for file in all_files:
    try:
        temp = pd.read_csv(file)
    except Exception as e:
        print(f"Error reading {file}: {e}")
        bad_files.append(file)
        continue

    if "Datetime_UTC" not in temp.columns:
        print(f" Skipping (missing 'Datetime_UTC' column): {file}")
        bad_files.append(file)
        continue

    # Parse Datetime_UTC 
    temp["Datetime_UTC"] = pd.to_datetime(temp["Datetime_UTC"], errors="coerce")

    if temp["Datetime_UTC"].isna().any():
        print(f"Warning: {file} contains unparsed datetime values (NaT).")

    df_list.append(temp)

if not df_list:
    raise RuntimeError("No valid CSVs were parsed successfully.")

# === merge and sort ===
df = pd.concat(df_list, ignore_index=True)

# sort by datetime if present
df = df.sort_values("Datetime_UTC").reset_index(drop=True)

# === save beside the script ===
output_file = os.path.join(script_dir, "merged_timeseries_epanomi.csv")
df.to_csv(output_file, index=False)

print(f"Merged CSV saved as: {output_file}")
if bad_files:
    print(f"{len(bad_files)} files were skipped due to issues.")