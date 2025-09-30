import os
import pandas as pd

INPUT_FOLDER = "raw"
OUTPUT_FOLDER = "reshaped_data"
COMBINED_NAME = "all_reshaped_combined.csv"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def read_any(filepath: str) -> pd.DataFrame:
    name = os.path.basename(filepath).lower()
    if name.endswith(".xlsx"):
        return pd.read_excel(filepath, header=None)
    try:
        return pd.read_csv(filepath, header=None, encoding="utf-8-sig")
    except Exception:
        return pd.read_csv(filepath, header=None, engine="python")

def find_row_index(df: pd.DataFrame, key: str) -> int:
    key = key.lower()
    for i, v in enumerate(df.iloc[:, 0].astype(str).str.strip().str.lower()):
        if v.startswith(key):
            return i
    raise ValueError(f"Could not find a row starting with '{key}'")

def reshape_one(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(axis=1, how="all")

    r_date = find_row_index(df, "date")
    r_time = find_row_index(df, "time")
    r_expo = find_row_index(df, "exposure")
    r_wave = find_row_index(df, "wavelength")

    cols = df.columns[1:]

    dates = df.loc[r_date, cols].astype(str).replace(["nan", "NaT"], pd.NA).ffill(axis=0)
    times = df.loc[r_time, cols].astype(str).replace(["nan", "NaT"], pd.NA)
    exposure = pd.to_numeric(df.loc[r_expo, cols], errors="coerce")

    dt = pd.to_datetime(dates.str.strip() + " " + times.str.strip(), errors="coerce")

    data_block = df.iloc[r_wave + 1 :, :]
    wl = pd.to_numeric(data_block.iloc[:, 0], errors="coerce")
    valid = wl.notna()
    wl = wl[valid].astype(int)

    irr = data_block.loc[valid, cols].apply(pd.to_numeric, errors="coerce")

    # ---- build in one shot (no fragmentation) ----
    # irradiance is rows=wavelengths, cols=timestamps -> transpose
    irr_matrix = irr.T.copy()
    irr_matrix.columns = wl.astype(str).tolist()
    base = pd.DataFrame({"Datetime": dt, "Exposure (msec)": exposure}).reset_index(drop=True)
    out = pd.concat([base, irr_matrix.reset_index(drop=True)], axis=1)

    # clean & order columns
    out = out.dropna(subset=["Datetime"]).reset_index(drop=True)
    wl_cols = sorted([c for c in out.columns if c not in ("Datetime", "Exposure (msec)")], key=lambda x: int(x))
    out = out[["Datetime", "Exposure (msec)"] + wl_cols]
    return out

def main():
    all_frames = []

    for filename in os.listdir(INPUT_FOLDER):
        if not filename.lower().endswith((".csv", ".xlsx")):
            continue
        path = os.path.join(INPUT_FOLDER, filename)
        try:
            df = read_any(path)
            reshaped = reshape_one(df)
        except Exception as e:
            print(f"[SKIP] {filename}: {e}")
            continue

        # save per-file
        outname = os.path.splitext(filename)[0] + "_reshaped.csv"
        outpath = os.path.join(OUTPUT_FOLDER, outname)
        reshaped.to_csv(outpath, index=False)
        print(f"Saved {outpath}")

        reshaped["SourceFile"] = filename  
        all_frames.append(reshaped)

    # save combined (chronological, outer-align columns just in case)
    if all_frames:
        combined = pd.concat(all_frames, axis=0, ignore_index=True, sort=False)
        combined = combined.sort_values("Datetime").reset_index(drop=True)
        # order columns: Datetime, Exposure, SourceFile (if present), then wavelengths asc
        fixed = ["Datetime", "Exposure (msec)"]
        if "SourceFile" in combined.columns:
            fixed.append("SourceFile")
        wl_cols = sorted([c for c in combined.columns if c not in fixed], key=lambda x: int(x))
        combined = combined[fixed + wl_cols]

        combined_path = os.path.join(OUTPUT_FOLDER, COMBINED_NAME)
        combined.to_csv(combined_path, index=False)
        print(f"Saved combined file: {combined_path}")
    else:
        print("No files processed.")

if __name__ == "__main__":
    main()
