@echo off
:: Set the path to Libradtran executable if it's not in the system PATH
set LIBRADTRAN_PATH=C:\path\to\libradtran\bin

:: Set the directory containing your input files (generated_files from the Python script)
set INPUT_DIR=generated_files

:: Change to the directory containing the input files (optional, for convenience)
cd %INPUT_DIR%

:: Loop through all the .dat files and run uvspec for each one
for %%f in (*.dat) do (
    echo Running uvspec for file %%f...
    "%LIBRADTRAN_PATH%\uvspec" < %%f > %%~nf_output.txt
)

echo All simulations are complete!
pause
