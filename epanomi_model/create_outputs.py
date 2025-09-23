import os
import subprocess
from pathlib import Path
import shutil

# ===== SETTINGS =====
PROJECT_DIR_WIN = r"C:\MSc - Applied Meteorology and Environmental Physics\MSc Thesis\epanomi_model"

# Path to uvspec in WSL
UVSPEC_LINUX = "/home/nadezsha/libRadtran-2.0.6/bin/uvspec"

# OPTIONAL: libRadtran data directory in WSL 
UVSPEC_DATA_LINUX = "/home/nadezsha/libRadtran-2.0.6/data"

# ===== DERIVED PATHS =====
INPUT_DIR_WIN   = str(Path(PROJECT_DIR_WIN) / "inputs")
OUTPUT_DIR_WIN  = str(Path(PROJECT_DIR_WIN) / "outputs")

def win_to_wsl(p: str) -> str:
    """Convert C:\\path\\to\\file -> /mnt/c/path/to/file"""
    p = os.path.abspath(p)
    drive, rest = os.path.splitdrive(p)
    return f"/mnt/{drive.rstrip(':').lower()}{rest.replace('\\', '/')}"

def run_uvspec(input_file_win: str, output_file_win: str):
    """Run uvspec via WSL with quoting + stdout redirection to save output."""
    input_wsl  = win_to_wsl(input_file_win)
    output_wsl = win_to_wsl(output_file_win)

    # Build a single bash command; export UVSPEC_DATA if provided
    exports = f"export UVSPEC_DATA='{UVSPEC_DATA_LINUX}'; " if UVSPEC_DATA_LINUX else ""
    bash_cmd = f"{exports}'{UVSPEC_LINUX}' -i '{input_wsl}' > '{output_wsl}'"

    cmd = ["wsl", "bash", "-lc", bash_cmd]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

# ===== PRECHECKS =====
if shutil.which("wsl") is None:
    raise RuntimeError("WSL is not available on this system.")

# Ensure uvspec exists & is executable in WSL
if subprocess.run(["wsl", "test", "-x", UVSPEC_LINUX]).returncode != 0:
    raise FileNotFoundError(f"uvspec not found or not executable in WSL at: {UVSPEC_LINUX}")

# Create outputs dir (Windows + WSL views)
os.makedirs(OUTPUT_DIR_WIN, exist_ok=True)
subprocess.run(["wsl", "mkdir", "-p", win_to_wsl(OUTPUT_DIR_WIN)], check=True)

# ===== MAIN =====
inp_files = [f for f in os.listdir(INPUT_DIR_WIN) if f.lower().endswith(".inp")]
print(f"Found {len(inp_files)} input files in {INPUT_DIR_WIN}")

for filename in inp_files:
    input_file  = os.path.join(INPUT_DIR_WIN, filename)
    output_file = os.path.join(OUTPUT_DIR_WIN, filename[:-4] + ".out")
    run_uvspec(input_file, output_file)

print("\nAll simulations finished! Outputs in:")
print(OUTPUT_DIR_WIN)