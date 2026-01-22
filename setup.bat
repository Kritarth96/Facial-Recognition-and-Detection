@echo off
echo 🚀 Setting up Face Recognition System...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo 📦 Installing Python dependencies...

:: Install required Python packages
pip install -r requirements.txt

echo 📁 Creating required directories...

:: Create faces directory if it doesn't exist
if not exist "static\faces" mkdir "static\faces"

echo 🔧 Setting up TypeScript (optional)...

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo 📦 Installing Node.js dependencies...
    npm install
    echo 🔨 Building TypeScript...
    npm run build
) else (
    echo ⚠️ Node.js not found. Using pre-compiled JavaScript files.
)

echo 🗄️ Setting up database...
echo Please ensure MySQL is running and create the database manually:
echo 1. Connect to MySQL: mysql -u root -p
echo 2. Create database: CREATE DATABASE capstone;
echo 3. Create table: USE capstone; CREATE TABLE logins (loginids VARCHAR(50) PRIMARY KEY, passwords VARCHAR(255));
echo 4. Insert user: INSERT INTO logins VALUES ('admin', '$2b$12$YOUR_HASHED_PASSWORD');

echo.
echo ✅ Setup complete!
echo.
echo 🌐 To start the server:
echo    python app.py
echo.
echo 🎯 Access the application:
echo    Modern Dashboard: http://localhost:8080/dashboard
echo    Classic Interface: http://localhost:8080/
echo.
echo 📋 Default login: admin / (set your password)

pause
