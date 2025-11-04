# Database setup script for Parkinson's Detection App

# Create database and user
CREATE DATABASE parkinson_db;
CREATE DATABASE parkinson_test_db;

# Create user (replace 'your_password' with a secure password)
CREATE USER parkinson_user WITH PASSWORD 'parkinson123';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE parkinson_db TO parkinson_user;
GRANT ALL PRIVILEGES ON DATABASE parkinson_test_db TO parkinson_user;

# Connect to the database
\c parkinson_db;

# Grant schema privileges
GRANT ALL ON SCHEMA public TO parkinson_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO parkinson_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO parkinson_user;

# For test database
\c parkinson_test_db;
GRANT ALL ON SCHEMA public TO parkinson_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO parkinson_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO parkinson_user;