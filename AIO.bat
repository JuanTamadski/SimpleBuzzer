@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo =====================================
echo Setting up Multiplayer Buzzer System
echo =====================================

:: Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python not found. Downloading Python installer...

    set PYTHON_INSTALLER=python-3.12.2-amd64.exe
    set DOWNLOAD_URL=https://www.python.org/ftp/python/3.12.2/%PYTHON_INSTALLER%

    :: Download Python using PowerShell
    powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%PYTHON_INSTALLER%'"

    echo Installing Python silently...
    %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    echo Waiting for Python installation to complete...
    timeout /t 10 >nul

    :: Clean up installer
    del %PYTHON_INSTALLER%
)

:: Ensure Python is now available
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python installation failed or not added to PATH.
    pause
    exit /b
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Create requirements.txt (if not found)
IF NOT EXIST requirements.txt (
    echo Creating requirements.txt...
    echo pygame>=2.1.0> requirements.txt
    echo pyserial>=3.5>> requirements.txt
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Download buzzer.py from GitHub
echo Downloading buzzer.py from GitHub...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/JuanTamadski/SimpleBuzzer/main/buzzer.py' -OutFile 'buzzer.py'"

:: Download WAV files from GitHub
echo Downloading other files from GitHub...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/JuanTamadski/SimpleBuzzer/main/player1.wav' -OutFile 'player1.wav'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/JuanTamadski/SimpleBuzzer/main/player2.wav' -OutFile 'player2.wav'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/JuanTamadski/SimpleBuzzer/main/player3.wav' -OutFile 'player3.wav'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/JuanTamadski/SimpleBuzzer/main/player4.wav' -OutFile 'player4.wav'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/JuanTamadski/SimpleBuzzer/main/buzzer.wav' -OutFile 'buzzer.wav'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/JuanTamadski/SimpleBuzzer/main/runme.bat' -OutFile 'runme.bat'"

:: Run the main script
echo Starting the buzzer program...
python buzzer.py

:: Keep window open after exit
pause
