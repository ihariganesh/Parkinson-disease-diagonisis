@echo off
echo Resetting PostgreSQL for Parkinson's Detection App...
echo.

:: Stop PostgreSQL service
echo Stopping PostgreSQL service...
net stop postgresql-x64-17

:: Start PostgreSQL service
echo Starting PostgreSQL service...
net start postgresql-x64-17

echo.
echo PostgreSQL service restarted.
echo.
echo To reset PostgreSQL password:
echo 1. Open pgAdmin (search for pgAdmin in Start menu)
echo 2. Connect to the PostgreSQL server (localhost)
echo 3. Right-click on "Login/Group Roles" -> Create -> Login/Group Role
echo 4. Create a new user: 
echo    - Name: parkinson_admin
echo    - Password: parkinson2024
echo    - Privileges: Can login? Yes, Superuser? Yes
echo.
echo Or run this command as Administrator in Command Prompt:
echo.
echo psql -U postgres -c "CREATE USER parkinson_admin WITH PASSWORD 'parkinson2024' SUPERUSER;"
echo psql -U postgres -c "CREATE DATABASE parkinson_db OWNER parkinson_admin;"
echo psql -U postgres -c "CREATE DATABASE parkinson_test_db OWNER parkinson_admin;"
echo.
pause