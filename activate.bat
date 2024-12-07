@echo off
SET "VENV_DIR=%~dp0backend\venv"
SET "SCRIPTS_DIR=%VENV_DIR%\Scripts"
SET "REQ_FILE=%~dp0backend\requirements.txt"

echo Checking Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Create project structure
mkdir backend 2>nul
mkdir frontend 2>nul
mkdir vscode-extension 2>nul
mkdir docker 2>nul

REM Create requirements.txt if it doesn't exist
IF NOT EXIST "%REQ_FILE%" (
    echo Creating requirements.txt...
    (
        echo flask
        echo azure-ai-textanalytics
        echo python-dotenv
        echo flask-cors
    ) > "%REQ_FILE%"
)

REM Initialize backend and virtual environment
IF NOT EXIST "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment
        exit /b 1
    )
)

REM Activate virtual environment and install requirements
call "%SCRIPTS_DIR%\activate.bat"
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment
    exit /b 1
)

echo Installing/Upgrading pip...
python -m pip install --upgrade pip
pip install -r "%REQ_FILE%"

REM Initialize frontend
cd frontend
IF NOT EXIST "package.json" (
    call npm create vite@latest . -- --template react-ts
    call npm install
    call npm install tailwindcss postcss autoprefixer @uiw/react-codemirror
)

REM Initialize VS Code extension
cd ../vscode-extension
IF NOT EXIST "package.json" (
    call npm init -y
    call npm install @types/vscode vscode
)

cd ..
echo Project structure created successfully!

REM Start development servers
start cmd /k "cd frontend && npm run dev"
start cmd /k "cd backend && .\\venv\\Scripts\\activate && python server.py"

echo.
echo Virtual environment is active. To deactivate, type 'deactivate'
echo To start the development servers again, run this script
echo.
