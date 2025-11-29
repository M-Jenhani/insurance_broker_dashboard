@echo off
REM Quick setup script for Windows

echo ========================================
echo  INSURANCE BROKER DASHBOARD - SETUP
echo ========================================
echo.

echo [1/5] Creating directories...
if not exist data mkdir data
if not exist models mkdir models
if not exist exports mkdir exports
echo Done!

echo.
echo [2/5] Installing Python dependencies...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Done!

echo.
echo [3/5] Generating synthetic data...
python src/generate_synthetic_data.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to generate data
    pause
    exit /b 1
)
echo Done!

echo.
echo [4/5] Processing and cleaning data...
python src/data_processor.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to process data
    pause
    exit /b 1
)
echo Done!

echo.
echo [5/5] Training ML models...
python src/ml_models.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to train models
    pause
    exit /b 1
)
echo Done!

echo.
echo ========================================
echo  SETUP COMPLETE!
echo ========================================
echo.
echo To launch the dashboard, run:
echo   streamlit run dashboard.py
echo.
echo Or press any key to launch now...
pause > nul

streamlit run dashboard.py
