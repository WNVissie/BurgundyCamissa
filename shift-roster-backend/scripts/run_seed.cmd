@echo off
setlocal
set CSV_DIR=%~1
if "%CSV_DIR%"=="" (
  set CSV_DIR=%~dp0..\Re-Employee Shft Roster
)
pushd "%~dp0.."
call venv\Scripts\python.exe -c "import seed_from_csv; seed_from_csv.main()"
popd
endlocal
