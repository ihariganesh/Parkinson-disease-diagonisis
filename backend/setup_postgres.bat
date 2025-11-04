@echo off
echo Setting up PostgreSQL database for Parkinson's Detection App...

:: Set PostgreSQL bin path
set PGBIN="C:\Program Files\PostgreSQL\17\bin"

echo.
echo 1. Creating database and user...
echo Please enter the postgres password when prompted.
echo.

:: Connect as postgres user and run setup commands
%PGBIN%\psql.exe -U postgres -h localhost -c "DROP DATABASE IF EXISTS parkinson_db;"
%PGBIN%\psql.exe -U postgres -h localhost -c "DROP DATABASE IF EXISTS parkinson_test_db;"
%PGBIN%\psql.exe -U postgres -h localhost -c "DROP USER IF EXISTS parkinson_user;"

%PGBIN%\psql.exe -U postgres -h localhost -c "CREATE DATABASE parkinson_db;"
%PGBIN%\psql.exe -U postgres -h localhost -c "CREATE DATABASE parkinson_test_db;"
%PGBIN%\psql.exe -U postgres -h localhost -c "CREATE USER parkinson_user WITH PASSWORD 'parkinson123';"
%PGBIN%\psql.exe -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE parkinson_db TO parkinson_user;"
%PGBIN%\psql.exe -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE parkinson_test_db TO parkinson_user;"

echo.
echo 2. Setting up schema permissions...
%PGBIN%\psql.exe -U postgres -h localhost -d parkinson_db -c "GRANT ALL ON SCHEMA public TO parkinson_user;"
%PGBIN%\psql.exe -U postgres -h localhost -d parkinson_test_db -c "GRANT ALL ON SCHEMA public TO parkinson_user;"

echo.
echo PostgreSQL setup completed!
echo Database: parkinson_db
echo User: parkinson_user
echo Password: parkinson123
pause