@echo off
cd /d "%~dp0"

set "PYTHON_EXE="
set "PY_PROBE=%TEMP%\local_dictation_python.txt"
py -3.11 -c "import sys; print(sys.executable)" > "%PY_PROBE%" 2>nul
if %ERRORLEVEL%==0 set /p PYTHON_EXE=<"%PY_PROBE%"

if not defined PYTHON_EXE if exist "C:\Users\abirh\AppData\Roaming\uv\python\cpython-3.11.13-windows-x86_64-none\python.exe" (
  set "PYTHON_EXE=C:\Users\abirh\AppData\Roaming\uv\python\cpython-3.11.13-windows-x86_64-none\python.exe"
)

if not defined PYTHON_EXE (
  echo Python 3.11 was not found. Install Python 3.11 or update install.bat with the correct path.
  exit /b 1
)

if not exist .venv (
  "%PYTHON_EXE%" -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
