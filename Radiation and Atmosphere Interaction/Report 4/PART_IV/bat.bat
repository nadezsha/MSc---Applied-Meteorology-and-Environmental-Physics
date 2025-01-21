@echo off
:: Loop through all .inp files in the current directory and run uvspec for each one
for %%f in (*.inp) do (
    echo Running uvspec for file %%f...
    uvspec < "%%f" > "%%~nf.out"
)

echo All simulations are complete!
pause
